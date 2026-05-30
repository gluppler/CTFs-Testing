#!/usr/bin/env python3
"""Debug the x1_0 computation from parity bits."""
import sys, os, secrets

sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
from ec import N as CURVE_N
from bignum import _binary_division_odd_modulus, mod
from trace import TRACE

N = CURVE_N

# Known test values
d_test = 0x1337
m2 = 0xfc6e91580c1936f44c3e4609a0aa10d0442e48c0facb84b74eca0effc2ebd7e0
k = 0xfeadeedd779b203479d10e751b3c6fa1f50e85acc4ffc7e7d22cfcae0ba27228

hash_int = 0x936062b5d1eab7ae33bd038260bc88f61bafda75d1b7f86c7455a5c810b20000  # random-ish
r = 0xa23b92d900b788a44a1f03b6afe5f78b6ae497e47bfe9e03631e9d66427e9f03  # random-ish

numerator = hash_int + r * d_test
denominator = m2 * k

print(f"denominator = nonce_mask * k = m2 * k = {denominator}")
print(f"denominator bits: {denominator.bit_length()}")

# Compute expected values
expected_s = (hash_int + r * d_test) * pow(k, -1, N) % N
a_mod = mod(numerator, N)  # This is what div does internally: a = mod(a, modulus)
print(f"a_mod (x1 initial) = {hex(a_mod)}")
print(f"denominator (u initial) = {hex(denominator)}")

# Now trace the binary GCD with div->v tracing
TRACE.configure({"half", "add", "sub"})
TRACE.reset()

# Call div properly to get v marker
from bignum import div
result = div(numerator, denominator, N)
trace_str_plain = ''.join(TRACE.get_trace())
print(f"Plain trace (no div tracking): len={len(trace_str_plain)}, h={trace_str_plain.count('h')}")

# Also with div tracking
TRACE.configure({"half", "add", "sub", "div"})
TRACE.reset()
result2 = div(numerator, denominator, N)
trace_str_div = ''.join(TRACE.get_trace())
print(f"Div trace: len={len(trace_str_div)}, h={trace_str_div.count('h')}, v={trace_str_div.count('v')}")

print(f"Result: {hex(result)} (expected {hex(expected_s)})")

# Parse the div trace
v_pos = trace_str_div.rfind('v')
if v_pos >= 0:
    div_trace = trace_str_div[v_pos+1:]
    print(f"DIV trace substring: {div_trace[:50]}...")
    
    # Parse runs
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
    
    # MANUALLY simulate the actual K (number of u-phase runs)
    # by running the GCD with tracking
    u, v = denominator, N
    x1 = a_mod
    x2 = 0
    actual_u_runs = 0
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
        
        if v_tz > 0 and actual_u_runs == 0:
            actual_u_runs = step
            print(f"First v-TZ at step {step}")
        
        if u >= v:
            if u != v: u -= v
            else: u = 0; break
        else:
            v -= u
        step += 1
    print(f"Actual u-phase runs: {actual_u_runs}")
    print(f"Total steps: {step}")
    
    # Now test: for K = actual_u_runs, compute x1_0 from parity
    K = actual_u_runs
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
    b = len(parity_bits)
    print(f"\nK={K}, S={S}, b={b}")
    print(f"Parity bits (first 20): {parity_bits[:20]}")
    print(f"u_tz_counts (first 20): {u_tz_counts[:20]}")
    
    # Compute B
    B = 0
    for bit in parity_bits:
        B = (B << 1) | bit
    print(f"B = {hex(B)[:30]}... (bits={B.bit_length()})")
    
    # Compute x1_0 from congruence: x1_0 ≡ -N*B (mod 2^b)
    candidate = (-N * B) % (1 << b)
    print(f"x1_0 from congruence = {hex(candidate)}")
    print(f"Actual x1_0 = {hex(a_mod)}")
    print(f"Match: {candidate == a_mod}")
    
    # Also check the constraint: x1_0 + N*B ≡ 0 (mod 2^b)
    # This should give x1_end_u = (x1_0 + N*B) / 2^b
    x1_end_u = (a_mod + N * B) // (1 << b)
    print(f"x1_end_u = {hex(x1_end_u)}")
    
    # Check: u_K (from recurrence) should be known
    # u_K = u after all u-phase processing (the odd value compared with N)
    
    # Verify by forward simulation of u
    u_sim = denominator
    for t in u_tz_counts:
        u_after_tz = u_sim // (1 << t)  # After TZ removal
        # Since u >> N during u-phase: subtract N
        u_sim = u_after_tz - N  # This is the u value after subtraction
    
    print(f"u_K (from forward sim) = {hex(u_sim)}")
    
    # Now, u_K should equal R where R = x1_0 * s^(-1) * 2^(-S) mod N
    inv_s = pow(result, -1, N)
    inv_2S = pow(pow(2, S, N), -1, N)
    R = (a_mod * inv_s % N) * inv_2S % N
    print(f"R = x1_0 * s^{-1} * 2^{-S} mod N = {hex(R)}")
    print(f"R == u_K: {R == u_sim}")
    
    # Also check: N - u_sim should have v2 = tz_runs[K]['units']
    v2_N_minus_u = (N - u_sim) & -(N - u_sim)  # lowest power of 2 divisor
    trailing_zeros = (N - u_sim).bit_length() - 1  # approximate? No...
    # Actually compute v2 properly:
    temp = N - u_sim
    v2 = 0
    while temp % 2 == 0:
        temp //= 2
        v2 += 1
    t_K = tz_runs[K]['units']
    print(f"v2(N - u_K) = {v2}, expected (from trace) = {t_K}")
    print(f"Match: {v2 == t_K}")
    
    # Check: N - u_sim ≡ 0 (mod 2^{t_K})
    print(f"u_K ≡ N (mod 2^{t_K}): {u_sim % (1<<t_K) == N % (1<<t_K)}")
    
    # Check the constraint: R ≡ N (mod 2^{t_K})
    print(f"R ≡ N (mod 2^{t_K}): {R % (1<<t_K) == N % (1<<t_K)}")
    
    # If all matches: algorithm works! Now find d
    if R == u_sim and v2 == t_K:
        print("\n=== ALGORITHM VERIFIED! ===")
        
        # Compute C for u_0 reconstruction
        C = 0
        cum = 0
        for t in u_tz_counts[:-1]:
            cum += t
            C += 1 << (S - cum)
        C += 1
        u_0 = u_sim * (1 << S) + N * C
        print(f"Reconstructed u_0 = {hex(u_0)}")
        print(f"Actual denominator = {hex(denominator)}")
        print(f"Match: {u_0 == denominator}")
        
        # Now find d
        # k = u_0 / m2. Since m2 is unknown, try small divisors...
        # Actually, use k = (hash + r*d) * s^(-1) mod N
        # and u_0 = m2 * k
        
        # For the correct d (d_test = 0x1337):
        k_actual = (hash_int + r * d_test) * pow(result, -1, N) % N
        m2_actual = u_0 // k_actual
        print(f"k_actual = {hex(k_actual)}")
        print(f"m2_actual = {hex(m2_actual)}")
        print(f"m2_actual * k_actual == u_0: {m2_actual * k_actual == u_0}")
        
        # Now verify: without knowing d, can I find it?
        # I know u_0 and x1_0 (a_mod). 
        # x1_0 = m2 * (hash + r*d) mod N
        # u_0 = m2 * k
        # k = (hash + r*d) * s^(-1) mod N
        # 
        # So: u_0 * s = m2 * (hash + r*d + N * t) for some t
        # x1_0 = m2 * (hash + r*d) mod N (known!
        # But also: u_0 * s mod N = m2 * (hash + r*d) mod N = x1_0
        # This is expected: u_0 * s ≡ x1_0 (mod N) (always true for correct reversal)
        
        # To find d: need m2 from u_0 and k.
        # But k = (hash + r*d) * s^(-1) mod N depends on d.
        # 
        # From u_0 = m2 * k and x1_0 ≡ m2 * (hash + r*d) (mod N):
        # x1_0 ≡ u_0 * s (mod N) [always true]
        #
        # For the correct d: u_0 / k = m2 (integer)
        # m2 < N
        # And x1_0 ≡ m2 * (hash + r*d) (mod N)
        #
        # Given u_0 and x1_0: d = (k * s - hash) * r^{-1} mod N
        # where k = u_0 / m2.
        #
        # m2 is a divisor of u_0, so finding m2 is finding a divisor of u_0.
        
        # For 512-bit semiprime: factoring is hard IN GENERAL.
        # But maybe the nonce k is SMALL?
        
        # Try brute-forcing small k values
        print("\nTrying to find d by checking divisors of u_0...")
        for k_try in range(1, 50000):
            if u_0 % k_try == 0:
                m2_try = u_0 // k_try
                if m2_try > 0 and m2_try < N:
                    d_try = (k_try * result - hash_int) * pow(r, -1, N) % N
                    k_verify = (hash_int + r * d_try) * pow(result, -1, N) % N
                    if k_verify == k_try:
                        print(f"Found! k = {k_try}, d = {hex(d_try)}")
                        print(f"Expected d = {hex(d_test)}")
                        print(f"Match: {d_try == d_test}")
