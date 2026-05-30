# Pro-Labs Strategy Guide
Read on demand for per-machine attack sequencing, pitfalls, and preparation.

## Tier 1: Easy / Quick Wins (start here)
These machines follow well-known patterns with minimal complexity.

### Baby (Windows, Easy)
- **Chain**: LDAP enum → spray → SeBackup → NTDS.dit → PtH → DA
- **Key tools**: nxc, evil-winrm, impacket-secretsdump
- **Pitfalls**: `robocopy /b` for NTDS copy, not direct file access
- **Flags**: user.txt via SMB or RDP, root.txt via secretsdump

### BabyTwo (Windows, Medium)
- **Chain**: Weak passwords → logon scripts → ACL abuse → GPO → DA
- **Key tools**: nxc, bloodhound-python, smbclient, pygpoabuse
- **Pitfalls**: Logon script path must be writable; use PowerView `Add-DomainObjectACL`
- **Flags**: user on desktop, root via DA access

### RetroTwo (Windows, Easy)
- **Chain**: SMB → .accdb crack → VBA creds → GenericWrite → RPC → SYSTEM
- **Key tools**: nxc, office2john + hashcat 9600, bloodyAD, xfreerdp, Perfusion.exe
- **Pitfalls**: .accdb password ≠ VBA password; extract both. $ sid = domain RID
- **Flags**: user + root via RDP as admin

### Lock (Windows, Easy)
- **Chain**: Gitea → PAT → webshell → mRemoteNG config → PDF24 LPE
- **Key tools**: curl, git, xfreerdp, mremoteng_decrypt.py, SetOpLock.exe
- **Pitfalls**: Gitea token from user settings page; mRemoteNG decrypts with `python3 mremoteng_decrypt.py`
- **Flags**: user via webshell, root via PDF24 + oplock

### Build (Linux, Easy)
- **Chain**: rsync → Jenkins decrypt → GitLab → webhook → Docker → RSH
- **Key tools**: rsync, python3, chisel, proxychains, mysql, john
- **Pitfalls**: Multiple pivot steps; Jenkins decryption key in `credentials.xml`. RSH port 513.
- **Flags**: user in Jenkins workspace, root via Docker or RSH

## Tier 2: Medium (AD + Web)
### Breach (Windows, Medium)
- **Chain**: SMB guest → NTLMv2 capture → kerberoast → silver ticket → MSSQL → SeImpersonate
- **Key tools**: nxc, responder, hashcat, impacket
- **Pitfalls**: Guest write on SMB → drop `@` file for UNC path capture. Silver ticket for Administrator to MSSQL. xp_cmdshell may need enabling.
### Bruno (Windows, Medium)
- **Chain**: .NET ZIP slip → DLL hijack → kerberoast → RBCD → DA
- **Key tools**: pwntools/python (ZIP generation), nxc, impacket, kerbrute
- **Pitfalls**: ZIP extraction uses Path.Combine + no sanitization → craft `../../` paths. svc_scan kerberoastable. Machine account quota of 10 for RBCD.
### Slonik (Linux, Medium)
- **Chain**: NFS → UID trust → PostgreSQL socket tunnel → pg_basebackup → root
- **Key tools**: nfs, ssh -L, psql, pg_basebackup, pspy
- **Pitfalls**: NFS mounts with `no_root_squash`? Check UID/GID match. PSQL socket only local → SSH tunnel. `COPY ... FROM PROGRAM` for RCE. pg_basebackup SUID binary.
### Delegate (Windows, Medium)
- **Chain**: Guest → hardcoded creds → WriteProperty → RBCD → DA
- **Key tools**: nxc, bloodyAD, krbrelayx, impacket-addcomputer
- **Pitfalls**: WriteProperty ACL on user object → set msDS-AdditionalDnsHostName for RBCD

### Job (Windows, Medium)
- **Chain**: SMTP → LibreOffice macro → RCE → SeImpersonate → Potato → SYSTEM
- **Key tools**: msfconsole (openoffice_document_macro), sendemail, GodPotato
- **Pitfalls**: SMTP may filter attachments; encode macro in base64. IIS `wwwroot` must be writable.

### Media (Windows, Medium)
- **Chain**: XAMPP → NTLMv2 leak → NTFS junction → SeTcbPrivilege → SYSTEM
- **Key tools**: responder, hashcat, mklink /J, mingw-w64 (compile TcbElevation)
- **Pitfalls**: `ntlm_theft.py` for UNC path generation; NTFS junction requires `icacls` write permission

### Bamboo (Linux, Medium)
- **Chain**: Squid proxy → PaperCut CVE-2023-27350 → writable root script → root
- **Key tools**: squidscan, proxychains, pspy, curl
- **Pitfalls**: PaperCut runs on internal port only → need proxy pivot first. CVE-2023-27350 = unauthenticated RCE

### Phantom (Windows, Medium)
- **Chain**: SMB → VeraCrypt → VyOS → RBCD → DA
- **Key tools**: nxc, hashcat 13722, veracrypt, impacket rbcd
- **Pitfalls**: VeraCrypt volume cracked offline (hashcat -m 13722). VyOS config contains AD creds for RBCD.

### Sendai (Windows, Medium)
- **Chain**: RID brute → GMSA → ESC4 → ESC1 → DA
- **Key tools**: nxc, bloodyAD, certipy, evil-winrm
- **Pitfalls**: GMSA password readable by anyone in domain. ESC4 modifies template before ESC1.

### Shibuya (Windows, Medium)
- **Chain**: kerbrute → machine red:red → WIM hashes → cross-session → ESC1
- **Key tools**: kerbrute, impacket, socat, certipy, RemotePotato0
- **Pitfalls**: Mount WIM files with `sudo mount -o loop`. Cross-session relay via RemotePotato0 + socat.

### Sweep (Windows, Medium)
- **Chain**: Guest → Lansweeper → SSH honeypot → GenericAll → package deploy → DA
- **Key tools**: nxc, sshesame, bloodyAD, evil-winrm
- **Pitfalls**: sshesame captures creds from Lansweeper auto-test. GenericAll over Lansweeper Admins group.

### VulnCicada (Windows, Medium)
- **Chain**: NFS → password image → ESC8 → Kerberos relay → DA
- **Key tools**: nxc, certipy, ntlmrelayx, krbrelayx, RemoteKrbRelay.exe
- **Pitfalls**: ESC8 requires HTTP relay target. Kerberos self-relay bypasses NTLM disabled policy.

### Watcher (Linux, Medium)
- **Chain**: Zabbix CVE-2024-22120 → backdoor webapp → TeamCity → root
- **Key tools**: ffuf, python3 exploit, ssh, nmap (local scan)
- **Pitfalls**: Zabbix RCE via `item.get` with `webbrain.cfg` config. TeamCity agent terminal runs as root.

## Tier 3: Hard (requires multiple pivots / advanced techniques)
### Atlas (Windows, Hard)
- **Chain**: Java Castor XML deserialization → RMI RCE → .NET WinSSHTerm crypto → admin creds
- **Key tools**: java, ysoserial, dotnet/ilspycmd, python3 + pycryptodome
- **Pitfalls**: Castor XML marshalling leads to Java RMI deserialization. WinSSHTerm uses AES-256-CBC with PBKDF2-SHA1 — reverse the binary for key derivation.
- **M2 note**: Java + .NET both via brew. Python crypto tools via pip. All cross-platform.
### Dump (Linux, Hard)
- **Chain**: PHP file naming command injection → tcpdump → AppArmor bypass → motd → root
- **Key tools**: curl, tcpdump, python3, pspy
- **Pitfalls**: Argument injection via crafted filename in PHP. tcpdump sudo + `-z` flag for arbitrary command. AppArmor blocks direct /root reads → bypass via tmpfs + motd exec.
- **M2 note**: tcpdump built-in on macOS. No special tools needed.
### JobTwo (Windows, Hard)
- **Chain**: Macro phish → hMailServer config → SDF db decrypt → Veeam exploit → SYSTEM
- **Key tools**: msfconsole (macro gen), sendemail, dotnet/python (SDF parsing), Veeam exploit
- **Pitfalls**: hMailServer config file on target has encrypted DB creds. SDF is SQL Server Compact — use dotnet or python-sdf. Veeam exploit runs as SYSTEM via sqlserver.exe.
- **M2 note**: msfconsole + dotnet via brew. Veeam exploit binary deployed to target.
### Store (Linux, Hard)
- **Chain**: Node.js file upload → arbitrary file read → SFTP creds → Node inspector → ChromeDriver → root
- **Key tools**: curl, node, sftp, chromedriver, selenium
- **Pitfalls**: File read finds SFTP creds AND env vars revealing `--inspect` flag. SFTP tunnel to forward Node inspector port. ChromeDriver WebDriver API accepts arbitrary browser scripts.
- **M2 note**: node + chromedriver via brew. selenium via pip.
### LustrousTwo (Windows, Hard)
- **Chain**: File read → UNC inject → NTLMv2 → S4U2self → .NET decompile → Velociraptor
- **Key tools**: kerbrute, responder, impacket-getST, ilspycmd, curl --negotiate
- **Pitfalls**: NTLM disabled → Kerberos-only auth. S4U2self bypasses "sensitive and cannot be delegated". Velociraptor API key in server.config.yaml.
### Redelegate (Windows, Hard)
- **Chain**: FTP → Keepass → MSSQL → SID spray → ForceChangePassword → Constrained Delegation
- **Key tools**: keepassxc, john, nxc mssql, bloodyAD, impacket
- **Pitfalls**: Keepass key + file both on FTP. MSSQL `xp_cmdshell` may be blocked.
### Race (Linux, Hard)
- **Chain**: Grav CMS → backup → token theft → theme upload → TOCTOU
- **Key tools**: feroxbuster, curl, pspy, python3
- **Pitfalls**: Named pipe TOCTOU requires precise timing. Write a script, don't try manually.
### Ten (Linux, Hard)
- **Chain**: FTP signup → MySQL UID → SSH key → etcd → Apache config → root
- **Key tools**: wfuzz, ftp, ssh, etcdctl
- **Pitfalls**: Shared-hosting environment; UID/GID collision with existing system user. etcd config poisoning triggers Apache reload.

## Tier 4: Specialized (binary exploitation / niche techniques)
### Rainbow (Windows, Medium)
- **Skill**: SEH buffer overflow + egghunter + FodHelper UAC bypass
- **Key tools**: pwntools, msfvenom, nasm, Burp Suite
- **Pitfalls**: Egghunter needed for WOW64. `msf-nasm_shell` for opcode generation. Test against remote target (not locally).
- **M2 note**: No VM needed. pwntools + msfvenom + nasm all via brew/pip. SEH BOF tested against remote target.
### Zero (Linux, Insane)
- **Skill**: .htaccess abuse + Apache cron config injection
- **Key tools**: feroxbuster, wfuzz, sftp, perl, pspy
- **Pitfalls**: .htaccess `php_value auto_prepend_file` for arbitrary file read. Apache config integrity check is a cronjob — inject condition to leak root files.
### Reaper (Windows, Insane)
- **Skill**: Format string leak + BOF ROP + DPAPI + kernel driver IOCTL → token steal
- **Key tools**: pwntools, ghidra, ropper, mingw-w64, msfvenom
- **Pitfalls**: Two-stage exploit (userland BOF + kernel driver). Kernel driver reversing needs NTDDK symbols. Token steal via `_EPROCESS->ActiveProcessLinks`.
- **M2 note**: Ghidra works natively. Kernel exploit testing needs Windows kernel debugger — impractical on any platform without a Windows target debug setup. Consider skipping.
### ReaperTwo (Windows, Insane)
- **Skill**: V8 type confusion (Harmony Set) + WebAssembly shellcode + kernel driver (fptr exec → PTE modify → token steal)
- **Key tools**: pwntools, wabt (wat2wasm), ghidra, ropper, d8 (V8 shell)
- **Pitfalls**: Two-stage: browser exploit (V8) + kernel driver. V8 type confusion in Set methods. WASM for shellcode execution. Kernel stage same as Reaper — MSR leak, stack pivot, ROP, PTE modify.
- **M2 note**: V8/d8 buildable on macOS (`brew install v8` + depot_tools). wabt via brew. Kernel stage blocker same as Reaper — no BSOD-safe kernel exploit testing. Consider skipping unless dedicated Windows debug VM.

## Chain Lab
### Puppet (Complete, writeup exists)
- **Full chain**: Pro-Labs/Puppet/writeup.md
- **Key insight**: Sliver C2 via FTP multiplayer config. PrintNightmare for first SYSTEM. Puppet manifest exec for DC lateral. SharpDPAPI for final flag (NOT in LSASS).
- **M2 note**: Sliver client is Linux-only binary. Need a container/VM for that tool. Everything else (Mimikatz DLLs, SharpDPAPI, PrintNightmare.ps1) runs on the target.
### Mythical (Not started)
- **Status**: No writeup, no info — unknown scope.

## Preparation Checklist
Before starting any machine:
- [ ] Add target to /etc/hosts: `echo "TARGET_IP domain.vl" | sudo tee -a /etc/hosts`
- [ ] Check target ports: `nmap -sV -p- TARGET_IP`
- [ ] Run pipeline: `./Pro-Labs/Machines/scripts/pipeline.sh TARGET_IP`
- [ ] Check wiki: `Pro-Labs/index.md` + `Pro-Labs/log.md` for known patterns
- [ ] Read patterns.md for matching attack chain (compiled from our solves)
