# Sacred-Scrolls-Revenge

**Category:** Pwn | **Difficulty:** Very Easy
**Binary:** `sacred_scrolls` (ELF 64-bit, not stripped)

## Protections

| Protection | Status    |
|-----------|-----------|
| RELRO     | Full      |
| Canary    | Disabled  |
| NX        | Enabled   |
| PIE       | Disabled  (0x400000) |
| RUNPATH   | `./glibc/` |

## Vulnerabilities

### 1. Uninitialized Stack Memory Leak (libc base)

In `main()` at `0x400ee2`, the wizard tag is read into an `alloca(0x600)` buffer that is **never zeroed**:

```c
buf = alloca(0x600);
read(0, buf, 0x5FF);
printf("Interact with magic library %s", buf);
memset(v18, 0, sizeof(v18));  // v18 is a DIFFERENT buffer (200 bytes at rbp-0x100)
```

Sending only 15 `A`s + newline fills 16 bytes of the 1536-byte buffer. The rest remains uninitialized stack data, which `printf("%s", buf)` leaks as a null-terminated string. The leaked 6 bytes after the input reveal the address of the `/bin/sh` string in libc (`libc + 0x1d8698`), giving a full libc base leak.

### 2. Stack Buffer Overflow in `spell_save()` (CVE-worthy)

In `spell_save()` at `0x400ea3`:

```c
char dest[32];                      // at rbp - 0x20
memcpy(dest, buf, 0x258);          // copies 600 bytes into 32-byte buffer
```

**Offset to return address:** `0x20` (dest) + `0x08` (saved rbp) = **`0x28` (40 bytes)**.

## Exploit Flow

### Step 1 — Leak libc

Send 15 `A`s as the wizard tag. Parse the 6 bytes leaked immediately after the echoed input to recover the libc base address.

```
Input:  AAAAAAAAAAAAAAA\n
Leaked: AAAAAAAAAAAAAAA\nXXXXXXXXXX...  (X = stack garbage containing libc addr)
Leak = u64(leak_bytes[16:22].ljust(8, b'\x00'))
libc.address = leak - 0x1d8698
```

### Step 2 — Build ROP chain (ret2libc)

The NX bit prevents shellcode execution, so we use a `ret2libc` ROP chain:

```
ret (alignment) → pop rdi; ret → "/bin/sh" → system()
```

- `ret` gadget: `0x4007ce` (stack alignment for movaps issue)
- `pop rdi; ret` gadget: `0x4011b3` (unaligned decode of `pop r15; ret` in `__libc_csu_init`)
- `/bin/sh` and `system()` resolved from leaked libc base

### Step 3 — Upload via spell_upload()

The binary accepts base64-encoded zip input. Create `spell.txt` with:

```
| magic signature (7B) | padding (33B) | ROP chain (32B) |
| 0xf09f9193e29aa1     | AAAA...AAAA   | ret, pop rdi, /bin/sh, system |
```

**Total: 72 bytes** (well within the 200-byte buffer).

Critical: the base64 output must not contain `/` (the binary's character filter rejects it). The exploit retries with a new process if `/` appears.

Zip `spell.txt` → base64 encode → send via menu option 1.

### Step 4 — Trigger via spell_read() → spell_save()

- **Option 2** (`spell_read`): Unzips the uploaded zip, validates the 7-byte magic signature (`\xf0\x9f\x91\x93\xe2\x9a\xa1`), loads `spell.txt` contents into the buffer.
- **Option 3** (`spell_save`): `memcpy(dest, buf, 0x258)` overflows the 32-byte stack buffer, overwriting the saved return address with our ROP chain. When `spell_save` returns, control flows to our ROP chain → shell.

## Local Test Result

**Pass** — shell obtained, flag captured.

```
FLAG: HTB{f4k3_fl4g_4_t35t1ng}
```

## Key Techniques

| Technique | Purpose |
|-----------|---------|
| Uninitialized stack leak | Recover libc base address |
| Base64 zip upload | Bypass input character restrictions |
| ret2libc ROP | Call `system("/bin/sh")` despite NX |
| Stack alignment (`ret` gadget) | Fix movaps alignment crash in `system()` |
