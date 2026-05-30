#!/usr/bin/env python3
"""Fix the B computation - bits should be in REVERSE order."""
import sys, os

sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
from ec import N as CURVE_N
from bignum import _binary_division_odd_modulus, mod
from trace import TRACE

N = CURVE_N

d_test = 0x1337
m2 = 0xfc6e91580c1936f44c3e4609a0aa10d0442e48c0facb84b74eca0effc2ebd7e0
k = 0xfeadeedd779b203479d10e751b3c6fa1f50e85acc4ffc7e7d22cfcae0ba27228

hash_int = 0x936062b5d1eab7ae33bd038260bc88f61bafda75d1b7f86c7455a5c810b20000
r = 0xa23b92d900b788a44a1f03b6afe5f78b6ae497e47bfe9e03631e9d66427e9f03

denominator = m2 * k
numerator = hash_int + r * d_test

TRACE.configure({"half", "add", "sub", "div"})
TRACE.reset()
a_mod = mod(numerator, N)
result = _binary_division_odd_modulus(a_mod, denominator, N)
trace_str = ''.join(TRACE.get_trace())

# Parse trace correctly
runs = []
i = 0
while i < len(trace_str):
    if trace_str[i] == 's':
        runs.append({'type': 'sub'})
        i += 2
    elif trace_str[i] == 'h':
        units = []
        while i < len(trace_str) and trace_str[i] in 'ha':
            if trace_str[i] == 'h' and i+1 < len(trace_str) and trace_str[i+1] == 'a':
                units.append(1)
                i += 3
            elif trace_str[i] == 'h' and i+1 < len(trace_str) and trace_str[i+1] == 'h':
                units.append(0)
                i += 2
            else:
                break
        runs.append({'type': 'tz', 'units': units})
    else:
        i += 1

tz_runs = [r for r in runs if r['type'] == 'tz']

# Get actual parity from manual simulation  
u = denominator
x1 = a_mod
x2 = 0
v = N

actual_parity = []
v_first = False
for step in range(500):
    if u == 1 or v == 1:
        break
    while (u & 1) == 0 and u != 1:
        parity = 1 if (x1 & 1) else 0
        u //= 2
        if parity:
            x1 = (x1 + N) // 2
        else:
            x1 //= 2
        if not v_first:
            actual_parity.append(parity)
    while (v & 1) == 0 and v != 1:
        v //= 2
        if x2 & 1:
            x2 = (x2 + N) // 2
        else:
            x2 //= 2
        if not v_first:
            v_first = True
    if not v_first:
        actual_u_runs = step + 1
    if u >= v:
        if u == v: u = 0; break
        u -= v; x1 -= x2
    else:
        v -= u; x2 -= x1

# Compute B with CORRECT ordering: bit_i contributes 2^i
b = len(actual_parity)
B_correct = 0
for i, bit in enumerate(actual_parity):
    B_correct |= (bit << i)

print(f"b = {b} bits")
print(f"B_correct (LSB first): {hex(B_correct)}")

# x1_0 = 2^b * x1_b - N * B_correct
# x1_0 ≡ -N * B_correct (mod 2^b)
x1_0 = (-N * B_correct) % (1 << b)
print(f"x1_0 computed = {hex(x1_0)}")
print(f"x1_0 actual   = {hex(a_mod)}")
print(f"Match: {x1_0 == a_mod}")

# If not matching, try c=1
if not (x1_0 == a_mod):
    # x1_0 = 2^b * x1_b - N * B
    # x1_0 <= N, x1_0 >= 0
    # x1_0 ≡ -N*B (mod 2^b)
    hmm = (-N * B_correct) % (1 << b)
    print(f"hmm = {hex(hmm)}")
    print(f"hmm < N: {hmm < N}")
    
    # The formula x1_0 = (-N*B) % 2^b is correct IF the result < N
    # and x1_b = (x1_0 + N*B) / 2^b is consistent
    
    # Try: x1_0 = hmm (if hmm < N)
    if hmm < N:
        x1_b = (hmm + N * B_correct) // (1 << b)
        print(f"x1_b (with c=0) = {hex(x1_b)}")
        print(f"x1_b < N: {x1_b < N}")
        
        # If x1_b >= N: need to subtract N
        if x1_b >= N:
            x1_b_adjusted = x1_b - N
            print(f"x1_b (adjusted) = {hex(x1_b_adjusted)}")
    
    # Let me also try: if hmm >= N, then
    # x1_0 should be hmm - 2^b + N? No...
    # If hmm >= N: x1_0 = hmm - 2^b? No, x1_0 must be >= 0.
    # 
    # x1_0 ≡ hmm (mod 2^b) and x1_0 ∈ [0, N-1].
    # Since N < 2^b: hmm is the unique solution OR hmm - 2^b is also a solution.
    # If hmm >= N: try x1_0 = hmm (which might be >= N, contradicting x1_0 < N)
    #   or x1_0 = hmm - 2^b (which would be < 0, impossible).
    # So x1_0 = hmm is the ONLY possible value.
    # If hmm >= N: there's no valid x1_0!
    
    # But the correct x1_0 IS < N. So hmm should give it.
    # UNLESS b is wrong (wrong number of u-phase runs).
    
    print("\nTesting all B constructions...")
    # Try: MSB-first (my original wrong approach)
    B_wrong = 0
    for bit in actual_parity:
        B_wrong = (B_wrong << 1) | bit
    print(f"B_wrong (MSB first): {hex(B_wrong)}")
    x1_test = (-N * B_wrong) % (1 << b)
    print(f"x1 from wrong B: {hex(x1_test)}")
    
    # The correct formula uses bits in GROWING index order (bit i contributes 2^i)
    # Let me verify with a small example
    print("\nManual verification with first 3 parity bits:")
    for i in range(min(5, b)):
        bit = actual_parity[i]
        print(f"  bit[{i}] = {bit}")
    
    # If parity bits = [0,0,0,1,1,0,0,0,1,0,...]
    # B_correct = 0*2^0 + 0*2^1 + 0*2^2 + 1*2^3 + 1*2^4 + 0*2^5 + ... = 2^3 + 2^4 + 2^8 + ...
    # x1_1 = (x1_0 + 0*N) / 2 = x1_0/2  (bit[0]=0: x1 was even)
    # x1_2 = (x1_1 + 0*N) / 2 = x1_1/2 = x1_0/4  (bit[1]=0)
    # x1_3 = (x1_2 + 0*N) / 2 = x1_2/2 = x1_0/8  (bit[2]=0)
    # x1_4 = (x1_3 + N) / 2 = (x1_0/8 + N)/2 = x1_0/16 + N/2  (bit[3]=1)
    # x1_5 = (x1_4 + N) / 2 = (x1_0/16 + N/2 + N)/2 = x1_0/32 + 3N/4  (bit[4]=1)
    
    # x1_5 = x1_0/2^5 + N*(bit[0]/2 + bit[1]/4 + bit[2]/8 + bit[3]/16 + bit[4]/32)
    # = x1_0/32 + N*(0 + 0 + 0 + 1/16 + 1/32) = x1_0/32 + N*3/32
    # 
    # In general: x1_b = x1_0/2^b + N*sum(bit_i/2^{b-i}) for i=0 to b-1
    
    # x1_b = x1_0/2^b + N*sum(bit_i/2^{b-i})
    # = x1_0/2^b + N*sum(bit_i*2^{i-b})
    # = x1_0/2^b + N*2^{-b}*sum(bit_i*2^i)
    
    # x1_b = (x1_0 + N*sum(bit_i*2^i)) / 2^b
    
    # YES: B = sum(bit_i * 2^i) ← LSB = bit_0
    
    print(f"\nB_correct = sum(bit_i * 2^i)")
    print(f"This gives B_correct = {hex(B_correct)}")
    
    # Try: different x1_b values
    # x1_0 = 2^b * x1_b - N * B_correct
    # For x1_0 = a_mod (correct):
    test_x1_b = (a_mod + N * B_correct) // (1 << b)
    test_rem = (a_mod + N * B_correct) % (1 << b)
    print(f"\nTesting with actual x1_0 = {hex(a_mod)}:")
    print(f"  (x1_0 + N*B) / 2^b = {hex(test_x1_b)}, remainder = {test_rem}")
    print(f"  Exact division: {test_rem == 0}")
    print(f"  x1_b from this: {hex(test_x1_b)}")
    
    # Hmm, if remainder != 0: the formula doesn't work
    # This means B_correct is wrong
    
    # Let me recompute B = sum(bit_i * 2^{b-1-i}) (MSB first)
    B_msb = 0
    for bit in actual_parity:
        B_msb = (B_msb << 1) | bit
    test_x1_b2 = (a_mod + N * B_msb) // (1 << b)
    test_rem2 = (a_mod + N * B_msb) % (1 << b)
    print(f"\nWith MSB-first B:")
    print(f"  (x1_0 + N*B) / 2^b = {hex(test_x1_b2)}, remainder = {test_rem2}")
    
    # Try with reversed bits
    B_rev = int(''.join(str(b) for b in reversed(actual_parity)), 2)
    test_x1_b3 = (a_mod + N * B_rev) // (1 << b)
    test_rem3 = (a_mod + N * B_rev) % (1 << b)
    print(f"\nWith fully reversed parity bits:")
    print(f"  B_rev = {hex(B_rev)}")
    print(f"  (x1_0 + N*B) / 2^b = {hex(test_x1_b3)}, remainder = {test_rem3}")
