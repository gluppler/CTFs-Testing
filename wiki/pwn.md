# Pwn Patterns — Accumulated Knowledge

## Categories (for search/grep)
Use `grep -n "<keyword>" wiki/pwn.md` to find relevant patterns before solving.

### ret2win (no PIE)
- **Keyword**: `ret2win`
- **Prereq**: PIE disabled, no canary
- **Approach**: Overflow to known win-function address + `ret` gadget for alignment
- **Used in**: Power-Greed, Getting-Started, Questionnaire

### ret2shellcode (NX disabled)
- **Keyword**: `ret2shellcode`
- **Prereq**: NX disabled (`GNU_STACK RWE`), PIE disabled
- **Approach**: Put shellcode in buffer, overwrite ret addr with `jmp rsp` or `jmp rsi` gadget
- **Used in**: El-Teteo, Regularity
- **Gadgets**: `jmp *rsi` (after `read()`, RSI still points to buffer)
- **Shellcode**: 27-byte `execve("/bin/sh")` from shell-storm

### format string leak (FSB)
- **Keyword**: `format-string` `fsb`
- **Prereq**: `printf(user_input)` or equivalent
- **Approach**: `%N$p` to leak stack values; `%Nx%M$hn` for partial writes
- **Stack offset**: Use `%1$p.%2$p...` to enumerate, find your input with `AAAA`
- **Used in**: racecar, Space-Pirate-Entry-Point

### format string write (%hn)
- **Keyword**: `format-string-write` `%hn`
- **Prereq**: FSB, need to modify a value on stack
- **Approach**: `%<count>x%<offset>$hn` writes 2 bytes at offset
- **Example**: `%4919x%7$hn` writes `0x1337` to offset 7 on stack
- **Used in**: Space-Pirate-Entry-Point

### integer overflow (signed truncation)
- **Keyword**: `integer-overflow` `int32`
- **Prereq**: 64-bit values checked as positive, then added as 32-bit signed
- **Approach**: Two positive `uint64_t` values whose `(int32_t)` sum overflows to negative
- **Example**: `0x7FFFFFFF + 0x7FFFFFFF = 0xFFFFFFFE = -2`
- **Used in**: Mathematricks

### heap address leak → malloc failure
- **Keyword**: `heap-leak` `malloc-fail`
- **Prereq**: Leaked heap address via `%p`, control over `malloc(size)`
- **Approach**: Pass leaked address as size → `malloc(0x7f...)` fails → returns NULL → `buf+size-1` writes zero to leaked address
- **Used in**: Blessing

### canary leak + overflow
- **Keyword**: `canary-leak`
- **Prereq**: Canary enabled, ability to read it (e.g., via format string or printf leak)
- **Approach**: Leak canary, include it in overflow payload to pass `__stack_chk_fail`
- **Used in**: Quack-Quack

### off-by-one / null byte overwrite
- **Keyword**: `off-by-one` `null-byte`
- **Prereq**: Array whose 1-past-end overwrites adjacent variable or string
- **Approach**: Send exact-length payload where last byte is `\x00`, null-terminating adjacent string
- **Example**: `read(buf, 7)` into 6-byte space + password variable → `strcmp("","") == 0`
- **Used in**: Writing-on-the-Wall

### 1-byte return address overwrite
- **Keyword**: `byte-overwrite` `ret-overwrite`
- **Prereq**: `read()` reads exactly 1 byte past ret addr.
- **Approach**: Padding to reach ret addr LSB, overwrite with target byte
- **Example**: `0x400b94` → `0x400b12` (last byte `0x94` → `0x12`)
- **Used in**: Space-Pirate-Going-Deeper

### uninitialized stack leak → ret2libc
- **Keyword**: `uninit-leak` `ret2libc`
- **Prereq**: Buffer not fully initialized before `printf("%s", buf)`, PIE needs leak
- **Approach**: Send 1 byte → residual stack data (PIE return addr) leaked via `%s`. Overflow to `puts@PLT(puts@GOT)` → back to `main`. Second pass: `system("sh")` with known libc.
- **Tip**: Libc `sh\x00` at `/bin/sh` offset + 5 (`0x1d869d` vs `0x1d8698`)
- **Tip**: Double `ret` gadget before `system()` for `movaps` stack alignment
- **Used in**: Sacred-Scrolls-Revenge, Space-Pirate-Retribution

### union type confusion
- **Keyword**: `union` `type-confusion`
- **Prereq**: C union where `integer` and `string[8]` share memory
- **Approach**: Write `p64(13371337)` via string setter, check passes on integer read
- **Used in**: Entity

### strcpy null-byte cascading
- **Keyword**: `strcpy` `key-zeroing`
- **Prereq**: `strcpy` that writes 1 byte past buffer into adjacent global key
- **Approach**: Generate keys of decreasing length (31→0), each `strcpy` null-terminator shifts by 1, eventually zeroing entire key
- **Used in**: Vault-Breaker

### ZIP upload + BOF
- **Keyword**: `zip` `base64` `upload`
- **Prereq**: Binary accepts base64 ZIP uploads, unzips `spell.txt`, reads into buffer
- **Approach**: Build ROP chain in file, ZIP with `-j` (strip paths), base64 encode, upload
- **Watch for**: `/` character in payload (both spell content AND base64 encoding)
- **Tip**: Use `sh` string (libc offset `0x1d869d`) instead of `/bin/sh` to avoid `/` in payload
- **Used in**: Sacred-Scrolls-Revenge

### Quick Decision Matrix
| What you have | Technique | Key checks |
|---------------|-----------|------------|
| No PIE + no canary + NX | ret2win | Find win addr, add `ret` gadget |
| No NX + no PIE | ret2shellcode | Find `jmp rsp`/`jmp rsi` gadget |
| printf(user_input) | FSB leak/write | Enumerate offsets with `%N$p` |
| Integer comparison bypass | int overflow | Check 32-bit truncation in asm |
| 64-bit positive → 32-bit negative | sign trunc | `0x7FFFFFFF + 0x7FFFFFFF` |
| Canary + printf leak | canary bypass | Leak then include in payload |
| 1 byte past ret addr | LSB overwrite | 56 pad + 1 target byte |
| PIE + no canary + overflow | uninit leak → ret2libc | Leak PIE first, then libc, then shell |
| C union + string setter | type confusion | Write integer bytes as string |
| strcpy loop with decreasing lengths | key zeroing | 31→0 writes null bytes |
| ZIP upload + BOF | base64 chain | Check `/` in content + b64 |
