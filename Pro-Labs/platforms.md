# Pro-Labs Platform Compatibility
Read on demand. Y = fully solvable on native platform (no VMs/Wine). N = blocked (requires Windows-only attacker tool).

## Solved Machines
| Machine | OS | Dif | M2 Mac | Linux | Notes |
|---------|-----|-----|--------|-------|-------|
| Down | L | E | Y | Y | All tools via brew/pip |
| Data | L | E | Y | Y | Docker Desktop for M2 ARM OK |
| Retro | W | E | Y | Y | nxc/certipy/impacket all pip, cross-platform |
| Reset | L | E | Y | Y | sshpass/tmux via brew |
| VulnEscape | W | E | N | Y | xfreerdp works but BPV (Windows GUI) needed for password decryption — no alternative on pure macOS |
| Manage | L | E | Y | Y | beanshooter.jar + OpenJDK via brew |
| Forgotten | L | E | Y | Y | All commands run on target via SSH |

## Unsolved Machines
| Machine | OS | Dif | M2 Mac | Linux | Notes |
|---------|-----|-----|--------|-------|-------|
| Baby | W | E | Y | Y | LDAP/nxc/evil-winrm/impacket all cross-platform |
| BabyTwo | W | M | Y | Y | nxc/bloodhound/GPO abuse all pip |
| RetroTwo | W | E | Y | Y | office2john + hashcat + bloodhound all cross-platform |
| Lock | W | E | Y | Y | Gitea + mRemoteNG decrypt + xfreerdp all work |
| Build | L | E | Y | Y | rsync/john/chisel/proxychains all brew |
| Delegate | W | M | Y | Y | bloodyAD + dnstool.py + krbrelayx all pip |
| Job | W | M | Y | Y | msfvenom + sendemail + python http.server all work |
| Media | W | M | Y | Y | responder + hashcat + mingw cross-compile via brew |
| Bamboo | L | M | Y | Y | squidscan Go build + proxychains + pspy all work |
| Phantom | W | M | Y | Y | veracrypt + hashcat 13722 + nxc all available |
| Sendai | W | M | Y | Y | GMSA + certipy + bloodhound all cross-platform |
| Shibuya | W | M | Y | Y | kerbrute + socat + certipy all work |
| Sweep | W | M | Y | Y | sshesame Go binary + nxc + bloodhound all work |
| VulnCicada | W | M | Y | Y | NFS mount + certipy relay + krbrelayx all cross-platform |
| Watcher | L | M | Y | Y | ffuf + CVE-2024-22120 python exploit + nmap all work |
| LustrousTwo | W | H | Y | Y | kerbrute + ilspycmd (dotnet) + responder all work |
| Race | L | H | Y | Y | feroxbuster + sshpass + pspy all brew |
| Redelegate | W | H | Y | Y | keepassxc + bloodyAD + impacket all cross-platform |
| Rainbow | W | M | Y | Y | pwntools + msfvenom + nasm all via brew/pip. SEH BOF tested against remote target — no local debugger needed. |
| Ten | L | H | Y | Y | wfuzz + etcdctl (brew install etcd) all work |
| Zero | L | I | Y | Y | feroxbuster + wfuzz + sftp + pspy all work |
| Reaper | W | I | N | P | Kernel exploit testing requires Windows kernel debugger (WinDbg). Ghidra + pwntools + mingw-w64 work on Linux for cross-compiling. Testing needs separate Windows VM with WinDbg (not in repo). |
| Atlas | W | H | Y | Y | Java deserialization (Castor XML → RMI) + .NET WinSSHTerm crypto analysis. OpenJDK via brew, dotnet via brew, pycryptodome for AES-256-CBC. No Windows-only tools. |
| Breach | W | M | Y | Y | SMB guest → NTLMv2 → kerberoast → silver ticket → MSSQL → SeImpersonate. All tools cross-platform. |
| Bruno | W | M | Y | Y | .NET ZIP slip → DLL hijack → kerberoast → RBCD → DA. pwntools + nxc + impacket all cross-platform. |
| Dump | L | H | Y | Y | PHP cmd injection → tcpdump sudo → AppArmor → motd root. tcpdump built-in, pspy via brew/dl. |
| JobTwo | W | H | Y | Y | Macro phishing → hMailServer → SDF db → Veeam → SYSTEM. msfconsole + dotnet + python all cross-platform. Veeam exploit binary deployed to target. |
| ReaperTwo | W | I | N | P | V8 type confusion + WebAssembly shellcode + kernel driver → token steal. V8/d8 + wabt available on Linux. Kernel driver stage same as Reaper: needs Windows VM with WinDbg (not in repo). |
| Slonik | L | M | Y | Y | NFS → UID trust → PostgreSQL socket tunnel → pg_basebackup → root. psql/pg_basebackup via `brew install libpq`. SSH built-in. |
| Store | L | H | Y | Y | Node.js file read → SFTP → Node inspector → ChromeDriver → root. node/chromedriver via brew. selenium via pip. |

## Puppet Chain (Pro-Lab)
| Step | Tools | M2 Mac | Linux | Notes |
|------|-------|--------|-------|-------|
| FTP anon → Sliver | ftp, Sliver client | N | Y | Sliver client is Linux-only binary |
| PrintNightmare | Mimikatz, PrintNightmare.ps1 | P | P | Tools deployed to target, not attacker |
| AD lateral | impacket, nxc, ssh | Y | Y | All cross-platform |
| Puppet manifest | puppet, ssh, scp | Y | Y | Puppet via brew/apt |
| SharpDPAPI | SharpDPAPI.exe | P | P | Deployed to target |

## Platform Notes
- **M2 Mac strengths**: All Python/pip tools, Homebrew ecosystem, Docker Desktop, Java, Go, dotnet. pwntools + msfvenom work natively for userland BOF exploits. No VM needed for 28/30 unsolved machines.
- **M2 Mac weaknesses**: no BulletsPassView (VulnEscape blocker), no Sliver client binary (Puppet chain blocker), no Windows kernel debugger (Reaper/ReaperTwo blocker).
- **Linux strengths**: Everything native. Sliver client runs directly. Wine available for Windows-only tools like BPV (VulnEscape).
- **Linux weaknesses**: Reaper/ReaperTwo kernel exploit testing needs a separate Windows VM with WinDbg — not included in this repo but doable on Kali with additional setup.
