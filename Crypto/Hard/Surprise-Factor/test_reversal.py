#!/usr/bin/env python3
"""Local test of the GCD reversal algorithm."""
import sys, os, secrets

sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
from ec import N as CURVE_N
from bignum import _binary_division_odd_modulus
from trace import TRACE

def parse_div_gcd(trace_str):
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
    return tz_runs

def local_test():
    N = CURVE_N
    
    # Known values for test
    d_test = 0x1337
    m2 = int.from_bytes(os.urandom(32), 'big') % N
    if m2 == 0: m2 = 1
    k = int.from_bytes(os.urandom(32), 'big') % N
    if k == 0: k = 1
    
    hash_int = int.from_bytes(os.urandom(32), 'big') % N
    r = int.from_bytes(os.urandom(32), 'big') % N
    
    numerator = (hash_int + r * d_test) * m2
    denominator = m2 * k
    
    print(f"d_test = {hex(d_test)}")
    print(f"m2 = {hex(m2)[:20]}... ({m2.bit_length()} bits)")
    print(f"k = {hex(k)[:20]}... ({k.bit_length()} bits)")
    print(f"denominator = {hex(denominator)[:20]}... ({denominator.bit_length()} bits)")
    
    # Call div through the full chain to get proper trace
    TRACE.configure({"half", "add", "sub", "div"})
    TRACE.reset()
    
    # Simulate what div does
    from bignum import mod
    a_mod = mod(numerator, N)
    result = _binary_division_odd_modulus(a_mod, denominator, N)
    trace_str = ''.join(TRACE.get_trace())
    
    expected_s = (hash_int + r * d_test) * pow(k, -1, N) % N
    print(f"result s = {hex(result)}")
    print(f"expected = {hex(expected_s)}")
    print(f"match = {result == expected_s}")
    print(f"trace: h={trace_str.count('h')}, a={trace_str.count('a')}, s={trace_str.count('s')}, v={trace_str.count('v')}")
    
    tz_runs = parse_div_gcd(trace_str)
    print(f"DIV TZ runs: {len(tz_runs)}")
    total_units = sum(r['units'] for r in tz_runs)
    print(f"Total TZ units: {total_units}")
    
    # Find actual K from manual simulation
    u, v = denominator, N
    actual_K = 0
    found_switch = False
    step = 0
    while u != 1 and v != 1:
        u_tz = 0
        while (u & 1) == 0:
            u //= 2
            u_tz += 1
        v_tz = 0
        while (v & 1) == 0:
            v //= 2
            v_tz += 1
        
        if not found_switch and v_tz > 0:
            actual_K = step
            found_switch = True
            print(f"Actual K = {actual_K} (first v-TZ at step {step})")
        
        if u >= v:
            if u != v: u -= v
            else: u = 0; break
        else:
            v -= u
        step += 1
    
    if not found_switch:
        print(f"No v-TZ found! Total steps: {step}. u-phase = all")
        actual_K = step
    
    print(f"Total steps: {step}")
    
    # Now test the reversal algorithm for each K around actual_K
    for K_try in range(max(1, actual_K-3), min(actual_K+4, len(tz_runs))):
        K = K_try
        
        parity_bits = []
        u_tz_counts = []
        for i in range(K):
            run = tz_runs[i]
            units = run['units']
            a = run['a']
            u_tz_counts.append(units)
            a_left = a
            for _ in range(units):
                if a_left > 0:
                    parity_bits.append(1)
                    a_left -= 1
                else:
                    parity_bits.append(0)
        
        S = sum(u_tz_counts)
        if S < 256:
            continue
        
        b = len(parity_bits)
        B = 0
        for bit in parity_bits:
            B = (B << 1) | bit
        
        candidate_x1_0 = (-N * B) % (1 << b)
        
        if candidate_x1_0 >= N:
            continue
        
        x1_0 = candidate_x1_0
        x1_end_u = (x1_0 + N * B) // (1 << b)
        
        # Check the consistency
        inv_s = pow(result, -1, N)
        inv_2S = pow(pow(2, S, N), -1, N)
        R = (x1_0 * inv_s % N) * inv_2S % N
        
        if R % 2 == 0:
            continue
        
        t_K = tz_runs[K]['units']
        if R % (1 << t_K) != N % (1 << t_K):
            continue
        
        # Compute u_0
        C = 0
        cum_so_far = 0
        for t in u_tz_counts[:-1]:
            cum_so_far += t
            C += 1 << (S - cum_so_far)
        C += 1
        
        u_0 = R * (1 << S) + N * C
        
        if u_0 <= 0 or u_0 >= N * N:
            continue
        
        print(f"\nK={K}: CONSISTENT!")
        print(f"  x1_0 = {hex(x1_0)[:30]}...")
        print(f"  Actual x1_0 should be: {hex(a_mod)[:30]}...")
        print(f"  Match x1_0: {x1_0 == a_mod}")
        print(f"  u_0 = {hex(u_0)[:30]}... ({u_0.bit_length()} bits)")
        print(f"  Actual u_0 = m2*k = {hex(denominator)[:30]}...")
        print(f"  Match u_0: {u_0 == denominator}")
        
        if x1_0 == a_mod and u_0 == denominator:
            print(f"  >>> PERFECT MATCH! ALGORITHM WORKS! <<<")
            
            # Now try to find d
            for k_check in range(1, min(100000, u_0)):
                if u_0 % k_check == 0:
                    m2_check = u_0 // k_check
                    if m2_check < N:
                        d_check = (k_check * result - hash_int) * pow(r, -1, N) % N
                        k_verify = (hash_int + r * d_check) * pow(result, -1, N) % N
                        if k_verify == k_check:
                            print(f"  Found d = {hex(d_check)} (expected {hex(d_test)})")
                            print(f"  Match: {d_check == d_test}")

if __name__ == '__main__':
    local_test()
