#!/bin/bash
# Download large binaries (run after clone, SKIPS git LFS)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

# ysoserial-all.jar — Java deserialization toolkit (Atlas)
if [ ! -f "$DIR/ysoserial-all.jar" ]; then
    echo "[+] Downloading ysoserial-all.jar..."
    curl -sL "https://github.com/frohoff/ysoserial/releases/latest/download/ysoserial-all.jar" \
      -o "$DIR/ysoserial-all.jar"
    echo "[+] ysoserial-all.jar downloaded"
else
    echo "[*] ysoserial-all.jar exists, skipping"
fi

# Sliver client — C2 binary (Puppet chain)
SLIVER="$DIR/sliver-client"
if [ ! -f "$SLIVER" ]; then
    echo "[+] Downloading Sliver client..."
    VER=$(curl -sL "https://api.github.com/repos/BishopFox/sliver/releases/latest" \
      | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])")
    curl -sL "https://github.com/BishopFox/sliver/releases/download/$VER/sliver-client_linux-amd64" \
      -o "$SLIVER"
    chmod +x "$SLIVER"
    echo "[+] Sliver client $VER downloaded"
else
    echo "[*] sliver-client exists, skipping"
fi
