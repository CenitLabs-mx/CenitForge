# Sandbox Dockerfile para ejecución agéntica
# Implementa: egress filtering, isolation, resource limits
#
# Uso:
#   docker build -f sandbox.Dockerfile -t agent-sandbox:latest .
#   docker run --rm \
#     --network sandbox-net \
#     --memory=4g \
#     --cpus=2 \
#     --pids-limit=512 \
#     --read-only \
#     --tmpfs /tmp:rw,noexec,nosuid,size=1g \
#     agent-sandbox:latest

FROM ubuntu:22.04 AS base

# Metadata
LABEL maintainer="platform@example.com"
LABEL description="Isolated sandbox for AI agent code execution"
LABEL version="1.0"

# No interactive
ENV DEBIAN_FRONTEND=noninteractive

# ============================================================
# System dependencies
# ============================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    build-essential \
    python3.12 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    postgresql-client \
    redis-tools \
    jq \
    iproute2 \
    iptables \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Non-root user
# ============================================================

RUN useradd -m -s /bin/bash -u 1000 agent && \
    echo "agent ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ============================================================
# Working directory
# ============================================================

WORKDIR /workspace
RUN chown -R agent:agent /workspace

# ============================================================
# Egress filtering script
# ============================================================

COPY egress-filter.sh /usr/local/bin/egress-filter
RUN chmod +x /usr/local/bin/egress-filter

# ============================================================
# Allowlist de dominios (configurable vía env)
# ============================================================

ENV EGRESS_ALLOWLIST="registry.npmjs.org,pypi.org,files.pythonhosted.org,github.com,api.github.com,raw.githubusercontent.com,docs.github.com,developer.mozilla.org,stackoverflow.com"

# Bloquear todo por defecto (metadata endpoint, IPs privadas)
ENV EGRESS_DENY_METADATA="true"
ENV EGRESS_DENY_PRIVATE="true"

# ============================================================
# Resource limits enforcement wrapper
# ============================================================

COPY run-with-limits.sh /usr/local/bin/run-with-limits
RUN chmod +x /usr/local/bin/run-with-limits

# ============================================================
# Health check
# ============================================================

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD test -f /tmp/healthy || exit 1

# ============================================================
# Entrypoint
# ============================================================

USER agent

COPY entrypoint.sh /usr/local/bin/entrypoint
RUN sudo chmod +x /usr/local/bin/entrypoint

ENTRYPOINT ["/usr/local/bin/entrypoint"]
CMD ["/bin/bash"]
