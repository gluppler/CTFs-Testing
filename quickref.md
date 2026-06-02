# quickref.md — One-liner Commands

## Pwn
```bash
# Binary analysis
checksec --file=binary && file binary
objdump -d binary | grep '<main>:' -A100
strings -t x binary | grep -i 'flag\|win\|shell\|cat'

# Pattern offset
python3 -c "from pwn import *; print(cyclic(200))"
python3 -c "from pwn import *; print(cyclic_find(0x61616164))"

# Run with bundled glibc
python3 -c "from pwn import *; p=process(['./glibc/ld-linux-x86-64.so.2','--library-path','./glibc/','./binary'],cwd='challenge'); p.interactive()"

# Find gadgets
ROPgadget --binary binary | grep -E 'pop rdi|ret'

# PDF text extraction
pdftotext challenge.pdf challenge.txt && grep -i 'vuln\|exploit\|overflow' challenge.txt
```

## Recon
```bash
nmap -sV -p- <target>
curl -sk https://<target>/ | head -50
curl -skL http://<target>:<port>/
```

## AD/Windows
```bash
nxc smb <domain> -u Guest -p "" --shares --rid-brute 1200
responder -I tun0 -v
xfreerdp3 /v:<target> /u:<user> /p:<pass> /dynamic-resolution +clipboard
```

## Cracking
```bash
john --wordlist=rockyou.txt hash.txt
hashcat -m 10900 hash.txt /usr/share/wordlists/rockyou.txt
```

## Web
```bash
ffuf -u https://<target>/FUZZ -w wordlist.txt
feroxbuster -u https://<target> -w wordlist.txt
```

## Setup
```bash
source /home/gluppler/Downloads/CTFs-Testing/.pathrc
python3 -m venv .venv && source .venv/bin/activate
```
