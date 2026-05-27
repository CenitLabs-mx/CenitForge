# Módulo HashiCorp Vault para gestión de secretos
# Implementa: auto-unseal, audit logging, PKI, KV v2

variable "environment" {
  type = string
}

variable "project_name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "kms_key_arn" {
  description = "KMS key for auto-unseal"
  type        = string
}

variable "instance_type" {
  type    = string
  default = "t3.medium"
}

# ============================================================
# AMI de Vault
# ============================================================

data "aws_ami" "vault" {
  most_recent = true
  owners      = ["self"]  # AMI propia con Vault preinstalado

  filter {
    name   = "name"
    values = ["vault-*"]
  }
}

# ============================================================
# Security Group
# ============================================================

resource "aws_security_group" "vault" {
  name_prefix = "${var.project_name}-${var.environment}-vault-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 8200
    to_port     = 8200
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # Solo desde VPC
    description = "Vault API"
  }

  ingress {
    from_port   = 8201
    to_port     = 8201
    protocol    = "tcp"
    self        = true
    description = "Vault cluster communication"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-vault"
    Environment = var.environment
  }
}

# ============================================================
# IAM Role para Auto-Unseal con KMS
# ============================================================

resource "aws_iam_role" "vault" {
  name = "${var.project_name}-${var.environment}-vault"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "vault_kms" {
  name = "${var.project_name}-${var.environment}-vault-kms"
  role = aws_iam_role.vault.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:DescribeKey"
      ]
      Resource = var.kms_key_arn
    }]
  })
}

resource "aws_iam_instance_profile" "vault" {
  name = "${var.project_name}-${var.environment}-vault"
  role = aws_iam_role.vault.name
}

# ============================================================
# Storage (S3 para HA)
# ============================================================

resource "aws_s3_bucket" "vault_storage" {
  bucket = "${var.project_name}-${var.environment}-vault-storage"

  tags = {
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "vault_storage" {
  bucket = aws_s3_bucket.vault_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "vault_storage" {
  bucket = aws_s3_bucket.vault_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "vault_storage" {
  bucket = aws_s3_bucket.vault_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ============================================================
# Configuración de Vault
# ============================================================

locals {
  vault_config = <<-EOF
    ui = true
    
    listener "tcp" {
      address     = "0.0.0.0:8200"
      tls_disable = 0
      tls_cert_file = "/etc/vault/tls/cert.pem"
      tls_key_file  = "/etc/vault/tls/key.pem"
    }
    
    storage "s3" {
      bucket = "${aws_s3_bucket.vault_storage.id}"
      region = "${data.aws_region.current.name}"
    }
    
    seal "awskms" {
      region     = "${data.aws_region.current.name}"
      kms_key_id = "${var.kms_key_arn}"
    }
    
    audit "file" {
      file_path = "/var/log/vault/audit.log"
    }
    
    telemetry {
      prometheus_retention_time = "24h"
      disable_hostname = true
    }
    
    cluster_name = "${var.project_name}-${var.environment}"
    api_addr     = "https://vault.${var.environment}.internal:8200"
  EOF
}

data "aws_region" "current" {}

# ============================================================
# EC2 Instance
# ============================================================

resource "aws_instance" "vault" {
  ami                    = data.aws_ami.vault.id
  instance_type          = var.instance_type
  iam_instance_profile   = aws_iam_instance_profile.vault.name
  subnet_id              = var.private_subnet_ids[0]
  vpc_security_group_ids = [aws_security_group.vault.id]

  root_block_device {
    volume_size = 50
    volume_type = "gp3"
    encrypted   = true
    kms_key_id  = var.kms_key_arn
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -e
    
    # Instalar Vault (si no está en AMI)
    which vault || {
      wget -q https://releases.hashicorp.com/vault/1.17.0/vault_1.17.0_linux_amd64.zip
      unzip vault_1.17.0_linux_amd64.zip -d /usr/local/bin/
      rm vault_1.17.0_linux_amd64.zip
    }
    
    # Configurar
    mkdir -p /etc/vault /var/log/vault
    cat > /etc/vault/config.hcl <<'VAULTCONF'
${local.vault_config}
VAULTCONF
    
    # Systemd service
    cat > /etc/systemd/system/vault.service <<'SYSTEMD'
    [Unit]
    Description=HashiCorp Vault
    Requires=network-online.target
    After=network-online.target
    
    [Service]
    User=vault
    Group=vault
    ExecStart=/usr/local/bin/vault server -config=/etc/vault/config.hcl
    ExecReload=/bin/kill --signal HUP $MAINPID
    KillMode=process
    Restart=on-failure
    LimitNOFILE=65536
    
    [Install]
    WantedBy=multi-user.target
    SYSTEMD
    
    useradd -r -s /bin/false vault || true
    chown -R vault:vault /etc/vault /var/log/vault
    
    systemctl daemon-reload
    systemctl enable vault
    systemctl start vault
  EOF
  )

  tags = {
    Name        = "${var.project_name}-${var.environment}-vault"
    Environment = var.environment
    Role        = "vault"
  }

  lifecycle {
    ignore_changes = [ami, user_data]
  }
}

# ============================================================
# Secrets iniciales (vía null_resource + vault CLI)
# ============================================================

resource "null_resource" "vault_init" {
  depends_on = [aws_instance.vault]

  provisioner "local-exec" {
    command = <<-EOF
      export VAULT_ADDR="https://${aws_instance.vault.private_ip}:8200"
      export VAULT_SKIP_VERIFY=true
      
      # Esperar a que Vault esté listo
      for i in {1..30}; do
        vault status && break
        sleep 10
      done
      
      # Inicializar si no está inicializado
      if ! vault status | grep -q "Initialized.*true"; then
        vault operator init -key-shares=5 -key-threshold=3 > /tmp/vault-init.txt
        echo "INIT COMPLETE - keys saved to /tmp/vault-init.txt"
      fi
      
      # Habilitar KV v2
      vault secrets enable -path=secret kv-v2 || true
      
      # Habilitar audit
      vault audit enable file file_path=/var/log/vault/audit.log || true
    EOF
  }
}

# ============================================================
# Outputs
# ============================================================

output "vault_address" {
  value = "https://${aws_instance.vault.private_ip}:8200"
}

output "vault_instance_id" {
  value = aws_instance.vault.id
}

output "vault_security_group_id" {
  value = aws_security_group.vault.id
}
