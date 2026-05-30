#!/usr/bin/env python3
"""Binary GCD reversal from trace: find first v-TZ run with zero 'a' count."""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))

from ec import N
from bignum import half, add, sub, mod
from trace import TRACE

def get_trace(numerator, denominator, modulus):
    TRACE.configure({"half", "add", "sub"})
    TRACE.reset()
    # Import and run the actual binary division
    from bignum import _binary_division_odd_modulus
    result = _binary_division_odd_modulus(numerator, denominator, modulus)
    return result, ''.join(TRACE.get_trace())

def parse_trace(trace_str):
    runs = []
    i = 0
    while i < len(trace_str):
        c = trace_str[i]
        if c == 's':
            runs.append({'type': 'sub'})
            i += 2
        elif c in 'ha':
            h = a = 0
            while i < len(trace_str) and trace_str[i] in 'ha':
                if trace_str[i] == 'h': h += 1
                elif trace_str[i] == 'a': a += 1
                i += 1
            runs.append({'type': 'tz', 'h': h, 'a': a})
        else:
            i += 1
    return runs

# Test with known values where denominator > N (realistic scenario)
N_val = N

# Simulate a realistic case: both nonce_mask and k are ~N
import secrets
nonce_mask = secrets.randbelow(N_val)
k = secrets.randbelow(N_val)
# Make k non-zero
if k == 0: k = 1

hash_int = 0xdeadbeefcafebabedeadbeefcafebabe
r = 0x1234567890abcdef1234567890abcdef
d = 0x1337  # some private key

numerator = (hash_int + r * d) * nonce_mask % N_val
denominator = nonce_mask * k

print(f"nonce_mask bits: {nonce_mask.bit_length()}")
print(f"k bits: {k.bit_length()}")
print(f"denominator bits: {denominator.bit_length()}")
print(f"N bits: {N_val.bit_length()}")

result, trace_str = get_trace(numerator, denominator, N_val)
print(f"Result: {hex(result)}")
print(f"Expected: {hex((hash_int + r * d) * pow(k, -1, N_val) % N_val)}")
print(f"Match: {result == (hash_int + r * d) * pow(k, -1, N_val) % N_val}")
print(f"Trace len: {len(trace_str)}, h:{trace_str.count('h')}, a:{trace_str.count('a')}, s:{trace_str.count('s')}")

runs = parse_trace(trace_str)
tz_runs = [r for r in runs if r['type'] == 'tz']
sub_runs = [r for r in runs if r['type'] == 'sub']
print(f"TZ runs: {len(tz_runs)}, Sub runs: {len(sub_runs)}")

# Look for the first TZ run with a_count == 0 (first v-TZ run)
for i, run in enumerate(tz_runs):
    h = run['h']
    a = run['a']
    tz_units = h // 2
    print(f"TZ run {i}: h={h}, a={a}, units={tz_units}, a_per_unit={a/tz_units if tz_units else 0:.2f}")
    if a == 0:
        print(f"  ^^^ FIRST ZERO-A RUN at index {i}!")
        print(f"  This marks the first v-TZ run.")
        print(f"  Previous runs ({i}) are all u-TZ runs.")
        print(f"  => {i} iterations of u >= v / u-TZ")
        print(f"  => {len(tz_runs) - i} iterations of alternating v/u")
        break

print(f"\nTotal TZ runs: {len(tz_runs)}")
print(f"First zero-a at is the first v-TZ switch point")
