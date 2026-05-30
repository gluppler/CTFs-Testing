# Pro-Labs Wiki

## Machines (Standalone)
| Machine | OS | Difficulty | Pattern | Flags |
|---------|-----|-----------|---------|-------|
| [Down](Machines/Down/) | Linux | Easy | SSRF→RCE→decrypt→sudo | User/root in `writeup.md` |
| [Retro](Machines/Retro/) | Windows | Easy | SMB→ADCS ESC1→cert→DA | User/root in `flags.txt` |
| [Data](Machines/Data/) | Linux | Easy | Grafana LFI→hash crack→docker priv | User/root in `writeup.md` |
| [Reset](Machines/Reset/) | Linux | Easy | Password reset→SSH→tmux+nano GTFOBins | `19ba...` / `7ad6...` |
| [VulnEscape](Machines/VulnEscape/) | Windows | Easy | RDP→kiosk→RunasCs→UAC bypass | `7acb...` / `44be...` |
| [Manage](Machines/Manage/) | Linux | Easy | JMX→RCE→backup leak→2FA bypass→sudo adduser | `a86d...` / `b364...` |
| [Forgotten](Machines/Forgotten/) | Linux | Easy | SSH creds→webshell on mount→container sudo→setuid bash | `2ec0...` / `ecbf...` |
| [Atlas](Machines/Atlas/) | Windows | Hard | Java Castor XML deserialization→RMI RCE→.NET WinSSHTerm crypto | writeup PDF |
| [Breach](Machines/Breach/) | Windows | Medium | SMB guest→NTLMv2→kerberoast→silver ticket→MSSQL→SeImpersonate | writeup PDF |
| [Bruno](Machines/Bruno/) | Windows | Medium | .NET ZIP slip→DLL hijack→kerberoast→RBCD→DA | writeup PDF |
| [Dump](Machines/Dump/) | Linux | Hard | PHP cmd injection→tcpdump→AppArmor→motd→root | writeup PDF |
| [JobTwo](Machines/JobTwo/) | Windows | Hard | Macro phish→hMailServer→SDF db→Veeam→SYSTEM | writeup PDF |
| [ReaperTwo](Machines/ReaperTwo/) | Windows | Insane | V8 type confusion→WASM→kernel driver→PTE→token steal | writeup PDF |
| [Slonik](Machines/Slonik/) | Linux | Medium | NFS→UID trust→PostgreSQL→pg_basebackup→root | writeup PDF |
| [Store](Machines/Store/) | Linux | Hard | Node.js file read→inspector→ChromeDriver→root | writeup PDF |

## Pro-Lab Chains
| Lab | Status | Pattern |
|-----|--------|---------|
| [Puppet](Puppet/) | Complete | C2→PrintNightmare→mimikatz→lateral→puppet manifest→DC root |
| Mythical | Not started | — |

## Technique Pages (Key Patterns)
| Pattern | Where Used | Details |
|---------|-----------|---------|
| SSRF File Read (protocol bypass) | Down | `log.md#Down` |
| escapeshellcmd nc injection | Down | `log.md#Down` |
| ADCS ESC1 (certificate impersonation) | Retro | `log.md#Retro` |
| Pre-created machine account exploitation | Retro | `log.md#Retro` |
| LDAP shell privilege escalation | Retro | `log.md#Retro` |
| PrintNightmare LPE | Puppet | `log.md#Puppet` |
| Sliver C2 operations | Puppet | `log.md#Puppet` |
| SspiUacBypass (SSPI UAC bypass BOF) | Puppet | `log.md#Puppet` |
| Puppet manifest exploitation (site.pp exec) | Puppet | `log.md#Puppet` |
| SharpDPAPI machinetriage (DPAPI credential extraction) | Puppet | `log.md#Puppet` |
| JMX RCE via beanshooter | Manage | `log.md#Manage` |
| Backup archive lateral movement | Manage | `log.md#Manage` |
| sudo adduser → admin group root | Manage | `log.md#Manage` |
| Docker mount → setuid bash → root | Forgotten | `log.md#Forgotten` |
