# Vault Breaker - Writeup

**Category:** Pwn
**Difficulty:** Very Easy
**Author:** w3th4nds / ir0nstone

## Vulnerability

`strcpy()` null-byte overwrite. The `new_key_gen()` function copies a user-specified-length random key to the global `random_key` buffer using `strcpy()`, which appends a null byte after the copied string. By iteratively generating keys of decreasing lengths (31 down to 0), each `strcpy` call zeroes out one more byte of `random_key`, eventually nulling out all 32 bytes.

## Exploit

1. Call `new_key_gen()` with length 31 → `strcpy` nulls byte 31 of `random_key`
2. Call with length 30 → nulls byte 30
3. ... continue down to length 0 → nulls byte 0
4. After 32 iterations, `random_key` is all zeros
5. Call `secure_password()` which XORs `flag.txt` with `random_key` — XOR with 0 = plaintext flag

## Flag

`HTB{f4k3_fl4g_4_t35t1ng}`

## Protections

- Full RELRO, Stack Canary, NX, PIE — all enabled but irrelevant to this logic bug
