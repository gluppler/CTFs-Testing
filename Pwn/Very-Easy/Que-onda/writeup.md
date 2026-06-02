# Que-onda — Very Easy Pwn

## Vulnerability
None. This is a **warm-up connection challenge** — no memory corruption, no exploit needed.

## Binary Analysis
```
$ file que_onda
ELF 64-bit LSB pie executable, x86-64, not stripped

$ checksec
Arch:    amd64-64-little
RELRO:   Full RELRO
Stack:   Canary found
NX:      NX enabled
PIE:     PIE enabled
```

### Flow
1. `main()` calls `banner()`
2. `banner()` prints a random ANSI-colored greeting, clears screen, then prompts:
   ```
   Hola mi Amigos! Send me the string "flag"
   ```
3. `read(0, buf, 6)` reads up to 6 bytes from stdin
4. `strncmp(buf, "flag", 4)` checks first 4 bytes
5. If match → `read_flag()` opens `./flag.txt` and prints it byte by byte
6. If no match → `error()` prints `Que??`

### Key strings (from `.rodata`)
- `0x22a2`: `"flag"` (comparison target)
- `0x2033`: `"./flag.txt"` (file to read)
- `0x22a7`: `"Que??"` (error message)

## Exploit
Simply send `"flag\n"` — the program reads 6 bytes, matches first 4 against `"flag"`, and dumps the flag.

```
from pwn import *
p = remote('127.0.0.1', 1337)
p.recvuntil(b'"flag"')
p.sendline(b'flag')
print(p.recvall().decode())
```

## Local Test
```
$ python3 exploit.py
HTB{f4ke_fl4g_4_t35t1ng}
```

## Flag
`HTB{f4ke_fl4g_4_t35t1ng}` (local placeholder — real flag from remote instance)
