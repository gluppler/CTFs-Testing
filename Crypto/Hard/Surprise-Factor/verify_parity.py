#!/usr/bin/env python3
"""Verify parity bits from trace vs actual x1 evolution."""
import sys, os

sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
from ec import N as CURVE_N
from bignum import _binary_division_odd_modulus, mod, div
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

# Parse div trace
v_pos = trace_str.rfind('v')
div_trace = trace_str[v_pos+1:] if v_pos >= 0 else trace_str
runs = []
i = 0
while i < len(div_trace):
    if div_trace[i] == 's':
        runs.append({'type': 'sub'})
        i += 2
    elif div_trace[i] in 'ha':
        h = a = 0
        while i < len(div_trace) and div_trace[i] in 'ha':
            if div_trace[i] == 'h': h += 1
            elif div_trace[i] == 'a': a += 1
            i += 1
        runs.append({'type': 'tz', 'h': h, 'a': a, 'units': h//2})
    else:
        i += 1

tz_runs = [r for r in runs if r['type'] == 'tz']

# Run the actual GCD tracking x1 parity
u = denominator
x1 = a_mod
x2 = 0
v = N

actual_parity_bits = []
actual_u_tz = []
u_runs_in_phase = 0
v_first_seen = False

for step in range(400):
    if u == 1 or v == 1:
        print(f"Terminated at step {step}")
        break
    
    # Process u TZ
    step_u_tz = 0
    while (u & 1) == 0 and u != 1:
        x1_was_odd = (x1 & 1) == 1
        u //= 2
        if x1_was_odd:
            x1 = (x1 + N) // 2
        else:
            x1 //= 2
        step_u_tz += 1
        if not v_first_seen:
            actual_parity_bits.append(1 if x1_was_odd else 0)
    
    if step_u_tz > 0 and not v_first_seen:
        actual_u_tz.append(step_u_tz)
        u_runs_in_phase = step + 1
    
    # Process v TZ
    step_v_tz = 0
    while (v & 1) == 0 and v != 1:
        v //= 2
        if x2 & 1:
            x2 = (x2 + N) // 2
        else:
            x2 //= 2
        step_v_tz += 1
        if step_v_tz > 0 and not v_first_seen:
            v_first_seen = True
            print(f"First v-TZ at step {step} with t={step_v_tz}")
    
    # Subtraction
    if u >= v:
        if u == v: u = 0; break
        u -= v
        x1 -= x2
    else:
        v -= u
        x2 -= x1

print(f"Actual u-runs before first v-TZ: {u_runs_in_phase}")
print(f"Actual parity bits count: {len(actual_parity_bits)}")
print(f"Actual u TZ counts (first 5): {actual_u_tz[:5]}")

# Now compare with trace
trace_u_tz = [r['units'] for r in tz_runs[:u_runs_in_phase]]
trace_parity = []
for r in tz_runs[:u_runs_in_phase]:
    a = r['a']
    for _ in range(r['units']):
        if a > 0:
            trace_parity.append(1)
            a -= 1
        else:
            trace_parity.append(0)

print(f"\nTrace u TZ counts (first 5): {trace_u_tz[:5]}")
print(f"Actual == Trace u TZ: {actual_u_tz == trace_u_tz}")
print(f"Trace parity bits count: {len(trace_parity)}")
print(f"Actual == Trace parity: {actual_parity_bits == trace_parity}")

if actual_parity_bits != trace_parity:
    # Find first difference
    for idx, (a, t) in enumerate(zip(actual_parity_bits, trace_parity)):
        if a != t:
            print(f"First diff at index {idx}: actual={a}, trace={t}")
            
            # Show surrounding context
            for j in range(max(0, idx-3), min(len(actual_parity_bits), idx+4)):
                if j < len(actual_parity_bits) and j < len(trace_parity):
                    print(f"  idx {j}: actual={actual_parity_bits[j]}, trace={trace_parity[j]}, match={actual_parity_bits[j]==trace_parity[j]}")
            break

# Also verify the x1_0 from actual parity bits
b = len(actual_parity_bits)
B_actual = 0
for bit in actual_parity_bits:
    B_actual = (B_actual << 1) | bit

x1_0_from_actual = (-N * B_actual) % (1 << b)
print(f"\nActual: x1_0 from actual parity = {hex(x1_0_from_actual)}")
print(f"Expected x1_0 (a_mod) = {hex(a_mod)}")
print(f"Match: {x1_0_from_actual == a_mod}")

# And from trace
B_trace = 0
for bit in trace_parity:
    B_trace = (B_trace << 1) | bit

x1_0_from_trace = (-N * B_trace) % (1 << b)
print(f"Trace: x1_0 from trace parity = {hex(x1_0_from_trace)}")
print(f"Expected x1_0 (a_mod) = {hex(a_mod)}")
print(f"Match: {x1_0_from_trace == a_mod}")
