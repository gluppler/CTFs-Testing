#!/usr/bin/env python3
"""
Surprise-Factor solver.
Strategy: reverse the binary GCD from the trace to recover
the full initial state (x1 = numerator, u = denominator).
Then use x1 = nonce_mask * (hash + r*d) mod N and u = nonce_mask * k
to extract the private key d.

Key insight: u = nonce_mask * k is the FULL product (not mod N),
and x1 = nonce_mask * (hash + r*d) mod N.
Since u is NOT reduced mod N, we can learn more about k.

Another insight: from two signatures, we can set up equations to solve for d.
"""
import json, socket

HOST = '154.57.164.80'
PORT = 30118

N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF

def get_sig(track):
    s = socket.socket()
    s.settimeout(20)
    s.connect((HOST, PORT))
    s.sendall((json.dumps({"action": "sign", "track": track}) + '\n').encode())
    buf = b''
    while True:
        c = s.recv(1)
        if not c: break
        buf += c
        if c == b'\n': break
    s.close()
    return json.loads(buf.decode())

def parse_div_trace(seg):
    """
    Parse the binary GCD trace for div segment.
    Returns list of (tz_count, add_count) tuples, one per TZ run.
    """
    # We see: tz operations (h, a), then ss, then repeats
    ops = []
    i = 0
    while i < len(seg):
        c = seg[i]
        if c == 'v':
            i += 1
            continue
        if c == 's':
            # ss pair = subtraction
            # We record the last TZ run info
            i += 2
            continue
        if c == 'h' or c == 'a':
            # TZ run: count h and a
            h_count = 0
            a_count = 0
            while i < len(seg) and seg[i] in 'ha':
                if seg[i] == 'h':
                    h_count += 1
                elif seg[i] == 'a':
                    a_count += 1
                i += 1
            ops.append((h_count, a_count))
        else:
            i += 1
    return ops

def verify_gcd(ops):
    """Check if parsed ops make sense."""
    for h, a in ops:
        # Each TZ removal is either hh (even x) or hah (odd x)
        # So total h = 2 * tz_count, and total a = number of odd-x TZ
        assert h >= 2 * a, f"Invalid: h={h}, a={a}"
        # All remaining h after accounting for hh+ hah must be divisible...
        # Actually each "hh" is 2h and each "hah" is 2h+1a
        # So h = 2*even_tz + 2*odd_tz = 2*(even_tz + odd_tz) = 2 * tz_count
        # and a = odd_tz
        assert h % 2 == 0, f"Odd total h: {h}"
        assert a <= h // 2, f"a > h/2: h={h}, a={a}"
    # Verify total TZ format across all runs
    total_h = sum(h for h, a in ops)
    total_a = sum(a for h, a in ops)
    total_tz = total_h // 2
    print(f"Total: TZ removals={total_tz}, odd ratio={total_a/total_tz*100:.1f}%")
    print(f"Runs: {len(ops)}")
    return True

def half(x, odd_flag, modulus):
    """Reverse of the halving in binary GCD.
    If odd_flag is True, x was odd, so we had: x = (x + modulus) / 2
    If odd_flag is False, x was even, so we had: x = x / 2
    
    We want to reverse: given x_after, find x_before.
    """
    if odd_flag:
        # x_after = (x_before + modulus) / 2
        # So x_before = 2 * x_after - modulus
        return 2 * x - modulus
    else:
        # x_after = x_before / 2
        return 2 * x

def reverse_gcd(ops, result, modulus):
    """
    Reverse the binary GCD to find initial x1 and u (and x2 and v).
    ops: list of (h_count, a_count) per TZ run
    result: final value (s for div)
    modulus: N for div
    
    Returns (u_initial, v_initial, x1_initial, x2_initial)
    """
    # We don't know if the algorithm ended with u=1 or v=1
    # Try both possibilities
    pass  # TODO

print("Getting sample traces...")

# Get a signature with half+add+sub+div for detailed analysis
r1 = get_sig(["half", "add", "sub", "div"])
t1 = ''.join(r1.get("trace", []))
div_pos = t1.find('v')

hash_int1 = int(r1['hash'], 16)
r_val1 = int(r1['r'], 16)
s_val1 = int(r1['s'], 16)

print(f"Sample 1:")
print(f"  hash: {hex(hash_int1)}")
print(f"  r: {hex(r_val1)}")
print(f"  s: {hex(s_val1)}")

seg1 = t1[div_pos:]
ops1 = parse_div_trace(seg1)
verify_gcd(ops1)

# Get a second sample
r2 = get_sig(["half", "add", "sub", "div"])
t2 = ''.join(r2.get("trace", []))
div_pos2 = t2.find('v')

hash_int2 = int(r2['hash'], 16)
r_val2 = int(r2['r'], 16)
s_val2 = int(r2['s'], 16)

print(f"\nSample 2:")
print(f"  hash: {hex(hash_int2)}")
print(f"  r: {hex(r_val2)}")
print(f"  s: {hex(s_val2)}")

seg2 = t2[div_pos2:]
ops2 = parse_div_trace(seg2)
verify_gcd(ops2)

# Print the TZ run details for first few runs of sample 1
print(f"\nFirst 15 TZ runs (h_count, a_count): {ops1[:15]}")
print(f"Total runs: {len(ops1)}")

# Each run is a group of consecutive TZ removals from ONE variable (u or v)
# In the initial iterations (while u >= N), all TZ are from u
# After u < N, TZ alternate between v and u

# The FIRST run's TZ count = v2(initial u = nonce_mask * k)
# This tells us the exponent of 2 in the initial denominator
tz_first = ops1[0]
print(f"\nFirst TZ run: h={tz_first[0]}, a={tz_first[1]}")
print(f"Initial TZ count = v2(denominator) = {tz_first[0] // 2}")
print(f"First run odd ratio: {tz_first[1]}/{tz_first[0]//2}")

# Key insight: during the first run, x2 = 0 (always even), so no 'a' comes from x2
# All 'a' in the first run are from x1 parity
# x1 starts as: numerator = nonce_mask * (hash + r*d) mod N
# After each TZ removal: x1 = x1 * 2^(-1) mod N

# So the 'a' pattern in the first run tells us about x1's parity after repeated halving
# This lets us determine x1 mod 2^k

# Let's try to reconstruct x1 from the parity info
def reconstruct_x1_from_parity(a_pattern, modulus):
    """
    Given the 'a' pattern for x1 during continuous TZ removals (no x2 interference),
    reconstruct x1.
    
    For each TZ removal i (from 0):
      x1_{i+1} = x1_i * 2^(-1) mod modulus
      a_i = 1 if x1_i was odd, 0 if x1_i was even
    
    We know x1_final (after all removals) = ? 
    Actually we need the total sequence. But for the FIRST run, 
    x1 starts as initial numerator and gets halved t times.
    
    We can reconstruct x1 modulo 2^(t+1) from the parity sequence.
    """
    # x1_i = x1_0 * 2^(-i) mod modulus
    # x1_i is odd iff a_i = 1
    # x1_i mod 2 = (x1_0 * 2^(-i) mod modulus) mod 2
    # Since modulus (N) is odd, 2^(-i) mod modulus is just some odd number
    # Specifically, 2^(-1) mod N = (N+1)/2 (since 2 * (N+1)/2 = N+1 ≡ 1 mod N)
    # and 2^(-i) = ((N+1)/2)^i mod N
    
    # Actually, x1_i = x1_0 * ((N+1)/2)^i mod N
    # The parity of x1_i depends on x1_0 mod 2 (and on i)
    # Since ((N+1)/2)^i ≡ 2^(-i) (mod N), and 2^(-i) is odd when i = 0, 
    # and even when i >= 1 (because 2^(-1) mod N = (N+1)/2 which is odd only if N ≡ 1 mod 4)
    
    # N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    # N mod 4 = 1 (since N is odd)
    # So (N+1)/2 mod 2 = (N+1)/2 & 1 = (N+1)//2 % 2 = 
    # N+1 = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632552
    # (N+1)//2 = 0x7FFFFFFF800000007FFFFFFFFFFFFFFFDE737D56D38BCF4279CE56167E3192A9
    # This is ODD (ends in 9)
    
    # So 2^(-1) mod N is ODD. And 2^(-i) mod N is also ODD for all i.
    # Therefore, x1_i = x1_0 * odd mod N.
    # x1_i mod 2 = (x1_0 mod 2) * (odd mod 2) = x1_0 mod 2.
    # WRONG! This isn't right because the mod N operation can change parity.
    
    # Let me think again. x1_i = x1_0 * inv2^i mod N.
    # inv2 = (N+1)/2 (since 2 * (N+1)/2 = N+1 ≡ 1 mod N)
    # inv2^i = inv2^i mod N
    # x1_i = (x1_0 * inv2^i) mod N
    # x1_i mod 2 = (x1_0 * inv2^i) mod 2
    
    # Since inv2^i is odd and N is odd:
    # x1_i mod 2 = x1_0 mod 2 (if x1_0 < N) NO because mod N can flip parity
    
    # Actually, x1_0 < N, and inv2^i < N, and product < N^2
    # After mod N: (x1_0 * inv2^i) mod N = (x1_0 * inv2^i) - floor(x1_0 * inv2^i / N) * N
    # mod 2: this is x1_0 * inv2^i mod 2 - floor(x1_0 * inv2^i / N) * N mod 2
    # = (x1_0 mod 2) * (inv2^i mod 2) - (floor(x1_0 * inv2^i / N) mod 2) * (N mod 2) mod 2
    # = x1_0 mod 2 - (floor(x1_0 * inv2^i / N) mod 2) mod 2 (since both N and inv2 are odd)
    # = (x1_0 mod 2) XOR (floor(fraction) mod 2)
    
    # This depends on BOTH x1_0 and the floor term. Very complex.
    
    # Instead, let me use a simpler approach.
    # After the first run, we have x1_after = x1_initial * 2^(-t) mod N
    # where t = tz_count.
    # And the 'a' pattern tells us the parity of x1 at each intermediate step.
    
    # The simple way: each 'a' means x1_before was odd.
    # x1_before = x1_after * 2^1 mod N (reversing the halving)
    # So if a_i = 1: (x1_after * 2^i mod N) mod 2 = 1 for some point i
    
    # But this doesn't easily give us x1_initial directly.
    
    # Let me try a DIFFERENT approach. 
    # I'll brute-force over possible values of the first few TZ of x1.
    # Each TZ removal either halves x1 (if even) or (x1+N)/2 (if odd).
    # Given the parity info, I can reconstruct x1 modulo 2^t where t is the # of TZ.
    
    # Starting from x1_after (unknown), work backwards:
    # For each step: x1_before = (x1_after * 2 - odd * N)
    # where odd is 1 if a_i = 1, 0 otherwise
    
    # So x1_initial = x1_after * 2^t - N * sum(odd_i * 2^(t-1-i))
    # modulo N: x1_after * 2^t ≡ x1_initial (mod N)
    
    # But x1_after / 2^t ≡ x1_initial * 2^(-t) (mod N)?
    # Wait, I'm confusing forward and reverse.
    
    # Forward: x1_{i+1} = (x1_i + a_i * N) / 2
    # Reverse: x1_i = 2 * x1_{i+1} - a_i * N
    
    # So: x1_0 = 2^t * x1_t - N * sum(a_i * 2^(t-1-i))
    
    # x1_t is the x1 value after all t TZ removals in the run.
    # This is also x1 before the subtraction.
    
    pass

# Get the public key
print(f"\nPublic key x: {r1.get('public_key', {}).get('x', 'N/A')}")
print(f"Public key y: {r1.get('public_key', {}).get('y', 'N/A')}")
