#!/usr/bin/env python3
"""Correct parity bit parsing from trace."""
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

# Parse correctly: scan the raw trace char by char
# Parse into runs: tz (h/a pattern) or sub
runs = []
i = 0
while i < len(trace_str):
    if trace_str[i] == 's':
        runs.append({'type': 'sub'})
        i += 2  # ss
    elif trace_str[i] == 'h':
        # Start of a TZ run
        # Parse units within this run: hh = even, hah = odd
        units = []
        while i < len(trace_str) and trace_str[i] in 'ha':
            if trace_str[i] == 'h' and i+1 < len(trace_str) and trace_str[i+1] == 'a':
                # hah pattern: odd
                units.append(1)
                i += 3
            elif trace_str[i] == 'h' and i+1 < len(trace_str) and trace_str[i+1] == 'h':
                # hh pattern: even
                units.append(0)
                i += 2
            elif trace_str[i] == 'h' and i+1 < len(trace_str) and trace_str[i+1] == 's':
                # h then sub - this shouldn't happen
                i += 1
                break
            else:
                # shouldn't happen
                if trace_str[i] == 'h':
                    i += 1
                else:
                    i += 1
        runs.append({'type': 'tz', 'units': units})
    else:
        i += 1

tz_runs = [r for r in runs if r['type'] == 'tz']

print(f"Total TZ runs: {len(tz_runs)}")
print(f"First run units: {tz_runs[0]['units'][:10]}...")
print(f"Total units: {sum(len(r['units']) for r in tz_runs)}")

# Now, run the actual GCD and collect REAL parity bits
u = denominator
x1 = a_mod
x2 = 0
v = N

actual_parity = []
v_first = False
actual_u_runs = 0

for step in range(500):
    if u == 1 or v == 1:
        print(f"Ended at step {step}")
        break
    
    # Process u TZ  
    while (u & 1) == 0 and u != 1:
        parity = 1 if (x1 & 1) else 0
        u //= 2
        if parity:
            x1 = (x1 + N) // 2
        else:
            x1 //= 2
        if not v_first:
            actual_parity.append(parity)
    
    # Process v TZ
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
        u -= v
        x1 -= x2
    else:
        v -= u
        x2 -= x1

print(f"\nActual u-runs: {actual_u_runs}")
print(f"Actual parity bits: {len(actual_parity)}")
print(f"First 10: {actual_parity[:10]}")

# Collect trace parity for first actual_u_runs runs
trace_parity = []
for r in tz_runs[:actual_u_runs]:
    trace_parity.extend(r['units'])

print(f"Trace parity bits: {len(trace_parity)}")
print(f"First 10: {trace_parity[:10]}")
print(f"Match: {actual_parity == trace_parity}")

if actual_parity != trace_parity:
    for idx, (a, t) in enumerate(zip(actual_parity, trace_parity)):
        if a != t:
            print(f"First diff at {idx}: actual={a}, trace={t}")
            break

# Now compute x1_0 from the CORRECT parity
b = len(actual_parity)
B = 0
for bit in actual_parity:
    B = (B << 1) | bit

x1_0_calc = (-N * B) % (1 << b)
x1_end_u_calc = (x1_0_calc + N * B) // (1 << b)

print(f"\nFrom correct trace parity:")
print(f"  x1_0 computed = {hex(x1_0_calc)}")
print(f"  x1_0 actual   = {hex(a_mod)}")
print(f"  Match: {x1_0_calc == a_mod}")
print(f"  x1_end_u = {hex(x1_end_u_calc)}")

# Also compute from the trace parity (should match if parsing is correct)
B_t = 0
for bit in trace_parity:
    B_t = (B_t << 1) | bit
x1_0_t = (-N * B_t) % (1 << b)
print(f"\nFrom trace parity (after fix):")
print(f"  x1_0 = {hex(x1_0_t)}")
print(f"  Match: {x1_0_t == a_mod}")
