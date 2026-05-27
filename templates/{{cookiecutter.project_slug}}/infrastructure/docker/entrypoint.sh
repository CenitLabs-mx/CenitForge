#!/bin/bash
# Entrypoint para sandbox agéntico
# Configura entorno y arranca shell/comando

set -euo pipefail

echo "=========================================="
echo "Agent Sandbox V5"
echo "=========================================="
echo "User:        $(whoami)"
echo "Working dir: $(pwd)"
echo "Egress:      restricted"
echo "=========================================="

# Marcar como healthy
touch /tmp/healthy

# Cargar egress filter
if [[ -f /usr/local/bin/egress-filter ]]; then
    source /usr/local/bin/egress-filter
    export PATH="/usr/local/bin/sandbox-wrappers:$PATH"
    echo "✓ Egress filter loaded"
fi

# Configurar aliases globales
cat > ~/.bashrc.sandbox << 'EOF'
# Egress filter wrappers
alias curl='safe_curl'
alias wget='safe_wget'

# Aliases de seguridad
alias rm='rm -i'

# Prompt distintivo
export PS1='[sandbox] \w \$ '
EOF

source ~/.bashrc.sandbox

# Configurar límites de recursos (soft)
ulimit -n 1024        # max open files
ulimit -u 256         # max processes
ulimit -v 4194304     # max virtual memory (4GB)

# Ejecutar comando o shell
if [[ $# -eq 0 ]]; then
    exec /bin/bash -l
else
    exec "$@"
fi
