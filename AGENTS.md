# AGENTS.md

## Core Principles
- **Token-aware**: This file stays small. Read companion files on demand via aliases below.
- **Wiki-first**: Grep `wiki/` for relevant patterns BEFORE any tool touches a challenge. The wiki IS your accumulated knowledge.
- **Wiki-update**: After every solve, add new techniques to the matching `wiki/<category>.md`. This is non-negotiable.
- **Curiosity-first**: Explore before exploit. Understand before automate.
- **Blackbox-first**: Zero intel assumed. Build knowledge, don't consume someone else's.
- **Automation-first**: Every solve step → script. Manual only for bootstrapping.
- **No /tmp**: All artifacts in challenge/category directory.

## Mandatory Pre-Solve Checklist
Before touching any challenge binary/service:
```bash
grep -rn "<technique>" wiki/          # Check accumulated patterns
cat STATE.md | grep "<challenge>"     # Has this been solved before?
cat SESSION.md                        # What were we doing last session?
```

## Mandatory Post-Solve Checklist
After capturing a flag:
1. Write `writeup.md` in challenge directory
2. Add new technique to `wiki/<category>.md` under the correct keyword
3. Update `STATE.md` with flag + status
4. Update `SESSION.md` if session context changed

## Workflow
1. **Explore** — recon, curiosity questions, no assumptions
2. **Catalog** — grep wiki/ → check STATE.md → check SESSION.md → collect enum data
3. **Gate** — list paths, rank by weirdness + likelihood (consult wiki patterns)
4. **Solve** — execute, script everything
5. **Capture** — writeup, update wiki, update STATE.md, update SESSION.md

## Non-Negotiable Rules
1. Never use system temp dirs — all artifacts in category directory
2. **Wiki grep before every challenge.** No exceptions.
3. **Wiki update after every solve.** No exceptions.
4. Writeup required post-solve
5. Cleanup — kill processes between attempts
6. Every fix verified against ALL machines before considered done
7. NXC output is STDERR: use `2>&1` not `2>/dev/null`, grep `\[+]` not `\[\+\]`
8. SSH quoting: `$pass` not `'$pass'`; wildcards need `bash -c`
9. Token-aware: read companion files on demand, don't bloat context

## File Index (aliases)
| Alias | File | Content |
|-------|------|---------|
| `@state` | STATE.md | All challenge progress across categories |
| `@session` | SESSION.md | Current session context + recent solves |
| `@wiki` | wiki/ | Accumulated LLM knowledge base — grep before solving |
| `@wpwn` | wiki/pwn.md | Pwn techniques + patterns |
| `@wweb` | wiki/web.md | Web techniques + patterns |
| `@wcrypto` | wiki/crypto.md | Crypto techniques + patterns |
| `@wforensic` | wiki/forensics.md | Forensic techniques + patterns |
| `@wrev` | wiki/reverse.md | Reverse engineering techniques |
| `@wmal` | wiki/malware.md | Malware analysis techniques |
| `@wrecon` | wiki/recon.md | Recon/OSINT techniques |
| `@wmisc` | wiki/misc.md | Misc techniques |
| `@qpwn` | quickref-pwn.md | Pwn one-liners |
| `@qweb` | quickref-web.md | Web one-liners |
| `@qforensic` | quickref-forensics.md | Forensics one-liners |
| `@qcrypto` | quickref-crypto.md | Crypto one-liners |
| `@qrev` | quickref-reverse.md | Reverse engineering one-liners |
| `@qmal` | quickref-malware.md | Malware analysis one-liners |
| `@qrecon` | quickref-recon.md | Recon/OSINT one-liners |
| `@qmisc` | quickref-misc.md | Misc one-liners |
| `@tools` | Pro-Labs/tools.md | Full tool inventory + install |
| `@platforms` | Pro-Labs/platforms.md | Per-machine Y/P/N breakdown |
| `@path` | .pathrc | PATH setup for Arch Linux |

## Wiki Structure
```
wiki/
├── index.md      # Master index — grep for "<technique>" to find file
├── pwn.md        # 12 patterns seeded from 19 solves
├── web.md        # (stub)
├── crypto.md     # (stub)
├── forensics.md  # (stub)
├── reverse.md    # (stub)
├── malware.md    # (stub)
├── recon.md      # (stub)
└── misc.md       # (stub)
```

## PATH Setup
```bash
source .pathrc
```
