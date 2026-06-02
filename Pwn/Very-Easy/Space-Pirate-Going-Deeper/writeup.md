# Space Pirate: Going Deeper - Writeup

## Challenge Info
- **Name**: Space Pirate: Going Deeper
- **Difficulty**: Very Easy
- **Category**: Pwn
- **Author**: w3th4nds

## Vulnerability
**1-byte return address overwrite** via buffer overflow. The `admin_panel()` function reads 0x39 (57) bytes into a buffer at `rbp-0x30` (48 bytes from saved RBP). This gives 1 byte of overflow past the saved RBP, overwriting the LSB of the return address.

## Binary Protections
| Protection | Enabled |
|-----------|---------|
| Canary    | No      |
| NX        | Yes     |
| PIE       | No      |
| RELRO     | Full    |

## Exploit Approach

1. **Target**: The `system("cat flag*")` call at `0x400b12` inside `admin_panel()`
2. **Return address leak**: None needed. PIE is disabled, all addresses are known
3. **Overflow**: The return address from `admin_panel` back to `main` is `0x400b94`. Changing its LSB to `0x12` redirects execution to `0x400b12` — directly to the instruction that calls `system("cat flag*")`

**Payload**: 56 bytes of padding + `\x12`

```
Buffer (rbp-0x30)    48 bytes padding
local_10 (rbp-0x08)   8 bytes padding
saved RBP              8 bytes padding → overwritten (56 total)
return address LSB     1 byte → 0x12  (0x400b94 → 0x400b12)
                      ─────────
                      57 bytes (0x39)
```

## Solution Steps
1. Select option 2 (Login) from menu
2. Send 56 junk bytes + `\x12` as the username
3. `admin_panel` returns to `0x400b12` which executes `system("cat flag*")`

## Flag
`HTB{f4k3_fl4g_4_t35t1ng}`
