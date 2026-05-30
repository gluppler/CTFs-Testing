#!/bin/bash
# ad-recon.sh - Active Directory enumeration
# Usage: ./ad-recon.sh <domain> <dc-ip> [guest_user]

DOMAIN="${1:-retro.vl}"
DC_IP="${2:-10.129.234.44}"
GUEST="${3:-Guest}"

VENV="/Users/gluppler/Downloads/CTFs-Testing/Pro-Labs/.venv313/bin"

echo "=== AD RECON: $DOMAIN ($DC_IP) ==="

# 1. SMB shares with Guest/null auth
echo "[1] SMB shares (Guest)..."
$VENV/nxc smb "$DOMAIN" -u "$GUEST" -p "" --shares 2>/dev/null | grep -v "Creating\|Initializing\|First" | tail -10

# 2. RID brute force for user enumeration
echo "[2] RID enumeration..."
$VENV/nxc smb "$DOMAIN" -u "$GUEST" -p "" --rid-brute 1200 2>/dev/null | grep "SidTypeUser" | head -20

# 3. User enumeration via ldap
echo "[3] LDAP users..."
$VENV/nxc ldap "$DC_IP" -u "$GUEST" -p "" --users 2>/dev/null | grep -v "Creating\|Initializing" | tail -15

echo ""
echo "=== Done ==="
