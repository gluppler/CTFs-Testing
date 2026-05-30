#!/usr/bin/env python3
"""Debug binary GCD to find where manual trace diverges from actual trace."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))

from ec import N
from bignum import P256_PRIME, _binary_division_odd_modulus, half, add, sub, _P256_MODULUS
from trace import TRACE

# Known test values
nonce_mask = 12345678901234567890
k = 9876543210987654321
hash_int = 0xdeadbeefcafebabe
r = 0x1234567890abcdef
d = 0x42

numerator = nonce_mask * (hash_int + r * d)
denominator = nonce_mask * k

print(f"denominator = nonce_mask * k = {denominator}")
print(f"denominator bit length: {denominator.bit_length()}")
print(f"N bit length: {N.bit_length()}")
print(f"denominator < N: {denominator < N}")

# Step-through of _binary_division_odd_modulus for the first few iterations
# Enable only half, add, sub tracing per iteration
TRACE.configure({"half", "add", "sub"})

# Let me reimplement _binary_division_odd_modulus with step-by-step outputs
def debug_binary_gcd(a, b, modulus):
    u = b
    v = modulus
    x1 = a % modulus
    x2 = 0
    step = 0
    
    print(f"\n=== Binary GCD Debug ===")
    print(f"Initial: u={hex(u)[:20]}... (bits={u.bit_length()}), v={hex(v)[:20]}... (bits={v.bit_length()})")
    print(f"Initial: x1={hex(x1)[:20]}...")
    
    while u != 1 and v != 1:
        print(f"\n--- Step {step} ---")
        print(f"Before TZ: u odd? {u&1}, v odd? {v&1}")
        
        # Process u TZ
        u_tz = 0
        while (u & 1) == 0:
            u = half(u)
            if x1 & 1:
                x1 = add(x1, modulus)
            x1 = half(x1)
            u_tz += 1
        
        # Process v TZ
        v_tz = 0
        while (v & 1) == 0:
            v = half(v)
            if x2 & 1:
                x2 = add(x2, modulus)
            x2 = half(x2)
            v_tz += 1
        
        print(f"After TZ: u_tz={u_tz}, v_tz={v_tz}")
        print(f"  u bits={u.bit_length()}, v bits={v.bit_length()}")
        
        # Subtraction
        if u >= v:
            u = sub(u, v)
            if x1 < x2:
                x1 = add(x1, modulus)
            x1 = sub(x1, x2)
            print(f"  u >= v: u -= v")
        else:
            v = sub(v, u)
            if x2 < x1:
                x2 = add(x2, modulus)
            x2 = sub(x2, x1)
            print(f"  v > u: v -= u")
        
        print(f"  u bits={u.bit_length()}, v bits={v.bit_length()}")
        
        step += 1
        if step > 10:
            print("... (truncated)")
            break
    
    if u == 1:
        return x1 % modulus
    return x2 % modulus

result = debug_binary_gcd(numerator % N, denominator, N)
expected = (hash_int + r * d) * pow(k, -1, N) % N
print(f"\nResult: {hex(result)}")
print(f"Expected: {hex(expected)}")
print(f"Match: {result == expected}")
