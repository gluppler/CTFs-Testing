# Racecar - Writeup

**Category:** Pwn
**Difficulty:** Very Easy
**Platform:** Linux 32-bit
**Protections:** Canary, NX, PIE, Full RELRO

## Vulnerability

**Format String Bug** in the `car_menu()` function. After winning a race, user input is passed directly to `printf()` without a format string:

```c
read(0, __format, 0x170);
printf(__format);  // format string vulnerability
```

The flag is loaded onto the stack (in `local_3c[44]`) immediately before the vulnerable `printf` call, via:

```c
fgets(local_3c, 0x2c, __stream);  // flag.txt -> stack buffer
```

## Exploit Approach

Leak the flag from the stack using format string specifiers (`%N$p`). The flag sits at stack offsets 12-19 (32-bit, 4 bytes per word). Navigate the menu to win a race (Car 1 + Circuit race gives ~90% win rate), then send `%12$p.%13$p...%19$p` to leak the flag bytes in little-endian hex format.

## Key Details

- **Binary:** 32-bit ELF, dynamically linked
- **Flag offset:** `%12$p` through `%19$p` on the stack
- **Win strategy:** Select Car 1 + Circuit (race 2) for ~90% win probability
- **Parsing:** ANSI escape code `\x1b[0m` prepends the first hex value; use offsets 1-34 and search for `HTB{` pattern in raw bytes

## Exploit Output

```
$ python3 exploit.py
[+] Won on attempt 1!
[+] Flag: HTB{f4k3_fl4g_f0r_l0c4l_t3st1ng}
```
