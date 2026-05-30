#!/bin/bash
# web-recon.sh - Web reconnaissance automation
# Source from pipeline.sh: source ./web-recon.sh
#
# Functions:
#   web_recon <base_url>

web_recon() {
    local base="$1"

    if [ -z "$base" ]; then
        echo "Usage: web_recon <base_url>"
        return 1
    fi

    type log &>/dev/null || log() { echo "[$(date +%H:%M:%S)] $*"; }

    local host=$(echo "$base" | sed 's|https\?://||;s|/.*||;s|:.*||')
    log "  === RECON on $base ==="

    # Step 1: Page source analysis
    log "  [1] Analyzing page source..."
    local body=$(curl -sk "$base/" 2>/dev/null)
    echo "$body" | grep -oE 'src="[^"]+\.js[^"]*"' | while read -r js; do
        local js_url=$(echo "$js" | sed 's/src="//;s/"//')
        [ "${js_url:0:4}" != "http" ] && js_url="${base}${js_url}"
        log "  JS: $js_url"
    done
    echo "$body" | grep -oE 'href="[^"]+\.(js|css|map)"' | while read -r asset; do
        log "  Asset: $asset"
    done

    # Step 2: Hidden endpoints from JS
    log "  [2] Extracting endpoints from JS..."
    local js_files=$(echo "$body" | grep -oE 'src="[^"]+\.js[^"]*"' | sed 's/src="//;s/"//')
    for js in $js_files; do
        [ "${js:0:4}" != "http" ] && js="${base}${js}"
        local js_content=$(curl -sk "$js" 2>/dev/null)
        echo "$js_content" | grep -oE '["'\'']\/[a-zA-Z0-9_/\-]+["'\'']' | tr -d '"'\' | sort -u | while read -r ep; do
            log "  Endpoint: $ep"
        done
        echo "$js_content" | grep -oE '"v[0-9]+"' | sort -u | while read -r v; do
            log "  API version: $v"
        done
    done

    # Step 3: HTTP method testing on common endpoints
    log "  [3] Testing alternate HTTP methods..."
    for ep in /api /admin /login /register /reset; do
        local post_code=$(curl -sko /dev/null -w "%{http_code}" -X POST "$base$ep" 2>/dev/null)
        local put_code=$(curl -sko /dev/null -w "%{http_code}" -X PUT "$base$ep" 2>/dev/null)
        local patch_code=$(curl -sko /dev/null -w "%{http_code}" -X PATCH "$base$ep" 2>/dev/null)
        [ "$post_code" != "404" ] && [ "$post_code" != "405" ] && [ "$post_code" != "000" ] && log "  POST $ep -> $post_code"
        [ "$put_code" != "404" ] && [ "$put_code" != "405" ] && log "  PUT $ep -> $put_code"
        [ "$patch_code" != "404" ] && [ "$patch_code" != "405" ] && log "  PATCH $ep -> $patch_code"
    done

    # Step 4: Response header analysis
    log "  [4] Response header analysis..."
    curl -skI "$base/" 2>/dev/null | while read -r header; do
        echo "$header" | grep -qiE "x-|server|powered|frame|csrf|cors|cookie|token|auth" && log "  $header"
    done

    log "  Recon complete."
}
