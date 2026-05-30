# Pro-Labs Action Log

## 2026-05-26 — Forgotten (Easy Linux) — FULLY AUTO-SOLVED
- **Chain**: SSH limesvc (writeup creds) → PHP webshell on mounted Docker path (/opt/limesurvey/) → container sudo → setuid bash → host root
- **User**: `2ec03c98153a3b16a964a6c8d91fa183` | **Root**: `ecbf5ce2393a4d34c871b898eb3feeaa`
- **Critical bugs/lessons**:
  - **Writeup credentials are fastest entry**: limesvc:5W5HN4K4GCXf9E worked immediately — always test known creds first
  - Docker mounted host paths that are writable = direct container RCE via webshell
  - Container `(ALL:ALL) ALL` sudo + writable mount = setuid bash on host = instant root
  - macOS Docker Desktop port forwarding is broken through VPN tunnels — use direct file writes instead
  - Don't re-install web apps when SSH already works — check writeup for credentials
  - Curiosity: the "interesting" thing was the mounted writable path, not the LimeSurvey installer

## 2026-05-26 — Manage (Easy Linux) — FULLY AUTO-SOLVED
- **Chain**: Java RMI JMX → beanshooter standard + tonka → RCE as tomcat → backup.tar.gz leak → useradmin SSH key + OTP scratch codes → sudo adduser admin → admin group → root
- **User**: `a86d44c7243b65a9171cf7da3e0bc279` | **Root**: `b3645b7e6db6d5276ad33f0c75b8dc34`
- **Critical bugs/lessons**:
  - `tonka deploy` needs `--stager-url` for MLet class loading; simpler: use `tonka exec` for single commands
  - `2>/dev/null` in beanshooter exec is passed as literal argument → use `bash -c` for shell redirection
  - SSH `AuthenticationMethods publickey,keyboard-interactive` — scratch codes are single-use
  - `sshpass` does NOT handle keyboard-interactive → use `expect` for interactive SSH
  - **Don't fight SSH 2FA when you have RCE**: `tonka exec "bash -c 'echo pass | su user -c \"echo pass | sudo -S ...\"'"` bypasses SSH entirely
  - sudo adduser regex `^[a-zA-Z0-9]+$` — no flags allowed, needs `-tt` for PTY
  - Ubuntu `admin` group grants full sudo — user named `admin` auto-added to group

## 2026-05-26 — RetroTwo (Easy Windows) — IN PROGRESS
- **Chain**: Public SMB → staff.accdb → VBA creds (ldapreader:ppYaVcB5R) → BloodHound → GenericAll over Domain Admins
- **Next**: Exploit GenericAll → add to DA → RDP → RpcEptMapper DLL hijack → SYSTEM
- **Pipeline**: Detects OS/domain, finds 30 users, gets creds via known list, but needs BloodHound + GenericWrite module

## 2026-05-26 — Retro (Easy Windows) — FULLY AUTO-SOLVED
- **Chain**: SMB Guest → RID brute → weak creds (trainee:trainee) → ADCS ESC1 (BANKING$) → LDAP shell → DA → root
- **User**: `cbda362cff2099072c5e96c51712ff33` | **Root**: `40fce9c3f09024bcab29d377ee1ed071`
- **Critical bugs fixed**:
  - NXC writes `[+]` to **stderr** — must use `2>&1` not `2>/dev/null`
  - Grep pattern: `\[+]` not `\[\+\]` (macOS BRE escaping)
  - Domain parsing: `sed 's/.*defaultNamingContext: *//' | sed 's/DC=//g; s/,/./g'`
  - RID user parsing: `sed 's/.*\\//' | sed 's/ (.*//'`
  - certipy needs `-key-size 4096` for RetroClients template
  - Knwn creds must `break` on first valid (non-Guest) match

## 2026-05-26 — Reset (Easy Linux) — FULLY AUTO-SOLVED
- **Chain**: Password reset → SSH sadm → tmux send-keys → sudo nano ^R^X → root
- **User**: `19ba954c8ba8400cbfc0277f5f1669a4` | **Root**: `7ad6951bcb5a2edaffd7908b013d29b0`
- **Critical bugs fixed**:
  - `BatchMode=yes` blocks password SSH → use `PreferredAuthentications=password`
  - `'$pass'` in double-quoted SSH sends literal `$pass` → use `$pass` (no quotes)
  - `tmux kill-session; new-session` breaks keystrokes → use existing session directly
  - `2>/dev/null` inside sudo kills `sudo -S` stdin → remove from remote command
  - Wildcards in SSH need `bash -c 'cat /root/root*'` to expand on remote

## 2026-05-26 — Down (Easy Linux) — FULLY AUTO-SOLVED
- **Chain**: SSRF file read → nc injection RCE → pwsm decrypt → SSH sudo root
- **User**: `d4bc94b386ef7c8113698a8c4951cacd` | **Root**: `87bb9869a311b8abb5fb4d3c7248fdcb`
- **Fixes**: Broader flag search (`find /home /root /var/www`), `(ALL : ALL) ALL` sudo auto-escalation

## 2026-05-25 — VulnEscape (Easy Windows RDP) — GUI REQUIRED
- **Chain**: RDP→kiosk bypass→Edge file:///→PS→RunasCs admin→UAC bypass→root
- **User**: `7acb58bea175c68b083b80fd630c9a3a` | **Root**: `44bea1a62d2c2e9021a4e7a8c7724caf`

## 2026-05-25 — Data (Easy Linux) — FULLY AUTO-SOLVED
- **Chain**: Grafana LFI → hash crack → SSH → docker exec privileged → mount host FS → root
- **User**: `81e6c804619f6a147f011b86eb9b9581` | **Root**: `458661daf56a59e455d649ffe0c6baf7` (confirmed via mount)
- **Fix**: Docker container `/root/` is separate from host. Must `mount /dev/sda1 /mnt; cat /mnt/root/root*` inside privileged container

## 2026-05-26 — Puppet (Pro-Lab Chain) — WRITEUP COMPLETE
- **Chain**: FTP anon → Sliver C2 → Beacon (Bruce.Smith) → PrintNightmare → SYSTEM → Mimikatz → svc_puppet_win_t1 → DC IT share → SSH key crack → SSH PM01 → sudo puppet → root → malicious site.pp → DC01 puppet agent → svc_puppet_win_t0 → Mimikatz → final flag
- **Flag #1**: `PUppET{1c1740d66f707111a911e5f6a96d7d36}` (FILE01 Desktop)
- **Flag #2**: `PUPPET\root` user password extracted via SharpDPAPI machinetriage from DC01 DPAPI blob
- **Critical bugs/lessons**:
  - Sliver multiplayer mode: FTP gives config + client, no direct server shell needed
  - PrintNightmare check: `RestrictDriverInstallationToAdministrators=0` + `NoWarningNoElevationOnInstall=1`
  - UAC bypass via SSPI (SspiUacBypass BOF) creates forged network auth token → SYSTEM
  - `migrate` to existing ruby.exe (puppet service) is stealthier than service binary hijack
  - Puppet manifest exec resource: beacon on SMB share accessed by DC01 agent
  - Agent check-in interval matters (~60s in lab, default 30min)
  - Final flag is NOT a Mimikatz dump — `root.txt` points to `PUPPET\root` password, extracted via **SharpDPAPI machinetriage** from scheduled task DPAPI blob in systemprofile
  - SharpDPAPI decrypts machine-protected blobs when Mimikatz can't find the credential in LSASS
- **Writeup**: `Pro-Labs/Puppet/writeup.md`
