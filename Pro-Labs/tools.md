# Pro-Labs Tool Inventory
Read this file on demand when you need tool install commands or tool→machine mappings.

## Tool Categories

### AD & Windows Enumeration
| Tool | Machines | macOS | Linux | Install |
|------|----------|-------|-------|---------|
| nxc/netexec | Baby/BabyTwo/Delegate/Job/Lock/Media/Phantom/RetroTwo/Sendai/Shibuya/Sweep/VulnCicada | Y | Y | `pip install netexec` |
| impacket secretsdump | Baby/Delegate/Redelegate/Shibuya/VulnCicada | Y | Y | `pip install impacket` |
| impacket smbclient | Delegate/LustrousTwo/RetroTwo/Shibuya | Y | Y | `pip install impacket` |
| impacket GetUserSPNs | Delegate | Y | Y | `pip install impacket` |
| impacket getTGT/getST | Delegate/LustrousTwo/Phantom/Redelegate | Y | Y | `pip install impacket` |
| impacket addcomputer | Delegate | Y | Y | `pip install impacket` |
| impacket psexec/smbexec | VulnCicada/Shibuya | Y | Y | `pip install impacket` |
| impacket rbcd | Phantom | Y | Y | `pip install impacket` |
| bloodhound-python | BabyTwo/Delegate/LustrousTwo/Phantom/Redelegate/RetroTwo/Sendai/Sweep | Y | Y | `pip install bloodhound` |
| bloodyAD | Delegate/Redelegate/RetroTwo/Sendai/VulnCicada | Y | Y | `pip install bloodyAD` |
| evil-winrm | Baby/Delegate/Redelegate/Sendai/Sweep | Y | Y | `gem install evil-winrm` |
| kerbrute | LustrousTwo/Shibuya | Y | Y | Go binary, brew/apt |
| ldapsearch | Baby | Y | Y | `brew install ldap-utils` / `apt install ldap-utils` |
| smbclient | BabyTwo/Sendai | Y | Y | `brew install samba` / `apt install smbclient` |

### AD & Windows Exploitation
| Tool | Machines | macOS | Linux | Install |
|------|----------|-------|-------|---------|
| certipy | Retro/Sendai/Shibuya/VulnCicada | Y | Y | `pip install certipy-ad` |
| responder | LustrousTwo/Media | Y | Y | `pip install responder` |
| krbrelayx (dnstool.py, addspn.py) | Delegate | Y | Y | `git clone https://github.com/dirkjanm/krbrelayx` |
| ntlmrelayx | VulnCicada | Y | Y | `pip install impacket` |
| ntpdate | Phantom/Shibuya/VulnCicada | Y | Y | `brew install ntp` / `apt install ntpdate` |
| xfreerdp | Lock/LustrousTwo/RetroTwo/VulnEscape | Y | Y | `brew install freerdp` / `apt install freerdp2-x11` |

### Windows Target-Side Tools (deployed to target)
| Tool | Machines | Type | Notes |
|------|----------|------|-------|
| RunasCs.exe | VulnEscape | EXE | Serve via HTTP; target downloads. Blocked on M2 — BPV needed to get the password for this step |
| GodPotato / GodPotato-NET4.exe | Job/Media | EXE | SeImpersonate privilege escalation |
| FullPowers.exe | Media | EXE | Token duplication |
| TcbElevation-x64.exe | Media | EXE | SeTcbPrivilege escalation |
| RemotePotato0.exe | Shibuya | EXE | Cross-session relay |
| Perfusion.exe | RetroTwo | EXE | Registry key privesc |
| RemoteKrbRelay.exe | VulnCicada | EXE | Kerberos relay |
| SetOpLock.exe | Lock | EXE | Oplock for msiexec escalation |
| nc64.exe | VulnEscape | EXE | Netcat for Windows |

### Linux PrivEsc / Pivot
| Tool | Machines | macOS | Linux | Install |
|------|----------|-------|-------|---------|
| sshpass | Down/Reset/Forgotten/Race | Y | Y | `brew install hudochenkov/sshpass/sshpass` / `apt install sshpass` |
| tmux | Reset | Y | Y | `brew install tmux` / `apt install tmux` |
| socat | Puppet/Shibuya | Y | Y | `brew install socat` / `apt install socat` |
| chisel | Build | Y | Y | `go install github.com/jpillora/chisel@latest` |
| proxychains | Bamboo/Build/Shibuya | Y | Y | `brew install proxychains-ng` / `apt install proxychains4` |
| pspy | Dump/Race/Ten/Watcher/Zero/Bamboo | Y | Y | `wget https://github.com/DominicBreuker/pspy/releases/...` |
| linpeas | Bamboo | Y | Y | `curl -L https://github.com/peass-ng/PEASS-ng/releases/...` |
| tcpdump | Dump | Y | Y | Built-in macOS / `apt install tcpdump` |

### Web Exploitation Tools
| Tool | Machines | macOS | Linux | Install |
|------|----------|-------|-------|---------|
| Burp Suite | Bamboo/Rainbow | Y | Y | Download from portswigger.net |
| chromedriver | Store | Y | Y | `brew install chromedriver` / `apt install chromium-chromedriver` |
| wabt (wat2wasm) | ReaperTwo | Y | Y | `brew install wabt` / `apt install wabt` |
| ffuf | Watcher | Y | Y | `brew install ffuf` / `apt install ffuf` |
| feroxbuster | Race/Zero | Y | Y | `brew install feroxbuster` / `apt install feroxbuster` |
| wfuzz | Ten/Zero | Y | Y | `pip install wfuzz` |
| squidscan | Bamboo | Y | Y | `go install github.com/...` |

### Database Tools
| Tool | Machines | macOS | Linux | Install |
|------|----------|-------|-------|---------|
| psql | Slonik | Y | Y | `brew install libpq` / `apt install postgresql-client` |
| pg_basebackup | Slonik | Y | Y | Ships with libpq / postgresql-client |
| mysql/mariadb | Build | Y | Y | `brew install mysql` / `apt install mariadb-client` |

### Password Cracking
| Tool | Mode/Hash | Machines | Install |
|------|-----------|----------|---------|
| john | SSH keys, NT, netntlmv2 | Build/Delegate/LustrousTwo/Redelegate/Shibuya | `brew install john` / `apt install john` |
| hashcat -m 9600 | MS Access .accdb | RetroTwo | `brew install hashcat` / `apt install hashcat` |
| hashcat -m 10900 | Grafana PBKDF2 | Data | `brew install hashcat` / `apt install hashcat` |
| hashcat -m 13722 | VeraCrypt | Phantom | `brew install hashcat` / `apt install hashcat` |
| crunch | Wordlist generation | Phantom | `brew install crunch` / `apt install crunch` |
| office2john | Office docs | RetroTwo | Ships with john |
| ssh2john | SSH keys | Puppet | Ships with john |
| keepass2john | Keepass databases | Redelegate | Ships with john |

### Binary Exploitation / Reverse Engineering
| Tool | Machines | macOS | Linux | Install |
|------|----------|-------|-------|---------|
| pwntools | Rainbow/Reaper | Y | Y | `pip install pwntools` |
| msfvenom | Job/Lock/Rainbow/Reaper | Y | Y | `brew install metasploit` / `apt install metasploit-framework` |
| msfconsole | Job/Lock/Redelegate | Y | Y | `brew install metasploit` / `apt install metasploit-framework` |
| ghidra | Reaper | Y | Y | Download from ghidra-sre.org |
| ropper | Reaper | Y | Y | `pip install ropper` |
| nasm | Rainbow | Y | Y | `brew install nasm` / `apt install nasm` |
| mingw-w64 | Media/Reaper | P | Y | `brew install mingw-w64` / `apt install mingw-w64` |
| ilspycmd | Atlas/LustrousTwo | Y | Y | `dotnet tool install ilspycmd -g` |
| winchecksec | Reaper | P | Y | `pip install winchecksec` (partial) |
| Java (OpenJDK) | Atlas/Manage | Y | Y | `brew install openjdk` / `apt install default-jdk` |
| ysoserial | Atlas | Y | Y | `git clone https://github.com/frohoff/ysoserial` (Java, cross-platform) |
| dotnet-sdk | Atlas/JobTwo | Y | Y | `brew install dotnet` / `apt install dotnet-sdk-8.0` |

### Crypto Challenges
| Tool | Challenge | Install |
|------|-----------|---------|
| python3 + pwntools | Hidden-Handshake, Kewiri, MadMath | `pip install pwntools` |
| python3 + sympy | MadMath (RSA modulus recovery) | `pip install sympy` |
| python3 + pycryptodome | MadMath (AES decryption) | `pip install pycryptodome` |

### C2 / Post-Exploitation Framework (Puppet Chain)
| Tool | Platform | Notes |
|------|----------|-------|
| Sliver client | Linux binary only | Server + client; multiplayer mode via FTP config |
| Mimikatz | Windows EXE | Deployed via Sliver sideload |
| SharpDPAPI | Windows .NET | DPAPI blob extraction |
| SspiUacBypass | BOF/COFF | Compiled via make, loaded into Sliver |
| PrintNightmare PoC (CVE-2021-34527.ps1) | PowerShell script | Deployed via Sliver upload |
| PrivescCheck.ps1 | PowerShell script | Audit script, deployed via Sliver |

### Monitoring / Process Detection (Linux targets)
| Tool | Install |
|------|---------|
| pspy64 | `wget https://github.com/DominicBreuker/pspy/releases/download/v1.2.1/pspy64` |
| linpeas.sh | `curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh` |

## macOS Homebrew Bundle (install all at once)
```bash
brew install nmap hashcat john tmux freerdp socat proxychains-ng ffuf feroxbuster \
  nasm mingw-w64 crunch ntp ldap-utils coreutils wabt chromedriver \
  openjdk dotnet libpq
pip install netexec certipy-ad impacket bloodhound bloodyAD responder pwntools \
  wfuzz ropper sympy pycryptodome selenium
gem install evil-winrm
```

## Kali/ Linux apt Bundle
```bash
# Core tools
apt install nmap hashcat john tmux freerdp2-x11 socat proxychains4 ffuf \
  feroxbuster nasm mingw-w64 crunch ntpdate ldap-utils metasploit-framework \
  wabt chromium-driver default-jdk postgresql-client wine

# dotnet-sdk-8.0 requires Microsoft repo (not in default apt)
# wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb
# dpkg -i packages-microsoft-prod.deb && apt update && apt install dotnet-sdk-8.0

pip install netexec certipy-ad impacket bloodhound bloodyAD responder pwntools \
  wfuzz ropper sympy pycryptodome selenium
gem install evil-winrm
```
