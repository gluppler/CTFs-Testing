# Space Pirate: Entry Point - Writeup

**Difficulty**: Very Easy
**Category**: Pwn
**Vulnerability**: Format String
**Protections**: Canary, NX, PIE, Full RELRO

## Summary

The binary has a **format string vulnerability** in `printf(local_38)` where our raw input is passed as the format string. The goal is to change `local_48` from `0xdeadbeef` to `0xdead1337` to call `open_door()`, which runs `system("cat flag*")`.

## Analysis

```c
// Pseudocode from main():
long local_48 = 0xdeadbeef;           // rbp-0x40
long *local_40 = &local_48;           // rbp-0x38
char local_38[40];                     // rbp-0x30

if (option == 1) {
    read(0, local_38, 0x1f);          // read 31 bytes
    printf("\nYour card is: ");
    printf(local_38);                 // FORMAT STRING BUG
    if (local_48 == 0xdead1337)
        open_door();                  // system("cat flag*")
}
```

Stack at `printf(local_38)`:
- Position 6: `0xdeadbeef` (value of local_48)
- Position 7: stack address pointing to local_48 (local_40)
- Position 8+: our input buffer

## Exploit

Use `%7$hn` to write to the address at position 7 (the pointer to local_48). Write `0x1337` (4919 decimal) as a 2-byte short to overwrite the low 2 bytes of `0xdeadbeef` → `0xdead1337`.

**Payload**: `%4919x%7$hn`

- `%4919x` prints 4919 characters (0x1337)
- `%7$hn` writes that count as a 2-byte short to the address at position 7

## Flag

`HTB{th3_g4t35_4r3_0p3n!}`
