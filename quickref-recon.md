# Recon / OSINT Quick Reference

```bash
# Port scan
nmap -sV -p- <target>
nmap -sC -sV -p <ports> <target>

# DNS
dig any <domain>
nslookup <domain>
host -t ns <domain>

# Web enumeration
curl -sk https://<target>/robots.txt
gobuster dir -u https://<target> -w wordlist.txt

# OSINT
curl -s "https://web.archive.org/web/timemap/link/<url>"

# SMB
smbclient -L //<target> -N
nxc smb <target> -u '' -p '' --shares
```
