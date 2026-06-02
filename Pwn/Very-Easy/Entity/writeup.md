# Entity — Very Easy Pwn

## Vulnerability
**Type Confusion via C Union.** The `DataStore` union shares memory between `unsigned long long integer` and `char string[8]`. Writing through the STRING path uses `memcpy` into the union with no check, while the INTEGER path blocks the magic value `13371337`.

## Exploit Approach
Use the STRING setter to write the raw bytes of `13371337` (as a little-endian 64-bit integer) into the union, bypassing the integer check. Then call FLAG to trigger `get_flag()`, which reads `DataStore.integer` and prints the flag if it equals `13371337`.

## Steps
1. Menu → `T` (STORE_SET)
2. Submenu → `S` (STRING field)
3. Ritual prompt → send `p64(13371337)` as raw 8 bytes
4. Menu → `C` (FLAG)
5. `get_flag()` checks `DataStore.integer == 13371337` → true → prints flag

## Result
**Local test passed.** Captured fake flag: `HTB{f4k3_fl4g_4_t35t1ng}`
