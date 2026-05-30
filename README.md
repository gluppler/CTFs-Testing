# CTF Challenges & Pro-Labs Testing

A curated collection of CTF (Capture The Flag) challenge solutions, automation scripts, and documented attack patterns across multiple categories. Designed for self-guided practice, automation-first workflow, and systematic knowledge capture.

## Repository Structure

```
CTFs-Testing/
├── AGENTS.md              # Agent instructions: workflow, curiosity framework, tool matrix
├── llm-wiki.md             # Wiki knowledge management pattern
├── .gitignore
├── Crypto/                 # Cryptography challenge writeups + exploits
│   ├── Very-Easy/          # Hidden-Handshake, Kewiri
│   └── Hard/               # MadMath (RSA modulus recovery)
├── Misc/                   # Miscellaneous challenges
├── Pro-Labs/               # Offensive Security Pro-Labs machines + chains
│   ├── index.md            # Machine catalog
│   ├── log.md              # Action log
│   ├── tools.md            # Full tool inventory per platform
│   ├── platforms.md        # Platform compatibility matrix (M2 Mac / Linux)
│   ├── patterns.md         # Attack patterns from all machines
│   ├── strategy.md         # Per-machine strategy, sequencing, pitfalls
│   ├── Machines/           # 30 standalone machines (Windows + Linux)
│   │   ├── scripts/        # Pipeline automation scripts
│   │   ├── Down/           # (solved) SSRF→RCE→decrypt→sudo
│   │   ├── Retro/          # (solved) SMB→ADCS ESC1→DA
│   │   ├── ...             # 7 solved + 22 unsolved
│   ├── Puppet/             # (solved) Pro-Lab chain: Sliver C2→AD→DC
│   └── Mythical/           # (pending) Pro-Lab chain
├── Pwn/                    # Binary exploitation (empty - future)
├── Reversing/              # Reverse engineering (empty - future)
└── Web/                    # Web exploitation challenge writeups + scripts
    ├── index.md
    ├── log.md
    └── scripts/            # pipeline.sh, jwt-forge, ssti, idor, nosqli, cmd-inject
```

## Approach

This repository follows a **dual-mindset methodology**:

1. **Curiosity-first** — Explore before you exploit. Question assumptions. Look for what's weird, not what's expected.
2. **Automation-first** — Every solved step becomes a script. The pipeline is the primary artifact.

## Platform Support

| Platform | Support | Notes |
|----------|---------|-------|
| **macOS (M1/M2/M3)** | ✅ Y (22/30) | 8 machines require VM/Wine for Windows exploit testing |
| **Linux** | ✅ Y (29/30) | All machines solvable natively |

See `Pro-Labs/platforms.md` for detailed per-machine breakdown.

## Quick Start

```bash
# Clone and set up
git clone <this-repo>
cd CTFs-Testing

# Install tools (pick your platform)
brew install nmap hashcat john tmux freerdp socat ffuf feroxbuster
pip install netexec certipy-ad impacket bloodhound bloodyAD responder pwntools

# Run pipeline against a target
./Pro-Labs/Machines/scripts/pipeline.sh <target_ip>

# Or target a specific machine
cd Pro-Labs/Machines/Reset && cat writeup.md  # start from the writeup
```

## Key Files

| If you want to... | Read this |
|-------------------|-----------|
| Understand the workflow | `AGENTS.md` |
| Find tools for a platform | `Pro-Labs/tools.md` |
| Check if a machine runs on your OS | `Pro-Labs/platforms.md` |
| Recognize attack patterns | `Pro-Labs/patterns.md` |
| Plan a machine attack sequence | `Pro-Labs/strategy.md` |
| See what's been solved | `Pro-Labs/index.md` + `Pro-Labs/log.md` |

## Tool Categories

| Category | Tools |
|----------|-------|
| AD/Windows | nxc, impacket, certipy, bloodhound, bloodyAD, evil-winrm, kerbrute |
| Linux PrivEsc | sshpass, tmux, socat, chisel, proxychains, pspy |
| Web | curl, ffuf, feroxbuster, wfuzz, Burp Suite |
| Cracking | john, hashcat (modes 9600/10900/13722) |
| Pwn | pwntools, metasploit, ghidra, mingw-w64 |
| Crypto | python3 (sympy, pycryptodome) |
| C2 | Sliver, Mimikatz, SharpDPAPI |

## License

For educational purposes only. Challenge content belongs to their respective platforms.
