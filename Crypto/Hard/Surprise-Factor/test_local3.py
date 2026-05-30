#!/usr/bin/env python3
"""Test whether first v-TZ run has zero a's, across multiple random trials."""
import sys, os, secrets
sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))

from ec import N
from trace import TRACE

def get_trace_and_result(numerator, denominator, modulus):
    TRACE.configure({"half", "add", "sub"})
    TRACE.reset()
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

def analyze_trace(trace_str):
    runs = parse_trace(trace_str)
    tz_runs = [r for r in runs if r['type'] == 'tz']
    
    # Find first v-TZ run by analyzing trace
    # The first v-TZ run happens when the subtraction changes direction
    # We can detect this by looking at the pattern of TZ distribution
    
    # Alternative approach: manually trace to find first v-TZ
    # This simulates the actual GCD AND records which variable has TZ
    return tz_runs

def trace_with_variable_info(denominator, modulus):
    """Run the binary GCD and record which variable each TZ run belongs to."""
    u = denominator
    v = modulus
    x1_v = 0  # placeholder
    x2_v = 0
    var_trace = []
    
    while u != 1 and v != 1:
        u_tz = 0
        while (u & 1) == 0:
            u //= 2
            u_tz += 1
            # For x1: not needed
        
        v_tz = 0
        while (v & 1) == 0:
            v //= 2
            v_tz += 1
        
        if u_tz > 0 and v_tz == 0:
            var_trace.append(('u', u_tz))
        elif v_tz > 0 and u_tz == 0:
            var_trace.append(('v', v_tz))
        elif u_tz > 0 and v_tz > 0:
            var_trace.append(('both', u_tz, v_tz))
        
        if u >= v:
            if u == v:
                u = 0
                break
            u -= v
        else:
            v -= u
    
    return var_trace

# Multiple random tests
for trial in range(10):
    nonce_mask = secrets.randbelow(N)
    k = secrets.randbelow(N)
    if k == 0: k = 1
    
    hash_int = secrets.randbelow(N)
    r = secrets.randbelow(N)
    d = secrets.randbelow(N)
    
    numerator = (hash_int + r * d) * nonce_mask % N
    denominator = nonce_mask * k
    
    result, trace_str = get_trace_and_result(numerator, denominator, N)
    tz_runs = parse_trace(trace_str)
    tz_list = [r for r in tz_runs if r['type'] == 'tz']
    
    var_trace = trace_with_variable_info(denominator, N)
    
    # Find first v-TZ in var_trace
    first_v = None
    for idx, vt in enumerate(var_trace):
        if vt[0] == 'v':
            first_v = idx
            break
    
    # For the trace TZ runs, check a-count around the first v-TZ
    if first_v is not None:
        # The trace TZ runs before first_v are all u-TZ
        # The one at first_v is the first v-TZ
        u_runs = tz_list[:first_v]
        v1_run = tz_list[first_v]
        print(f"Trial {trial}: #u-runs={len(u_runs)}, first v-TZ: h={v1_run['h']}, a={v1_run['a']}, units={v1_run['h']//2}, has_a={v1_run['a']>0}, total_runs={len(tz_list)}")
        
        # Also check a-count for all u-runs vs v-runs
        u_has_a = sum(1 for r in u_runs if r['a'] > 0)
        v_has_a = sum(1 for r in tz_list[first_v:] if r['a'] > 0)
        print(f"  u-runs with 'a': {u_has_a}/{len(u_runs)}, v-runs with 'a': {v_has_a}/{len(tz_list)-first_v}")
