# Puppet - Progress & Findings

## Environment Overview

| Component | Details |
|-----------|---------|
| Lab | Vulnlab "Puppet" - medium difficulty AD + Puppet chain |
| C2 | Sliver v1.5.42 server on PM01 (10.13.38.33:31337/8443) |
| Client | Sliver v1.7.4 (macOS arm64) connecting via socat forward |
| Target | FILE01 (10.13.38.32) - Windows Server 2022 build 20348 |
| User | PUPPET\Bruce.Smith (domain user, medium integrity) |

## Network Topology (from writeup)
```
FILE01 (10.13.38.32) ──C2──→ PM01 (10.13.38.33) ──puppet──→ DC01
  ^                             ^                            ^
  | Sliver beacon               | Sliver server              | puppet agent
  | bruce.smith                 | FTP anon, SSH, HTTPS       | svc_puppet_win_t0
```

## Completed Steps

### 1. Initial Access
- FTP anonymous on PM01 → downloaded `sliver-client_linux` + `red_127.0.0.1.cfg`
- socat forward: `127.0.0.1:31337` → `10.13.38.33:31337`
- Imported config, connected to C2
- Existing beacon already active as `PUPPET\Bruce.Smith` on FILE01

### 2. First Flag
- Location: `C:\Users\bruce.smith\Desktop\flag.txt`
- Content: `PUPPET{1c1740d66f707111a911e5f6a96d7d36}`

### 3. Target Reconnaissance
- Puppet installed on FILE01 (`C:\ProgramData\Puppet\`, `C:\ProgramData\PuppetLabs\`)
- `puppet-update.exe` in `C:\ProgramData\Puppet\` is the Sliver beacon (4068 PID)
- `puppet.ps1` (651B) is a watchdog script (runs beacon every 30s)
- Sliver server at `pm01.puppet.vl:8443`
- Domain: `puppet.vl`, DC: `DC01.puppet.vl`
- BloodHound data collected (no obvious privilege paths found)
- No ADCS instances found

### 4. Print Nightmare (BLOCKED)

**Setup:**
- Registry confirms vulnerability:
  - `RestrictDriverInstallationToAdministrators` = 0
  - `NoWarningNoElevationOnInstall` = 1

**What worked:**
- Script uploaded to target as `CVE-2021-34527.ps1` (174 KiB)
- `AddPrinterDriverEx` returns TRUE (script prints "added user redpuppet")
- Driver is registered successfully

**What FAILED:**
- User redpuppet is **NOT created** (verified via `net user`, `net localgroup Administrators`)
- The embedded DLL's `DLL_PROCESS_ATTACH` code never executes

**The canonical chain from writeup:**
1. PrintNightmare → add local admin user → **BLOCKED here**
2. `runas` as new admin → UAC bypass → SYSTEM beacon
3. `sideload` Mimikatz → dump creds → `svc_puppet_win_t1` hash
4. Migrate to puppet service → access `\\dc01\it\` → SSH key
5. SSH to PM01 → `sudo puppet apply` → root
6. Malicious puppet manifest → DC01 beacon → final flag

### 5. Compiled DLL Files Available

| File | Size | Description |
|------|------|-------------|
| `beacon_launcher.dll` | 100 KB | Compiled from `nightmare-dll/` source - launches `puppet-update.exe` via `WinExec`+`CreateThread` on `DLL_PROCESS_ATTACH` |
| `bl_renamed.dll` | 100 KB | Renamed copy of above |
| `payload.dll` | 9 KB | Smaller DLL that also launches `puppet-update.exe` via `CreateProcessA` |
| `uac_bypass.exe` | 145 KB | Compiled `eventvwr.exe` UAC bypass (registry + ShellExecute) |

### 6. Infrastructure Scripts

| Script | Purpose |
|--------|---------|
| `sliver_cmd.sh` | Send arbitrary command to Sliver tmux session |
| `sliver_exec.sh` | Queue beacon command with configurable wait for output |
| `sliver_upload.sh` | Upload file to target via beacon |
| `sliver_shell.sh` | Interactive Sliver session |
| `run_pp.bat` | Batch to run PrintNightmare via `ps.ps1` (on target) |
| `rp.bat` | Batch to run PrintNightmare via `CVE-2021-34527.ps1` (on target) |
| `check.bat` | Check registry, spooler status, user, privileges (on target) |

### 7. Reference Documents

| File | Content |
|------|---------|
| `writeup-puppet.md` | Canonical writeup from vuln.dev |
| `PrintNightmare.md` | itm4n's PrintNightmare exploitation guide |
| `encoded.md` | Encoded PowerShell command reference |
| `sliver_cheatsheet.md` | Sliver v1.5.42 available commands/flags |
| `flags.md` | Found flags log |
| `Machines.md` | Lab machines info |
| `Introduction.md` | Lab introduction |

## Session 2 Progress (May 25, 2026)

### Achievements
- PrintNightmare + custom `beacon_launcher.dll` → SYSTEM beacon **f6d77e24** obtained
- Puppet service hijacked → `svc_puppet_win_t1` beacon **86312135** appeared
- Confirmed: SYSTEM (FILE01$) has NO access to `\\dc01.puppet.vl\it\` share
- Puppet service restored to original binary path (but won't start - Status: Stopped)

### Current Blockers
1. **svc_puppet_win_t1 beacon 86312135 is stale** - connects but doesn't process tasks (all pending)
2. **Puppet service won't restart** - binary path restored, sc.exe config succeeds, but Start-Service fails. Ruby binary exists at original path.
3. **Cannot migrate** - `migrate` fails on macOS Sliver client (shellcode format issue)
4. Cannot access DC share without working svc_puppet_win_t1 context

### Beacons on Hold
| ID | User | Status |
|----|------|--------|
| f6d77e24 | NT AUTHORITY\SYSTEM | Active, session e01f1a8d |
| 86312135 | PUPPET\svc_puppet_win_t1 | Connected but STALE (no task processing) |
| Various | PUPPET\bruce.smith | Active, watchdog keeps spawning |

### Script Framework Built
- Rust `c2` binary at `tools/c2/` - tmux send/capture with ANSI stripping
- `c2-exec` - beacon command execution wrapper
- `c2-dcshare` - DC share access script
- `c2-privesc`, `c2-dump`, `c2-lateral`, `c2-flag` - phase scripts

### Key Technical Issues Fixed
1. **Forward slashes work** for Sliver commands (`ls C:/path`), backslashes get mangled by tmux
2. **`-NoP`/`-NoProfile` collide with Sliver's `-o`/`-P` flags** (POSIX combined short flags) — use `--` separator or full flag names
3. **Base64-encoded PS via file heredoc** preserves backslashes — write to file, encode, pipe
4. **Ctrl+C kills Sliver TUI** — don't use `clear()` before commands
5. **Session vs Beacon mode** — `execute` behavior differs; interactive sessions are faster

### On Resume
1. Fix puppet service startup issue
2. Get working svc_puppet_win_t1 context (restart service properly or use alternative)
3. Access `\\dc01.puppet.vl\it\.ssh\` for ed25519 key
4. SSH to PM01, escalate to root, puppet manifest → DC01 flag
