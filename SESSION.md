# SESSION.md — 2026-06-03

## Completed
- Solved all 19 Very-Easy Pwn challenges (local + remote)
- Exploits covered: ret2win, ret2shellcode, format strings, BOF (off-by-one, canary bypass, null-byte overwrite, 1-byte ret), integer overflow, type confusion, uninitialized leaks, ret2libc, Q&A, ZIP upload RCE
- Set up tooling: pwntools, Python3, objdump, checksec
- Automated with subagents for batch solving (13 in parallel)

## Key Files
- `/home/gluppler/Downloads/CTFs-Testing/Pwn/Very-Easy/*/exploit.py` — 19 working exploits
- `/home/gluppler/Downloads/CTFs-Testing/Pwn/Very-Easy/*/writeup.md` — 19 writeups
- `/home/gluppler/Downloads/CTFs-Testing/Pwn/Very-Easy/*/flag.txt` — 19 captured flags

## State
- Pwn Very-Easy: 19/19 ✅
- Pwn Easy: 0/N
- Crypto, Forensics, Web, Misc, OSINT, Reverse, Malware, AI-ML: not started

## Patterns Learned
- Always check NX/canary/PIE first — shapes exploit approach
- Format strings: `%N$p` leaks, `%hn` writes
- ret2libc: need stack alignment `ret` gadget before `system()`
- Multi-stage exploits: leak PIE → leak libc → ret2libc (Sacred-Scrolls, Retribution)
- Web delivery: some challenges use HTTP POST instead of raw TCP (El-Pipo)
- ZIP upload challenges: use `-j` flag to strip paths, check for `/` in payload
- glibc mismatch: use local libc offsets — remote often matches the bundled libc

## Next Targets
- Pwn Easy challenges
- Or other categories (Web, Crypto, Forensics)
