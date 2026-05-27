# Módulo Sanitization Gateway V5
# Servicio que intercepta payloads hacia LLMs externos y los sanitiza

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

variable "docker_image" {
  description = "Docker image for sanitization gateway"
  type        = string
}

variable "cpu" {
  type    = number
  default = 512
}

variable "memory" {
  type    = number
  default = 1024
}

variable "desired_count" {
  type    = number
  default = 2
}

# ============================================================
# ECS Cluster
# ============================================================

resource "aws_ecs_cluster" "sanitizer" {
  name = "${var.project_name}-${var.environment}-sanitizer"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# ============================================================
# Task Definition
# ============================================================

resource "aws_ecs_task_definition" "sanitizer" {
  family                   = "${var.project_name}-${var.environment}-sanitizer"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "sanitizer"
    image = var.docker_image
    
    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]
    
    environment = [
      { name = "ENVIRONMENT", value = var.environment },
      { name = "LOG_LEVEL", value = "INFO" },
      { name = "PRESIDIO_ANALYZER_URL", value = "http://localhost:5001" },
      { name = "MAX_PAYLOAD_SIZE_MB", value = "10" },
    ]
    
    secrets = [
      {
        name      = "SANITIZATION_SIGNING_KEY"
        valueFrom = aws_secretsmanager_secret.signing_key.arn
      }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.sanitizer.name
        "awslogs-region"        = data.aws_region.current.name
        "awslogs-stream-prefix" = "sanitizer"
      }
    }
    
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8080/healthz || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
    
    essential = true
  }])

  tags = {
    Environment = var.environment
  }
}

# ============================================================
# ECS Service
# ============================================================

resource "aws_ecs_service" "sanitizer" {
  name            = "${var.project_name}-${var.environment}-sanitizer"
  cluster         = aws_ecs_cluster.sanitizer.id
  task_definition = aws_ecs_task_definition.sanitizer.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.sanitizer.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.sanitizer.arn
    container_name   = "sanitizer"
    container_port   = 8080
  }

  tags = {
    Environment = var.environment
  }
}

# ============================================================
# Security Group
# ============================================================

resource "aws_security_group" "sanitizer" {
  name_prefix = "${var.project_name}-${var.environment}-sanitizer-"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
    description = "Allow from VPC"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS to LLM providers"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-sanitizer"
    Environment = var.environment
  }
}

# ============================================================
# ALB (interno)
# ============================================================

resource "aws_lb" "sanitizer" {
  name               = "${var.project_name}-${var.environment}-sanitizer"
  internal           = true
  load_balancer_type = "application"
  security_groups    = [aws_security_group.sanitizer.id]
  subnets            = var.private_subnet_ids

  tags = {
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "sanitizer" {
  name        = "${var.project_name}-${var.environment}-sanitizer"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/healthz"
    port                = "traffic-port"
    timeout             = 5
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "sanitizer" {
  load_balancer_arn = aws_lb.sanitizer.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.sanitizer.arn
  }
}

# ============================================================
# IAM Roles
# ============================================================

resource "aws_iam_role" "ecs_execution" {
  name = "${var.project_name}-${var.environment}-sanitizer-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-${var.environment}-sanitizer-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# ============================================================
# Signing Key (para firmar reports)
# ============================================================

resource "random_password" "signing_key" {
  length  = 64
  special = false
}

resource "aws_secretsmanager_secret" "signing_key" {
  name        = "${var.project_name}/${var.environment}/sanitizer/signing-key"
  description = "HMAC signing key for sanitization reports"
}

resource "aws_secretsmanager_secret_version" "signing_key" {
  secret_id     = aws_secretsmanager_secret.signing_key.id
  secret_string = random_password.signing_key.result
}

# ============================================================
# CloudWatch Logs
# ============================================================

resource "aws_cloudwatch_log_group" "sanitizer" {
  name              = "/ecs/${var.project_name}-${var.environment}-sanitizer"
  retention_in_days = 90

  tags = {
    Environment = var.environment
  }
}

# ============================================================
# CloudWatch Alarms
# ============================================================

resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.project_name}-${var.environment}-sanitizer-high-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Sanitizer returning too many 5xx errors"

  dimensions = {
    TargetGroup  = aws_lb_target_group.sanitizer.arn_suffix
    LoadBalancer = aws_lb.sanitizer.arn_suffix
  }
}

data "aws_region" "current" {}

# ============================================================
# Outputs
# ============================================================

output "service_endpoint" {
  description = "Internal endpoint for the sanitizer service"
  value       = "http://${aws_lb.sanitizer.dns_name}"
}

output "signing_key_secret_arn" {
  value = aws_secretsmanager_secret.signing_key.arn
}

output "cluster_name" {
  value = aws_ecs_cluster.sanitizer.name
}
