# Getting-Started — Very Easy Pwn

## Vulnerability
Stack buffer overflow — `scanf("%s", buffer)` reads unbounded input into a 32-byte buffer on the stack, allowing overwrite of adjacent stack variables.

## Analysis

From `main` disassembly (PIE base `0x0`):

- Buffer at `rbp-0x30` (32 bytes zeroed)
- Dummy alignment value `0x6969696969696969` at `rbp-0x10`
- Canary `0x00000000deadbeef` at `rbp-0x08`
- `scanf("%s", buffer)` at `main+0x114` — reads until whitespace, no limit
- Comparison at `main+0x12a`: if `rbp-0x8 != 0xdeadbeef`, calls `win()`
- `win()` opens `./flag.txt` and prints its contents character by character

Distance from buffer start to canary: `0x30 - 0x8 = 0x28 = 40` bytes.

## Exploit

```
payload = b'A' * 40 + b'B' * 8
```

40 bytes of padding fill the buffer + alignment dummy, and the 8 `B`s overwrite `0xdeadbeef` with `0x4242424242424242`, which is not equal, so `win()` executes.

## Local Test Result

```
HTB{f4k3_fl4g_4_t35t1ng}
```

## Flag

`HTB{f4k3_fl4g_4_t35t1ng}`
