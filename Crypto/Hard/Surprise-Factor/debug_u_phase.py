#!/usr/bin/env python3
"""Debug u-phase forward simulation step by step."""
import sys, os, secrets

sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
from ec import N as CURVE_N
from bignum import _binary_division_odd_modulus, mod, div
from trace import TRACE

N = CURVE_N

# Known test values (same as before)
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

# Parse trace
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
print(f"TZ runs: {len(tz_runs)}")

# Forward simulation of the actual GCD with proper check
u = denominator
x1 = a_mod
x2 = 0

u_phase_runs_found = 0
for step in range(min(140, len(tz_runs))):
    run = tz_runs[step]
    t = run['units']
    h = run['h']
    a = run['a']
    
    # Determine which variable has TZ
    # After the previous subtraction, one variable is even
    if u & 1 == 0:
        # u has TZ
        u_odd = u // (1 << t)  # After TZ removal
        cur_var = 'u'
        
        # Simulate x1 TZ evolution
        a_left = a
        for _ in range(t):
            if a_left > 0:
                x1 = (x1 + N) // 2
                a_left -= 1
            else:
                x1 = x1 // 2
        
        # Now compare u_odd with v = N
        if u_odd >= N + 1:  # Ensure u >= v strictly (u > v or u = v which shouldn't happen)
            u = u_odd - N  # even
            sub_dir = 'u>=v'
            x1 = x1 - x2  # x2 = 0 in u-phase
        else:
            if u_odd == N:
                print(f"Iter {step}: u_odd == N! Infinite loop risk")
            v = N - u_odd  # even
            sub_dir = 'v>u'
            x2 = x2 - x1  # x2 becomes -x1
            if u_phase_runs_found == 0:
                u_phase_runs_found = step
                print(f"First v>u at step {step}! u_odd = {hex(u_odd)}, N = {hex(N)}, u_odd.bit_length() = {u_odd.bit_length()}")
        
        if step < 5 or step >= 127:
            print(f"Step {step}: TZ={t}, var={cur_var}, sub={sub_dir}, u_odd bits={u_odd.bit_length()}")
    else:
        # v has TZ
        print(f"Step {step}: v has TZ (first v-TZ at step {u_phase_runs_found})")
        break

print(f"\nTotal u-phase runs: {u_phase_runs_found}")
print(f"u_phase_runs (first v-TZ at step): {u_phase_runs_found}")

# Now check: is there a switch from u>=v to v>u BEFORE step 132?
# Let me do a clean forward simulation tracking everything
print("\n=== Clean forward simulation ===")
u = denominator
x1 = a_mod
x2 = 0
v = N

total_u_runs = 0
for step in range(400):
    if u == 1 or v == 1:
        print(f"Ended at step {step}. u=1: {u==1}, v=1: {v==1}")
        break
    
    u_was_even = (u & 1) == 0
    v_was_even = (v & 1) == 0
    
    # Process u TZ
    u_tz = 0
    while (u & 1) == 0 and u != 1:
        u //= 2
        if x1 & 1:
            x1 = (x1 + N) // 2
        else:
            x1 //= 2
        u_tz += 1
    
    # Process v TZ
    v_tz = 0
    while (v & 1) == 0 and v != 1:
        v //= 2
        if x2 & 1:
            x2 = (x2 + N) // 2
        else:
            x2 //= 2
        v_tz += 1
    
    if step == 0:
        print(f"Initial TZ: u={u_tz}, v={v_tz}")
    if u_tz > 0 and v_tz == 0 and step < 140:
        total_u_runs = step + 1
    
    # Subtraction
    if u >= v:
        if u == v:
            u = 0
            break
        u -= v
        x1 -= x2
        sub_type = 'u>=v'
    else:
        v -= u
        x2 -= x1
        sub_type = 'v>u'
    
    if step < 3 or (step >= 129 and step < 140):
        print(f"Step {step}: u_tz={u_tz}, v_tz={v_tz}, sub={sub_type}, u.bit={u.bit_length() if u>0 else 0}, v.bit={v.bit_length() if v>0 else 0}")

print(f"Total: step={step+1}, u_runs={total_u_runs}")
