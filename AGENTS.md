# AGENTS.md

## Core Principles
- **Token-aware**: AGENTS.md stays compact. Companion files (tools.md/platforms.md/patterns.md/strategy.md) read on demand.
- **Curiosity-first**: Explore before exploit. Understand before automate. The pipeline is the record, not the strategy.
- **Blackbox-first**: Assume zero intel on every new target. You build the knowledge — you don't consume someone else's. Writeups are optional accelerators, not the strategy.
- **Automation-first**: pipeline.sh is primary artifact. Manual commands only for bootstrapping. Every solve step → pipeline.
- **Compaction**: Compact at 2 challenges / 50 calls. Move technique details to log.md, concepts to index.md.
- **Outcome-first**: Describe target result, not every step.

## The Curiosity Mindset
**Phase 0 questions before any tool:**
- What's weird? (unusual port, service, header, response, behavior)
- What's the least expected entry point?
- What happens when I do the WRONG thing?
- What would an auditor miss?

**Lateral triggers (when stuck):**
- Check backup/archive/.git/.env/config/temp files in every accessible dir
- Try the opposite of what the challenge seems to want
- Look for race windows, side channels, temp file shenanigans
- Re-read your enumeration output — what did you skip? What looked like noise?
- Check for hidden params, debug endpoints, dev routes on every web surface
- Test privilege boundaries: what's exposed that shouldn't be?

**"What Else" gate — before committing to any path:**
- Enumerate 3+ alternative interpretations of each finding
- For each open port/service, ask: "What else could this mean?"
- If automation fails, explore manually first before fixing script

## Workflow (5-step)
1. **Explore** — nmap recon, curiosity questions, no assumptions, no writeups
2. **Catalog** — Check index.md + log.md for similar patterns from past solves, run pipeline.sh, collect all enumeration data
3. **Gate** — List all possible paths, rank by weirdness + likelihood
4. **Solve** — Execute chosen path, script everything, pipeline integration
5. **Capture** — Write writeup, update pipeline, wiki index+log, AGENTS patterns

## Tool Inventory (compact)
| Cat | Tool | M2 | Lin | Install |
|-----|------|----|-----|---------|
| Recon | nmap, curl, python3 | Y | Y | brew/apt/builtin |
| AD | nxc, impacket, certipy | Y | Y | pip |
| AD | bloodhound-py, bloodyAD | Y | Y | pip |
| AD | evil-winrm, ldapsearch | Y | Y | gem/apt |
| AD | kerbrute | Y | Y | go |
| Win | xfreerdp, responder | Y | Y | brew/apt/pip |
| Crack | john, hashcat | Y | Y | brew/apt |
| Linux | sshpass, tmux, socat | Y | Y | brew/apt |
| Linux | chisel, proxychains, pspy | Y | Y | go/apt/dl |
| Web | ffuf, feroxbuster, wfuzz | Y | Y | brew/apt/pip |
| Pwn | pwntools, msf, ghidra | Y | Y | pip/apt/dl |
| Pwn | mingw-w64 cross-compiler | P | Y | brew/apt |
| Crypto | sympy, pycryptodome | Y | Y | pip |
| DB | psql, pg_basebackup, etcdctl | Y | Y | brew libpq / apt |
| Mail | swaks | Y | Y | brew/apt |
| Browser | wabt, chromedriver | Y | Y | brew |
| Chain | Sliver client | N | Y | binary (bin/linux/) |
| Chain | c2 helper | Y | Y | Rust build (tools/c2/) |
| Chain | ysoserial | Y | Y | Java jar (bin/linux/) |
| Chain | ilspycmd | Y | Y | dotnet tool --global |
| Chain | Mimikatz/SharpDPAPI | P | P | win exe/target |

## Platform Matrix (Y/P/N — pure M2, no VMs/Wine)
**Solved (7):** Down(L,Y,Y) Data(L,Y,Y) Retro(W,Y,Y) Reset(L,Y,Y) Manage(L,Y,Y) Forgotten(L,Y,Y) Puppet(W,C,N,Y)
**Solved (blocked):** VulnEscape(W,N,Y) — BPV Windows-only password decryption
**Unsolved (solvable):** Baby(W,E,Y,Y) BabyTwo(W,M,Y,Y) RetroTwo(W,E,Y,Y) Lock(W,E,Y,Y) Build(L,E,Y,Y) Delegate(W,M,Y,Y) Job(W,M,Y,Y) Media(W,M,Y,Y) Bamboo(L,M,Y,Y) Phantom(W,M,Y,Y) Sendai(W,M,Y,Y) Shibuya(W,M,Y,Y) Sweep(W,M,Y,Y) VulnCicada(W,M,Y,Y) Watcher(L,M,Y,Y) Breach(W,M,Y,Y) Bruno(W,M,Y,Y) Slonik(L,M,Y,Y) LustrousTwo(W,H,Y,Y) Race(L,H,Y,Y) Redelegate(W,H,Y,Y) Rainbow(W,M,Y,Y) Ten(L,H,Y,Y) Zero(L,I,Y,Y) Atlas(W,H,Y,Y) Dump(L,H,Y,Y) JobTwo(W,H,Y,Y) Store(L,H,Y,Y)
**Unsolved (blocked):** Reaper(W,I,N,P) (kernel exploit needs Windows VM + WinDbg), ReaperTwo(W,I,N,P) (browser + kernel exploit, kernel stage same blocker)
**Chain:** Mythical(?,?,?) (not started)

## Machine Strategy Tiers
- **Tier 1 (Easy/fast)**: Baby, BabyTwo, RetroTwo, Lock, Build
- **Tier 2 (Medium AD/Web)**: Delegate, Job, Media, Bamboo, Phantom, Sendai, Shibuya, Sweep, VulnCicada, Watcher, Breach, Bruno, Slonik
- **Tier 3 (Hard)**: LustrousTwo, Redelegate, Race, Ten, Atlas, Dump, JobTwo, Store
- **Tier 4 (Specialized)**: Rainbow (SEH BOF), Zero (htaccess/Apache cron), Reaper (kernel driver), ReaperTwo (V8 + kernel)
- **Chain**: Puppet (solved, writeup exists), Mythical (not started)

## Non-Negotiable Rules
1. Never use system temp dirs — all artifacts in category directory
2. **Wiki first** — check index.md + log.md for patterns from past solves before starting. This is your accumulated knowledge. Add to it after every solve.
3. **No writeup dependency** — writeups are optional accelerators for existing challenges. Never assume one exists for a new target. The wiki + patterns.md are your knowledge base, built from your own solves.
4. Writeup required post-solve (also update pipeline, wiki, AGENTS per rule 13)
5. Cleanup — kill processes, clean artifacts between attempts
6. Scripts at all costs — pipeline.sh / phase scripts are PRIMARY
7. NXC output is STDERR — use `2>&1` not `2>/dev/null`, grep `\[+]` not `\[\+\]`
8. SSH quoting: `$pass` not `'$pass'`; wildcards need `bash -c`; `2>/dev/null` inside sudo breaks `sudo -S` stdin
9. Docker FS: `cat /root/root*` reads container FS; `mount /dev/sda1 /tmp/h` for host files
10. Every fix verified against ALL machines before considered done
11. Post-solve: writeup → pipeline → wiki index+log → AGENTS patterns table
12. Token-aware: read companion files on demand, don't bloat context

## Platform Directory Organization
```
Pro-Labs/bin/
├── macos/               # macOS ARM64 host binaries (c2)
└── linux/               # Linux x86_64 host binaries
    ├── c2               # Sliver tmux helper (compiled from Puppet/tools/c2/)
    ├── sliver-client    # C2 framework binary
    └── ysoserial-all.jar  # Java deserialization toolkit
Pro-Labs/Puppet/
├── c2                   # Platform-detecting shim → bin/{macos,linux}/c2
├── c2-*                 # Sliver automation scripts (cross-platform bash)
├── payloads/            # Windows artifacts deployed TO targets
│   ├── beacon_launcher.dll, bl_renamed.dll, payload.dll
│   ├── uac_bypass.exe, mimikatz.exe, mimikatz_temp/
│   ├── CVE-2021-1675.ps1, CVE-2021-34527.ps1, getkeys.ps1
│   ├── check.bat, rp.bat, run_pp.bat
│   └── BANKING$.ccache
├── source/              # Buildable source (UAC-BOF-Bonanza, PrivescCheck, CVE-2021-34527)
├── tools/c2/            # Rust source for c2 helper (builds on any platform)
└── docs/                # Writeups, flags, notes, sliver cheatsheet
```

## PATH Setup (Arch Linux)
```bash
export PATH="$PATH:/home/gluppler/.dotnet/tools:/home/gluppler/Downloads/CTFs-Testing/Pro-Labs/bin/linux"
```

## Reference File Index (read on demand, NOT auto-loaded)
```
Pro-Labs/tools.md       — Full tool inventory, categories, install commands per platform
Pro-Labs/platforms.md   — Per-machine Y/P/N breakdown with rationale + notes
Pro-Labs/patterns.md    — Attack patterns from all solved + unsolved machines (compiled from our solves)
Pro-Labs/strategy.md    — Per-machine notes, attack sequences, common pitfalls (compiled from our solves)
AGENTS.md               — This file: core principles, platform org, tool audit, quick reference
```

## Installed Tool Audit (Arch Linux, Pro-Labs ready)
| Status | Tool | Machine(s) | Install |
|--------|------|-----------|---------|
| ✅ | nmap, curl, python3, john, hashcat | all | pacman/pip |
| ✅ | nxc, impacket, certipy, bloodhound, bloodyAD, evil-winrm | Baby→VulnCicada | pip (venv) |
| ✅ | kerbrute, ldapsearch, smbclient | Baby→Shibuya | yay/pacman |
| ✅ | xfreerdp3, responder | Lock→VulnEscape | pacman @ /usr/bin/xfreerdp3 |
| ✅ | sshpass, tmux, socat, chisel, proxychains, pspy | Build→Watcher | pacman/yay |
| ✅ | ffuf, feroxbuster, wfuzz, gobuster, squidscan | web targets | yay/pip |
| ✅ | pwntools, msfconsole/venom, ghidra, nasm, mingw-w64 | Rainbow→Reaper | pip/pacman |
| ✅ | psql, pg_basebackup, mysql, etcdctl | Slonik→Ten | pacman |
| ✅ | Java (26), maven, dotnet-sdk (10.0) | Atlas→JobTwo | pacman |
| ✅ | ilspycmd, ysoserial-all.jar, swaks | Atlas→Job | dotnet/dl/pacman |
| ✅ | crunch, wabt, chromedriver, keepassxc, tcpdump | Phantom→Store | pacman/yay |
| ✅ | Sliver client, c2 (Linux build) | Puppet | bin/linux/ |
| 🚫 | ropper | Reaper | blocked on Python 3.14 |
| 🔲 | rockyou.txt | cracking | download when needed |

## Quick Reference
```
nmap -sV -p- <target>
curl -sk https://<target>/ | head -50
curl -skL http://<target>:<port>/ | tr '[:upper:]' '[:lower:]'  # case-fold web body
nxc smb <domain> -u Guest -p "" --shares --rid-brute 1200
python3 -m venv .venv && source .venv/bin/activate
pip install netexec certipy-ad impacket bloodhound-py bloodyAD
responder -I tun0 -v
java -jar beanshooter.jar tonka exec <target> 2222 "<cmd>"
hashcat -m 10900 hash.txt /usr/share/wordlists/rockyou.txt  # Grafana PBKDF2
john --wordlist=rockyou.txt hash.txt                         # SSH/NT/netntlmv2
xfreerdp3 /v:<target> /u:<user> /p:<pass> /dynamic-resolution +clipboard
swaks --to user@domain --from a@b --server <smtp_target> --body "..." --attach exploit.doc
etcdctl --endpoints=http://<target>:2379 get / --prefix
java -jar ysoserial-all.jar CommonsCollections6 'cmd' > payload.bin
```
