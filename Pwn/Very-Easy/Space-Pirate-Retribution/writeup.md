# Space-Pirate-Retribution

## Summary

Two vulnerabilities in `missile_launcher()`: (1) uninitialized stack leak via `printf("%s", buf)` when few bytes are sent, leaking PIE addresses; (2) buffer overflow — `read(0, buf2, 0x84)` into a smaller buffer, overwriting return address. Chain: leak PIE → leak libc via ROP → ret2libc `system("/bin/sh")`.

## Solution

### Step 1: PIE leak (uninitialized buffer)

`missile_launcher()` reads 31 bytes via `read()` then passes the buffer to `printf("%s[-] Permission Denied!", buf)`. Sending only 1 byte leaves the rest of the buffer with residual stack data containing a PIE return address. The `%s` prints it.

### Step 2: Libc leak + ret2libc

The second `read(0, buf2, 0x84)` overflows 88 bytes to reach the return address. Build a ROP chain: `puts@PLT(GOT_entry)` → return to `main` for a second round, then `ret2libc` with calculated libc base.

```
Offset to saved RBP:  0x50 bytes (32 + 31 + 16 + 1)
Offset to return addr: 0x58 bytes (add 8 for saved RBP)
```

## Flag

```
HTB{...}
```
