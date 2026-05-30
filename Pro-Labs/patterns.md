# Pro-Labs Attack Pattern Catalog
Read on demand for pattern recognition during solve.
Compiled from our own solves — not from external writeups.

## Web → Linux PrivEsc (14 machines)
| Pattern | Machine | Key Tools | Chain |
|---------|---------|-----------|-------|
| SSRF file read → RCE → decrypt → sudo root | Down | curl, escapeshellcmd, cryptocode, sshpass | `/../../etc/passwd` → nc injection in `$sendMailPath` → decrypt pwsm.blob → SSH → sudo |
| Grafana LFI → hash crack → docker priv | Data | curl, CVE-2021-43798, sqlite3, hashcat 10900 | `/public/plugins/.../grafana.db` → extract hash/salt → crack → SSH → docker exec → `mount /dev/sda1` |
| Password reset → SSH → tmux → sudo nano GTFOBins | Reset | curl, sshpass, tmux send-keys | Reset admin password → SSH sadm → `tmux send-keys` → sudo nano `^R^X` → shell → root flag |
| JMX → RCE → backup leak → 2FA bypass → sudo adduser | Manage | beanshooter, tonka, java | `tonka exec` on 2222 → RCE as tomcat → backup.tar.gz → scratch codes → ssh useradmin → `sudo adduser admin` → `su admin` → `sudo su` |
| SSH → webshell on Docker mount → setuid bash | Forgotten | sshpass, curl, base64 webshell | SSH limesvc → write `<?php system($_GET['c']);?>` to `/opt/limesurvey/` → cp bash + chmod +s → `bash -p` → host root |
| Squid proxy → PaperCut CVE-2023-27350 → writable root script | Bamboo | squidscan, proxychains, curl, pspy | Proxy pivot → PaperCut RCE → find writable root cron script → modify → wait → root |
| rsync → Jenkins decrypt → GitLab → webhook RCE → Docker → RSH | Build | rsync, python3 decrypt.py, chisel, mysql | rsync share → decrypt Jenkins creds → GitLab → webhook → RCE → Docker → MySQL → `.rhosts` → RSH |
| Grav CMS → backup → token theft → theme upload → TOCTOU | Race | feroxbuster, curl, pspy, python3 | Weak basic auth → backup download → rest token → proxy interception → custom theme upload RCE → named pipe TOCTOU → root |
| FTP signup → MySQL UID pivot → etcd Apache poisoning | Ten | wfuzz, ftp, ssh, etcdctl | Public FTP signup → UID/GID overlap with system → SSH key inj → etcd config poison → Apache reload → root |
| Zabbix CVE-2024-22120 → TeamCity agent terminal → root | Watcher | ffuf, python3 exploit, ssh, nmap | Zabbix RCE → backdoor web app → steal creds → SSH tunnel → TeamCity agent terminal → root |
| SFTP → .htaccess file read → cron config injection | Zero | feroxbuster, sftp, perl, pspy | SFTP web root → .htaccess `php_value auto_prepend_file` → arbitrary read → hardcoded creds → SSH → cron integrity check abuse → config injection → root |
| PHP arg injection → tcpdump sudo → AppArmor → motd root | Dump | curl, tcpdump, python3, pspy | PHP file naming cmd injection → www-data → sudo tcpdump → AppArmor bypass via tmpfs → motd exec → root |
| NFS → UID trust → PG socket tunnel → pg_basebackup → root | Slonik | nfs, ssh, psql, pg_basebackup | NFS exports → UID/GID match home dir → history file creds → SSH tunnel to PG socket → `COPY ... PROGRAM` RCE → pspy backup script → pg_basebackup SUID → root |
| Node.js upload → file read → inspector → ChromeDriver root | Store | curl, node, sftp, chromedriver, selenium | File upload → arbitrary file read → config leak → SFTP creds → Node inspector tunnel → JS eval RCE → WebDriver API → malicious script → root |

## SMB → ADCS → Domain Admin (5 machines)
| Pattern | Machine | Key Tools | Chain |
|---------|---------|-----------|-------|
| SMB Guest → RID brute → weak creds → ESC1 → DA | Retro | nxc, certipy, impacket getTGT | Guest RID brute → trainee:trainee → machine account BANKING$:banking → certipy req -upn Administrator → pfx → LDAP shell → add to Domain Admins |
| SMB → accdb crack → VBA creds → GenericWrite → RPCMap privesc | RetroTwo | nxc, office2john, hashcat 9600, bloodyAD | staff.accdb → VBA creds (ldapreader) → BloodHound → GenericAll over pre-created computer → RPC EptMapper DLL hijack → SYSTEM |
| GMSA abuse → ADCS ESC4 → ESC1 → DA | Sendai | nxc, bloodyAD, certipy | RID brute → GMSA (MGTSVC$) → gMSADump → ESC4 template mod → ESC1 cert → DA |
| Kerberos enum → WIM hashes → cross-session relay → ESC1 | Shibuya | kerbrute, impacket, socat, certipy | Kerberos user enum → machine red:red → WIM image hashes → RemotePotato0 cross-session → certipy ESC1 |
| NFS → ESC8 → Kerberos relay → DA | VulnCicada | nxc, certipy, ntlmrelayx, krbrelayx | NFS share → password image → certipy relay → ESC8 → Kerberos self-relay → machine cert → secretsdump → DA |

## SMB → ACL Abuse → Domain Admin (8 machines)
| Pattern | Machine | Key Tools | Chain |
|---------|---------|-----------|-------|
| LDAP enum → password spray → SeBackup → NTDS.dit → PtH | Baby | nxc, ldapsearch, impacket secretsdump | LDAP users → spray → SeBackupPrivilege → `reg save hklm\sam` → `robocopy /b` NTDS → secretsdump → PtH |
| Password guess → logon scripts → ACL → GPO → DA | BabyTwo | nxc, bloodhound, smbclient, pygpoabuse | Weak passwords → logon script path writable → ACL abuse via PowerView → Set-DomainUserPassword → GPO exploitation |
| Guest → hardcoded creds → WriteProperty → Unconstrained Delegation | Delegate | nxc, bloodyAD, impacket, krbrelayx | Guest SMB → hardcoded creds in file → WriteProperty ACL → resource-based delegation via krbrelayx → DA |
| VeraCrypt → password crack → VyOS → RBCD → DA | Phantom | nxc, hashcat 13722, veracrypt, impacket | SMB email file → base64 PDF → veracrypt container crack → VyOS router creds → RBCD → S4U2Self → DA |
| Lansweeper → guest → GenericAll → package deployment → DA | Sweep | nxc, bloodhound, sshesame, evil-winrm | Guest → Lansweeper Map Credentials → honeypot SSH capture → GenericAll over Lansweeper Admins → package deploy to DC |
| FTP → Keepass → MSSQL → password spray → Constrained Delegation | Redelegate | nxc, keepassxc, john, bloodyAD | FTP anon → Keepass DB crack → MSSQL local login → SID spray → User-Force-Change-Password ACL → Constrained Delegation |
| SMB guest → NTLMv2 capture → kerberoast → silver ticket → MSSQL → SeImpersonate | Breach | nxc, responder, hashcat, impacket | Guest write on SMB → UNC path NTLMv2 capture → crack → kerberoast svc_mssql → silver ticket Administrator → MSSQL xp_cmdshell → SeImpersonate privesc |
| .NET ZIP slip → DLL hijack → kerberoast → RBCD → DA | Bruno | pwntools, nxc, impacket, kerbrute | Custom .NET app extracts ZIP unsafely → Path.Combine zip-slip → DLL placed in app dir → kerberoast svc_scan → creds → DLL hijack RCE → machine account quota → RBCD → admin reset → DA |

## Windows Exploit Chain (9 machines)
| Pattern | Machine | Key Tools | Chain |
|---------|---------|-----------|-------|
| SMTP → LibreOffice macro → RCE → SeImpersonate → Potato exploit | Job | nmap, msfconsole, sendemail, GodPotato | SMTP open → msf macro document → sendemail → RCE as jack.black → IIS write → SeImpersonate → GodPotato → SYSTEM |
| Gitea enum → PAT → ASPX webshell → mRemoteNG → PDF24 LPE | Lock | curl, git, msfvenom, xfreerdp | Gitea API → PAT → git clone → ASPX upload → webshell → mRemoteNG config decrypt → PDF24 LPE → SYSTEM |
| XAMPP → NTLMv2 leak → NTFS junction → SeTcbPrivilege → SYSTEM | Media | responder, hashcat, ssh, mingw-w64 | Windows Media Player UNC → responder capture → crack NTLMv2 → SSH → PHP webshell → NTFS junction + SeTcbPrivilege → SYSTEM |
| FTP → SEH buffer overflow → egghunter → FodHelper UAC bypass | Rainbow | pwntools, msfvenom, nasm, Burp Suite | FTP anon → SEH overflow offset → egghunter + staged shellcode → FodHelper registry UAC bypass → SYSTEM |
| File read → UNC NTLMv2 capture → S4U2self → Velociraptor → SYSTEM | LustrousTwo | kerbrute, responder, impacket-getST, ilspycmd | Arbitrary file read → UNC inject → Net-NTLMv2 → crack → S4U2self delegation → .NET decompile → PowerShell injection → Velociraptor admin → VQL exec |
| FTP → format string + BOF → DPAPI → kernel driver → token steal | Reaper | pwntools, ghidra, ropper, mingw-w64, msfvenom | FTP → format string leak ASLR → BOF offset 88 → ROP → VirtualAlloc → shell → DPAPI decrypt SSH → RDP as admin → kernel driver IOCTL → arbitrary write → token steal → SYSTEM |
| Java deserialization → RMI RCE → .NET crypto → admin | Atlas | java, ysoserial, dotnet, pycryptodome | Spring Boot Castor XML → Java RMI deserialization RCE → reverse engineer .NET WinSSHTerm → AES-256-CBC PBKDF2 decrypt → admin creds |
| Macro phish → hMailServer → SDF db → Veeam → SYSTEM | JobTwo | msfconsole, dotnet, python3 | SMTP macro phish → foothold → hMailServer config → encrypted DB creds → SDF database extract → Veeam Backup exploit → SYSTEM via sqlserver.exe |
| V8 type confusion → WASM shellcode → kernel driver → PTE → token steal | ReaperTwo | pwntools, wabt, ghidra, ropper | SMB dev artifacts → V8 Harmony Set type confusion → WASM shellcode → RCE low-user → kernel driver fptr exec → MSR leak kASLR → stack pivot → ROP → PTE modify → shellcode → SYSTEM |

## C2 Chain (1 lab)
| Pattern | Machine | Key Tools | Chain |
|---------|---------|-----------|-------|
| FTP → Sliver C2 → PrintNightmare → Mimikatz → SSH → Puppet manifest → DC → SharpDPAPI | Puppet | Sliver, PrintNightmare.ps1, Mimikatz, SharpDPAPI, Puppet, ssh2john | FTP anon → Sliver beacon Bruce.Smith → PrintNightmare → SYSTEM → Mimikatz → svc_puppet_win_t1 → SSH → PM01 → sudo puppet → malicious site.pp → DC01 → svc_puppet_win_t0 → Mimikatz → SharpDPAPI DC DPAPI → final flag |
