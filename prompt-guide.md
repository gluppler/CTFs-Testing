# Prompt Guide — CTF Edition

Write prompts like briefing a teammate, not scripting a robot.

## Core: Outcome-First

Describe the goal + constraints, not every step. The agent decides *how*.

```
Goal: [what needs to be true when done]
Constraints: [limits, boundaries, what to avoid]
Stop: [condition that means "done" or "stuck — ask"]
```

## Category Template (unified)

Every CTF category follows the same pattern — only the first pass changes:

```
Goal: Identify the vulnerability and capture the flag.
Stop: Valid flag found. If first pass yields nothing, retry with deeper analysis.
First pass by category:
  Web:     Map endpoints, check auth/injection surfaces, trace data flow
  Pwn:     strings → file → checksec → dynamic analysis
  Reverse: strings → ltrace → disassembly → trace flag logic
  Crypto:  Identify cipher type, gather known/chosen plaintext, test weakness
  Forensics: file type → strings → metadata → binwalk → volatility
  Misc:    Identify constraint system → test boundaries → probe escape
```

## Pro-Labs (multi-machine / AD chains)

```
Goal: Escalate from initial access to Domain Admin / root on all targets.
Strategy: Follow AGENTS.md workflow — Explore → Catalog → Gate → Solve → Capture
Constraints: Script every step into pipeline.sh. Enumerate all credential vectors first. Reference past solve patterns in patterns.md.
Stop per phase: Machine falls into a single solution tier. Move on after capture.
```

## Quick Reference

| Instead of this | Do this | Why |
|---|---|---|
| "Run strings, then file, then objdump..." | "Find the flag. Start with static analysis." | Outcome describes target |
| "Don't brute-force, don't scan all ports" | "Avoid port scans >1000 ports" | Positive constraint, not negative |
| "Keep trying until you find the flag" | "Stop after 3 failed approaches and report" | Clear stopping condition |
| "Use the exploit in /tmp/..." | "Read Pro-Labs/patterns.md for matching attack chain" | Reference existing knowledge |
| "The flag format is HTB{...}" | Include format in success criteria | Explicit success signal |

## Token-Saving Rules

1. **Reference, don't repeat** — say "See AGENTS.md §Curiosity Mindset" not the full text
2. **Use existing data** — check `index.md` + `log.md` before asking for fresh analysis
3. **Output minimal** — return only the flag + 2-line chain summary for solved machines
4. **Prefer tables** over prose when comparing options
