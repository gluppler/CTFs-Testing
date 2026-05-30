#!/bin/bash
# linux-privesc.sh - Quick Linux privilege escalation checks
# Usage: ./linux-privesc.sh <user@host> [password]

SSH_TARGET="$1"
PASS="$2"

if [ -z "$SSH_TARGET" ]; then
    echo "Usage: linux-privesc.sh <user@host> [password]"
    exit 1
fi

do_ssh() {
    if [ -n "$PASS" ]; then
        sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_TARGET" "$1" 2>/dev/null
    else
        ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_TARGET" "$1" 2>/dev/null
    fi
}

do_sudo() {
    if [ -n "$PASS" ]; then
        sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_TARGET" "echo '$PASS' | sudo -S $1" 2>/dev/null
    fi
}

echo "=== Linux Privilege Escalation ==="
echo "Target: $SSH_TARGET"
echo ""

echo "[1] Sudo privileges"
do_ssh 'sudo -l 2>/dev/null || echo "no sudo"'

echo "[2] SUID binaries (common)"
do_ssh 'find / -perm -4000 -type f 2>/dev/null | grep -vE "snap|/usr/lib|busybox" | head -20'

echo "[3] Writable cron jobs"
do_ssh 'ls -la /etc/cron* 2>/dev/null; ls -la /var/spool/cron/crontabs 2>/dev/null'

echo "[4] Capabilities"
do_ssh 'getcap -r / 2>/dev/null | head -10'

echo "[5] World-writable files"
do_ssh 'find /etc -writable -type f 2>/dev/null | head -10'

echo "[6] Listening services"
do_ssh 'ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null'

echo "[7] Group memberships"
do_ssh 'id; groups'

echo "[8] Try sudo with password"
do_sudo 'id 2>/dev/null'
do_sudo 'cat /root/root.txt 2>/dev/null'

echo ""
echo "=== Done ==="
