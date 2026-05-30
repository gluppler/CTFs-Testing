#!/usr/bin/env python3
"""
Solver for Surprise Factor - Core GCD reversal algorithm.
Tests locally then attacks the server.
"""
import sys, os, socket, json, secrets

sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
from ec import N as CURVE_N

def get_sig_and_trace(track, host='154.57.164.80', port=30118):
    s = socket.socket()
    s.settimeout(60)
    s.connect((host, port))
    req = {'action': 'sign', 'track': track}
    s.sendall((json.dumps(req) + '\n').encode())
    data = b''
    while True:
        try:
            chunk = s.recv(1000000)
            if not chunk: break
            data += chunk
        except: break
    s.close()
    return json.loads(data.decode())

def submit_d(d, host='154.57.164.80', port=30118):
    s = socket.socket()
    s.settimeout(10)
    s.connect((host, port))
    req = {'action': 'submit', 'd': hex(d)}
    s.sendall((json.dumps(req) + '\n').encode())
    data = b''
    while True:
        try:
            chunk = s.recv(10000)
            if not chunk: break
            data += chunk
        except: break
    s.close()
    return json.loads(data.decode())

def parse_div_gcd(trace_str):
    """Extract the div GCD trace and return parsed TZ runs."""
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

def compute_x1_0_from_parity(parity_bits, N):
    """
    Given a list of parity bits (0=even, 1=odd) for TZ processing,
    compute the initial x1 value.
    
    x1 evolves: if bit=0, x1 = x1/2; if bit=1, x1 = (x1+N)/2.
    
    Working backwards: after b bits, we have:
    x1_final = (x1_0 + B * N) / 2^b
    where B is determined by the parity bits.
    
    If b >= 256 and x1_0 < N: x1_0 is uniquely determined.
    """
    # Iteratively narrow down x1_0
    # x1_0 is constrained by: for each parity bit, certain congruences hold
    
    # After each step j: x1_j = (x1_0 + B_j * N) / 2^j
    # where B_j is determined by first j parity bits.
    
    # The (j+1)th parity bit tells us: x1_j mod 2
    # If bit=0: x1_j is even → x1_j = 2 * x1_{j+1}
    # If bit=1: x1_j is odd → x1_j = 2 * x1_{j+1} - N
    
    # Working BACKWARDS from x1_b (unknown) to x1_0:
    # x1_0 = 2*x1_1 - b_0*N where b_0 = first parity bit
    # x1_1 = 2*x1_2 - b_1*N
    # ...
    # x1_{b-1} = 2*x1_b - b_{b-1}*N
    
    # x1_0 = 2^b * x1_b - N * (b_0 * 2^{b-1} + b_1 * 2^{b-2} + ... + b_{b-1})
    
    # Since x1_b < N (roughly), and x1_0 < N:
    # 2^b * x1_b - N * B ≡ x1_0 (mod N)
    # Actually, x1_b = (x1_0 + N * B) / 2^b
    # 
    # For 0 <= x1_0 < N:
    # 0 <= (x1_0 + N * B) / 2^b < N + N*B/2^b < ∞
    # But x1_b could be any non-negative value < N (approximate upper bound)
    
    # More precisely: x1_j for any j satisfies x1_j < N + (some small additional)
    # Actually x1_j should be in [0, N-1] after each step if we think of it mod N.
    # But as a regular integer, x1_j can be larger.
    
    # Let me just compute by simulating forward from a GUESS x1_0
    # and checking if the parity matches.
    
    # Actually, the approach: compute x1_0 by solving the congruence.
    # x1_b = (x1_0 + N * B) / 2^b
    # x1_b ≈ x1_0 / 2^b + N * B / 2^b
    # 
    # For x1_0 < N and b > log2(N):
    # x1_0 / 2^b < 1 (negligible)
    # So x1_b ≈ N * B / 2^b
    #
    # Since x1_0 < N and x1_b >= 0:
    # x1_b = (x1_0 + N * B - c * N * 2^b) / 2^b for some integer c >= 0
    # 
    # But x1_b also needs to be < N (from the algorithm's invariant)
    # So: (x1_0 + N * B) / 2^b - c * N < N
    #     (x1_0 + N * B) / 2^b < (c+1) * N
    #     x1_0 + N * B < (c+1) * N * 2^b
    #     
    # Since x1_0 < N:
    #     N * (B + 1) < (c+1) * N * 2^b
    #     B + 1 < (c+1) * 2^b
    #     c + 1 > (B + 1) / 2^b
    #
    # For b > log2(B): (B+1) / 2^b < 1, so c = 0.
    # B < 2^b (since B is a b-bit number). So for b > log2(N):
    # B + 1 < 2^b + 1, and (B+1) / 2^b < 1 + 1/2^b < 2
    # So c can be 0 or 1.
    
    # For c = 0: x1_b = (x1_0 + N * B) / 2^b
    # For c = 1: x1_b = (x1_0 + N * B) / 2^b - N
    
    # Since x1_0 < N:
    # (x1_0 + N * B) / 2^b - N < x1_b < (x1_0 + N * B) / 2^b
    # The lower bound: (0 + N * B) / 2^b - N = N * (B / 2^b - 1)
    # The upper bound: (N-1 + N * B) / 2^b ≈ N * (B + 1) / 2^b
    
    # For B ≈ 2^{b-1} (average case): x1_b ≈ N/2. Both c=0 and c=1 give valid results.
    
    # Hmm, this is getting complicated. Let me just try c=0 first and check.
    
    b = len(parity_bits)
    # Compute B from parity bits
    B = 0
    for bit in parity_bits:
        B = (B << 1) | bit
    
    # x1_b = (x1_0 + N * B) / 2^b for c=0
    # x1_0 = 2^b * x1_b - N * B
    
    # Without knowing x1_b, I can't determine x1_0 uniquely.
    # BUT: I know that x1_b is the result of further TZ processing.
    
    # After the u-phase: x1 = x1_end_u = (x1_0 + N * B) / 2^b
    # Then the first v-subtraction: x2 = -x1_end_u
    # Then v-TZ process x2.
    
    # The trace for the first v-TZ gives me the parity of x2.
    
    # NEW APPROACH: For each candidate x1_0 in the range:
    # Compute x1_end_u = (x1_0 + N * B) / 2^b
    # Then check: x2 = -x1_end_u, and the parity of x2 should match
    # the first v-TZ unit's a-value.
    
    # Since 2^b is large, only ONE value of x1_0 in [0, N-1] gives integer x1_end_u.
    
    # x1_end_u = (x1_0 + N * B) / 2^b
    
    # For this to be integer: x1_0 + N * B ≡ 0 (mod 2^b)
    # x1_0 ≡ -N * B (mod 2^b)
    
    # Since x1_0 < N < 2^b:
    # x1_0 = (-N * B) mod 2^b
    # 
    # Wait, if 2^b > N: x1_0 = (-N * B) % (2^b)
    # But x1_0 < N, so x1_0 = ((-N * B) % (2^b)) % N
    # Which equals x1_0 = (-N * B) % N = 0? No, that's wrong.
    
    # x1_0 = ((-N * B) mod 2^b) mod N? No, that's not right either.
    
    # Let me think: x1_0 ∈ [0, N-1].
    # x1_0 ≡ -N*B (mod 2^b). Since N*B is some random number, -N*B mod 2^b
    # is some value in [0, 2^b-1].
    
    # We need x1_0 ≡ (-N*B) mod 2^b (i.e., x1_0 - (-N*B) is divisible by 2^b).
    # x1_0 is in [0, N-1] where N < 2^b.
    
    # So x1_0 can be: (-N*B) mod 2^b, or (-N*B) mod 2^b + 2^b, etc.
    # BUT x1_0 < N < 2^b. So ONLY ONE possibility:
    # x1_0 = ((-N*B) % 2^b) if this is < N
    
    hmm = (-N * B) % (1 << b)
    if hmm < N:
        x1_0 = hmm
        x1_end_u = (x1_0 + N * B) // (1 << b)
        return x1_0, x1_end_u, False
    
    # If our assumption (c=0) is wrong, try c=1
    # x1_end_u = (x1_0 + N * B) / 2^b - N
    # x1_0 = 2^b * (x1_end_u + N) - N * B
    # x1_0 ≡ -N*B (mod 2^b) still holds
    
    # For c=1: x1_end_u = (x1_0 + N*B)/2^b - N >= 0
    # x1_end_u + N = (x1_0 + N*B)/2^b >= N
    # x1_0 >= N*(2^b - B)
    
    # Hmm, this makes x1_0 very large. But x1_0 < N. So c=1 => x1_0 >= N*(2^b - B) >= N (since 2^b > B).
    # Contradiction! So c=1 is impossible.
    
    # So the only valid c is 0, and:
    x1_0 = (-N * B) % (1 << b)
    if x1_0 >= N:
        # Need to wrap around: x1_0 = ((-N*B) % (1<<b)) % N
        # But that's the same as ((-N*B) % (1<<b)) - N? No.
        # x1_0 must be < N AND ≡ -N*B (mod 2^b).
        # Since 2^b > N, there's exactly 0 or 1 values in [0, N-1] with this congruence.
        # The value is ((-N*B) % 2^b) - N if >= N? No...
        
        # Actually if ((-N*B) % 2^b) >= N: there's NO valid x1_0 in [0, N-1].
        # This means our assumption about x1_end_u < N is wrong, and c > 0.
        
        # For c=1: x1_end_u = (x1_0 + N*B)/2^b - N
        # x1_0 + N*B = 2^b * (x1_end_u + N)
        # x1_0 = 2^b * (x1_end_u + N) - N*B
        # x1_0 ≡ -N*B (mod 2^b) (same congruence)
        
        # x1_0 >= N is required: N*B + 2^b * N - N*B = 2^b * N... hmm
        
        # x1_0 = 2^b * N - N*B + 2^b * x1_end_u
        # For x1_0 < N: 2^b * N - N*B + 2^b * x1_end_u < N
        # 2^b * N < N + N*B - 2^b * x1_end_u
        # For b > log2(N): 2^b > N. So 2^b * N > N.
        # This is impossible! So c must be 0.
        
        # If c=0 and (-N*B) % 2^b >= N: this means no solution.
        # But the algorithm MUST have some x1_0. Something's wrong.
        
        return None, None, True
    
    x1_end_u = (x1_0 + N * B) // (1 << b)
    return x1_0, x1_end_u, False

def solve():
    N = CURVE_N
    
    # Get one signature with trace
    print("Getting signature from server...")
    resp = get_sig_and_trace(['half', 'add', 'sub', 'div'])
    
    trace_list = resp.get('trace', [])
    trace_str = ''.join(trace_list)
    hash_int = int(resp['hash'], 16)
    r = int(resp['r'], 16)
    s_val = int(resp['s'], 16)
    
    print(f"hash: {hex(hash_int)[:30]}...")
    print(f"r: {hex(r)[:30]}...")
    print(f"s: {hex(s_val)[:30]}...")
    
    tz_runs = parse_div_gcd(trace_str)
    print(f"DIV TZ runs: {len(tz_runs)}")
    
    # Total TZ units
    total_units = sum(r['units'] for r in tz_runs)
    print(f"Total TZ units: {total_units}")
    
    # Try different K values (u-phase lengths)
    # Use estimated K ≈ total_units * 256 / (256 + log2(N)) ≈ total_units / 2
    for K_estimate in range(115, 145):
        K = K_estimate
        if K >= len(tz_runs):
            break
        
        # Get parity bits from first K runs
        parity_bits = []
        u_tz_counts = []
        for i in range(K):
            run = tz_runs[i]
            h = run['h']
            a = run['a']
            units = run['units']
            u_tz_counts.append(units)
            
            # Extract parity bits: each unit is either "hh" (even) or "hah" (odd)
            a_left = a
            for _ in range(units):
                if a_left > 0:
                    parity_bits.append(1)  # odd
                    a_left -= 1
                else:
                    parity_bits.append(0)  # even
        
        S = sum(u_tz_counts)
        if S < 256:  # Need enough TZ units to determine x1_0 uniquely
            continue
        
        # Compute x1_0 from parity bits
        b = len(parity_bits)
        B = 0
        for bit in parity_bits:
            B = (B << 1) | bit
        
        # x1_0 ≡ -N*B (mod 2^b), and x1_0 < N
        candidate_x1_0 = (-N * B) % (1 << b)
        
        if candidate_x1_0 >= N:
            continue
        
        x1_0 = candidate_x1_0
        x1_end_u = (x1_0 + N * B) // (1 << b)
        
        # Check: R = x1_0 * s^(-1) * 2^(-S) mod N = u_K mod N
        inv_s = pow(s_val, -1, N)
        inv_2S = pow(pow(2, S, N), -1, N)
        R = (x1_0 * inv_s % N) * inv_2S % N
        
        # u_K must be odd (since it's odd after TZ removal)
        if R % 2 == 0:
            continue
        
        # u_K ≡ N (mod 2^{t[K]}) where t[K] = v2(N - u_K)
        t_K = tz_runs[K]['units']
        
        if R % (1 << t_K) != N % (1 << t_K):
            continue  # Failed consistency check
        
        # Viable match found!
        u_K = R  # Since u_K < N and odd
        
        # Compute u_0 = u_K * 2^S + N * C
        # where C = 2^{S - u_tz_counts[0]} + 2^{S - u_tz_counts[0] - u_tz_counts[1]} + ... + 1
        C = 0
        running_S = 0
        for t in reversed(u_tz_counts):
            running_S += t
            C += 1 << running_S
        # Wait, I need to compute C differently
        # C = 2^{S - t_0} + 2^{S - t_0 - t_1} + ... + 2^{0}
        C = 0
        cum_tz = 0
        for t in reversed(u_tz_counts):
            cum_tz += t
            C += 1 << (cum_tz - 1)  # Hmm, this isn't right either
        
        # Let me recompute C carefully
        # u_0 = u_K * 2^S + N * (2^{S-t_0} + 2^{S-t_0-t_1} + ... + 1)
        # where t_i are the TZ counts for each u-phase run
        
        C = 0
        cum_remaining = 0
        for t in reversed(u_tz_counts):
            cum_remaining += t
            C += 1 << (cum_remaining - t)  # 2^{S - ...}
        # Or more simply: iterate forward
        C = 0
        cum_so_far = 0
        for t in u_tz_counts[:-1]:  # All except last
            cum_so_far += t
            C += 1 << (S - cum_so_far)
        C += 1  # The last term is 2^0 = 1
        
        u_0 = u_K * (1 << S) + N * C
        
        # Verify u_0 consistency
        # u_0 = m2 * k where k = (hash + r*d)/s mod N and m2 < N
        # Since we don't know d, verify: u_0 < N^2 (reasonable) and u_0 > 0
        
        if u_0 <= 0 or u_0 >= N * N:
            continue
        
        if u_0 % 2 != 0:
            continue  # u_0 must be even (denominator = m2 * k)
        
        # Also check: u_0 * s ≡ x1_0 (mod N)
        if (u_0 * s_val) % N != x1_0 % N:
            continue
        
        print(f"\n>>> CONSISTENT at K={K}! <<<")
        print(f"  S={S}, u_0 bits={u_0.bit_length()}")
        print(f"  x1_0 = {hex(x1_0)[:30]}...")
        print(f"  u_K = {hex(u_K)[:30]}...")
        print(f"  u_0 = {hex(u_0)[:30]}... ({u_0.bit_length()} bits)")
        
        # Now find d from u_0 and x1_0
        # u_0 = m2 * k, x1_0 = m2 * (hash + r*d) mod N
        # 
        # From ECDSA: k = (hash + r*d) * s^(-1) mod N
        # x1_0 = m2 * k * s mod N = u_0 * s mod N ✓ (already checked)
        #
        # m2 * (hash + r*d) ≡ x1_0 (mod N)
        # (hash + r*d) ≡ x1_0 * m2^(-1) (mod N) ... need m2
        #
        # u_0 = m2 * k (full product)
        # k is the nonce, an integer in [1, N-1]
        # m2 = u_0 / k must be integer
        #
        # k = (hash + r*d) * s^(-1) mod N = hash*s^(-1) + r*s^(-1)*d mod N
        #
        # From u_0 = m2 * ((hash + r*d) * s^(-1) mod N):
        # u_0 * s = m2 * (hash + r*d + t*N) for some integer t
        # u_0 * s - m2 * hash = m2 * r * d + m2 * t * N
        # m2 * r * d = u_0 * s - m2 * hash - m2 * t * N
        # d = (u_0 * s - m2 * hash - m2 * t * N) / (m2 * r)
        #
        # Since u_0 = m2 * k and k = (hash + r*d)/s mod N:
        # u_0 * s = m2 * (hash + r*d) + m2 * t * N
        # = m2 * hash + m2 * r * d + m2 * t * N
        # d = (u_0 * s - m2 * hash - m2 * t * N) / (m2 * r)
        #
        # For each divisor k of u_0 (k < N):
        #   m2 = u_0 / k
        #   d = (k * s - hash) * r^(-1) mod N
        #   Check: public key matches (via signature equation)
        
        print(f"  Attempting to find d by factoring u_0...")
        
        # Try small divisors of u_0 (since k < N might have special structure)
        # Check if k from ECDSA equation (with some d) divides u_0
        
        # Actually, let me try: d = (u_0 * s - m2 * hash) / (m2 * r) mod N
        # but this requires m2 and assumes t=0 in k = (hash + r*d)/s
        
        # For ANY divisor m2 of u_0:
        #   k = u_0 / m2
        #   d = (k * s - hash) * r^(-1) mod N
        #   Check: signature equation with d matches
        
        # Since u_0 < N^2: u_0 = m2 * k with m2, k < N
        # Both m2 and k are approximately 256 bits.
        
        # Without factoring u_0 (which is ~510 bits): this is hard.
        
        # But wait: k = (hash + r*d)/s mod N is in [0, N-1].
        # And m2 = u_0 / k (integer).
        
        # For WRONG d: k' != k (actual nonce), and u_0 % k' != 0.
        # For CORRECT d: u_0 % k == 0.
        
        # But I don't know d! However, I can search over d values
        # by checking u_0 % k == 0 where k = (hash + r*d)/s mod N.
        
        # For the CORRECT d: k divides u_0.
        # For a WRONG d: probability u_0 % k == 0 is 1/k ≈ 2^{-256}.
        
        # So if I try random d values and check u_0 % k == 0:
        # Each check has negligible false positive rate.
        
        # I just need to FIND d. Unless d has some special structure...
        
        # What if k is a SMALL value? Then I can try all k < some limit.
        # If k = actual nonce is small (e.g., < 2^30): brute-force by
        # trying all k and computing d = (k*s - hash) * r^(-1) mod N.
        
        print(f"  Checking if k (the nonce) is small...")
        for k_candidate in range(1, 100000):
            if u_0 % k_candidate == 0:
                m2 = u_0 // k_candidate
                if m2 < N:
                    d = (k_candidate * s_val - hash_int) * pow(r, -1, N) % N
                    # Verify
                    k_check = (hash_int + r * d) * pow(s_val, -1, N) % N
                    if k_check == k_candidate:
                        print(f"  >>> FOUND d = {hex(d)} <<<")
                        # Verify by submitting
                        result = submit_d(d)
                        print(f"  Submit: {result}")
                        if result.get('valid'):
                            print(f"  FLAG: {result.get('flag')}")
                            return d
        
        # Try if d is small instead
        print(f"  Checking if d is small...")
        for d_candidate in range(1, 100000):
            k = (hash_int + r * d_candidate) * pow(s_val, -1, N) % N
            if k < N and u_0 % k == 0:
                print(f"  >>> FOUND d = {hex(d_candidate)} <<<")
                result = submit_d(d_candidate)
                print(f"  Submit: {result}")
                if result.get('valid'):
                    print(f"  FLAG: {result.get('flag')}")
                    return d_candidate
    
    print("No solution found.")
    return None

if __name__ == '__main__':
    solve()
