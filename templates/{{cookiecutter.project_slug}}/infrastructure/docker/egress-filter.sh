#!/bin/bash
# Egress filter para sandbox agéntico
# Bloquea:
# - Metadata endpoints (169.254.169.254)
# - IPs privadas (10.x, 172.16-31.x, 192.168.x)
# - Dominios no en allowlist
#
# Requiere: iptables, iproute2

set -euo pipefail

# ============================================================
# Configuración
# ============================================================

ALLOWLIST_CSV="${EGRESS_ALLOWLIST:-}"
DENY_METADATA="${EGRESS_DENY_METADATA:-true}"
DENY_PRIVATE="${EGRESS_DENY_PRIVATE:-true}"
AUDIT_LOG="${AUDIT_LOG:-/var/log/egress-audit.log}"

# Convertir allowlist a array
IFS=',' read -ra ALLOWLIST <<< "$ALLOWLIST_CSV"

# ============================================================
# Logging function
# ============================================================

log_egress() {
    local status="$1"
    local dest="$2"
    echo "$(date -Iseconds) | $status | $dest | PID=$$ | USER=$(whoami)" >> "$AUDIT_LOG" 2>/dev/null || true
}

# ============================================================
# DNS resolution con filtrado
# ============================================================

resolve_and_validate() {
    local domain="$1"
    
    # Verificar si está en allowlist
    local allowed=false
    for allowed_domain in "${ALLOWLIST[@]}"; do
        if [[ "$domain" == "$allowed_domain" ]] || [[ "$domain" == *".$allowed_domain" ]]; then
            allowed=true
            break
        fi
    done
    
    if [[ "$allowed" == "false" ]]; then
        log_egress "BLOCKED_DOMAIN" "$domain"
        echo "ERROR: Domain '$domain' not in allowlist" >&2
        return 1
    fi
    
    # Resolver DNS
    local ip
    ip=$(getent ahosts "$domain" 2>/dev/null | head -1 | awk '{print $1}')
    
    if [[ -z "$ip" ]]; then
        log_egress "DNS_FAILED" "$domain"
        return 1
    fi
    
    # Validar que no sea IP privada
    if [[ "$DENY_PRIVATE" == "true" ]]; then
        if is_private_ip "$ip"; then
            log_egress "BLOCKED_PRIVATE_IP" "$domain -> $ip"
            echo "ERROR: Domain resolves to private IP: $ip" >&2
            return 1
        fi
    fi
    
    # Validar que no sea metadata endpoint
    if [[ "$DENY_METADATA" == "true" ]]; then
        if [[ "$ip" == "169.254.169.254" ]] || [[ "$ip" == "169.254.170.2" ]]; then
            log_egress "BLOCKED_METADATA" "$domain -> $ip"
            echo "ERROR: Metadata endpoint blocked" >&2
            return 1
        fi
    fi
    
    log_egress "ALLOWED" "$domain -> $ip"
    echo "$ip"
    return 0
}

# ============================================================
# Check IP privada
# ============================================================

is_private_ip() {
    local ip="$1"
    
    # 10.0.0.0/8
    [[ "$ip" =~ ^10\. ]] && return 0
    
    # 172.16.0.0/12
    [[ "$ip" =~ ^172\.(1[6-9]|2[0-9]|3[0-1])\. ]] && return 0
    
    # 192.168.0.0/16
    [[ "$ip" =~ ^192\.168\. ]] && return 0
    
    # 127.0.0.0/8
    [[ "$ip" =~ ^127\. ]] && return 0
    
    # 169.254.0.0/16 (link-local, including metadata)
    [[ "$ip" =~ ^169\.254\. ]] && return 0
    
    # 0.0.0.0
    [[ "$ip" == "0.0.0.0" ]] && return 0
    
    return 1
}

# ============================================================
# Wrapper para curl/wget
# ============================================================

safe_curl() {
    # Extraer dominio del URL
    local url="$1"
    local domain
    domain=$(echo "$url" | sed -E 's|https?://([^/:]+).*|\1|')
    
    # Validar
    if ! resolve_and_validate "$domain" > /dev/null; then
        return 1
    fi
    
    # Ejecutar curl original
    /usr/bin/curl "$@"
}

safe_wget() {
    local url="$1"
    local domain
    domain=$(echo "$url" | sed -E 's|https?://([^/:]+).*|\1|')
    
    if ! resolve_and_validate "$domain" > /dev/null; then
        return 1
    fi
    
    /usr/bin/wget "$@"
}

# ============================================================
# Exports
# ============================================================

export -f safe_curl safe_wget resolve_and_validate is_private_ip log_egress
export AUDIT_LOG

# Si se ejecuta directamente, instalar aliases
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Egress filter loaded. Use safe_curl/safe_wget or source this script."
    alias curl=safe_curl
    alias wget=safe_wget
fi
