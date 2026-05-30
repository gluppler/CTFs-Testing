#!/usr/bin/env python3
"""
Focused solver for Surprise-Factor.

The binary GCD of (denominator, N) where denominator = nonce_mask * k (FULL product, not mod N)
and x1 = nonce_mask * (hash + r*d) mod N.

We can reverse the binary GCD from the trace to find u = nonce_mask * k (full integer).
Then for each candidate d, we check if k = (hash + r*d)/s mod N divides u exactly.

If d is small (e.g. for CTF testing), we can brute-force.
"""
import json, socket, sys

HOST = '154.57.164.80'
PORT = 30118

N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

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

def forward_gcd(ops, result, modulus):
    """
    ops: list of (h_count, a_count) per TZ run, IN ORDER from the trace
    Result: s (the signature output)
    
    We need to determine:
    1. Which variable (u or v) each TZ run belongs to
    2. The subtraction direction at each step
    
    Approach: Try all possible subtraction direction sequences,
    constrained by consistency with the algorithm.
    
    For each TZ run, we know the number of TZ removed. Combined with
    the known u/v values (which we can track), we can determine
    the subtraction direction uniquely in most cases.
    
    Returns: (u_initial, x1_initial) or None
    """
    N = modulus
    
    # We'll work backwards from the final state
    # Final state: u=1, result = x1 (mod N), OR v=1, result = x2 (mod N)
    
    # Parse each TZ run into individual TZ removal steps with parity info
    tz_steps = []
    for h_count, a_count in ops:
        # h_count = 2 * n_even + 2 * n_odd = 2 * total_tz
        # a_count = n_odd (number of TZ where x was odd)
        total_tz = h_count // 2
        n_odd = a_count
        n_even = total_tz - n_odd
        
        # For reversal, we need to know WHICH x (x1 or x2) each 'a' belongs to
        # But we don't know this from the trace alone!
        # We'll determine this when we figure out the subtraction direction.
        
        # For each individual TZ step in order:
        # The h and a appear as: [h][h] or [h][a][h]
        # So we need to parse the actual sequence
        tz_steps.append((total_tz, n_odd))
    
    # Try to reverse from the end
    # We need to determine if u=1 or v=1 at the end
    # Try both possibilities
    
    def try_reverse(end_with_u):
        """Try ending with u=1 (True) or v=1 (False)."""
        if end_with_u:
            # u=1, result = x1 mod N
            x1 = result
            x2 = None  # unknown
            u = 1
            v = None  # unknown
        else:
            # v=1, result = x2 mod N
            x2 = result
            x1 = None  # unknown
            v = 1
            u = None  # unknown
        
        # Work backwards through TZ steps
        # Each TZ step processes one variable (u or v), halving it
        
        # This approach won't easily work without knowing v/u values...
        # Let me try a forward approach instead.
        return None
    
    return None

def reverse_gcd_forward(ops, modulus):
    """
    Simulate the binary GCD FORWARD using the TZ pattern.
    At each subtraction step, try both directions and check consistency.
    
    ops: list of (h_count, a_count) per TZ run
    modulus: N
    
    Returns list of possible (u_initial, x1_initial) values
    """
    # Step 1: Determine which variable each TZ run belongs to
    # In the binary GCD, we process u first, then v, then subtract
    # After subtraction, one variable is even -> process that one's TZ next
    
    # U initial is unknown. V always starts as modulus (N).
    # The first TZ run is for u (if u even) or doesn't exist (if u odd).
    
    # We'll use the APPROACH of tracking the possible u, v, x1, x2 values.
    from copy import deepcopy
    
    # State: list of possible (u, v, x1, x2, run_idx)
    # u and v are the actual integer values
    # x1 and x2 are the actual integer values
    # (u and v are positive, x1 and x2 can be negative)
    
    # Initially: u = ? (unknown), v = modulus, x1 = ?, x2 = 0
    # We'll maintain symbolic bounds and track possible values
    
    # Actually, let me try a different approach.
    # From the trace, we know:
    # - Total TZ count and number of odd-x TZ per run
    # - Number of runs = number of subtraction events
    
    # There are N runs and N subtractions (from the data).
    # We need to assign each run to either u or v, and determine
    # the subtraction direction.
    
    # APPROACH: Use the fact that the first run is ALWAYS for u.
    # And the algorithm always processes u BEFORE v in each iteration.
    # After each subtraction, exactly one variable changes (is even).
    # The next iteration processes that variable first.
    
    # So: if run i is for u, the subtraction is u >= v, and u changes.
    #     Next run i+1 is for u (since u is even from subtraction).
    # if run i is for v, the subtraction is v > u, and v changes.  
    #     Next run starts with u check (skip, u odd), then v check.
    #     Next run i+1 is for v (since v was made even).
    
    # This means: AFTER THE FIRST SUBTRACTION, the SAME variable keeps getting TZ runs!
    # Because the subtraction always makes ONE variable even, and that variable
    # gets TZ in the next iteration.
    
    # WAIT: after subtraction, one variable is even. The other is odd.
    # Next: process u first (skip if odd), then process v (skip if odd).
    # The EVEN variable always gets processed.
    
    # So: if u-even: tz for u, then v-skip, then subtract.
    #     if v-even: u-skip (u odd), then tz for v, then subtract.
    # After subtraction: one variable becomes even again.
    
    # So the TZ patterns alternate between u and v, NOT stay on the same one!
    
    # Wait, let me re-examine. After u >= v: 
    #   u = u - v (even) 
    # NEXT: process u TZ.
    # After: both odd. Subtract: u >= v or v > u depending.
    
    # After v > u:
    #   v = v - u (even)
    # NEXT: skip u (odd), process v TZ.
    # After: both odd. Subtract.
    
    # So the TZ pattern is: u, ss, u, ss, u, ss, ... until u < N
    # After u < N: v, ss, v, ss, v, ss, ... 
    # Then alternating: u, ss, v, ss, u, ss, v, ss, ...
    
    # Actually no. Let me re-examine.
    
    # After u >= v:
    # u changes, v stays
    # u = (odd-odd) = even, v = odd
    # Next: process u TZ -> u odd, v odd
    # Subtract: either u >= v or v > u
    
    # After v > u:
    # u stays, v changes
    # u = odd, v = (odd-odd) = even
    # Next: process v TZ -> u odd, v odd
    # Subtract: either u >= v or v > u
    
    # KEY: After processing TZ, BOTH are odd. The subtraction is determined
    # by which is larger.
    
    # So the pattern is:
    # - If the PREVIOUS subtraction was u >= v: current TZ is for u
    # - If the PREVIOUS subtraction was v > u: current TZ is for v
    # And after TZ processing: compare u and v to determine next subtraction.
    
    # This means the TZ RUNS DIRECTLY TELL US the subtraction direction!
    # tz_for_u => prev subtraction was u >= v
    # tz_for_v => prev subtraction was v > u
    
    # But we still need to determine EACH tz run's variable.
    # From the first run (if even) or first subtraction (if odd):
    # Initial u parity tells us if the first run exists.
    
    # From our data: TZ runs = subtraction events = 311.
    # This means either:
    # (a) u odd, no initial TZ. First op: subtraction (u >= N, since u large).
    #     Then 311 iterations of (tz_run, ss). But this gives 311 tz_runs and 310 ss.
    #     NO! This doesn't match.
    
    # (b) u even, initial TZ run. Then 310 iterations of (ss, tz_run).
    #     Then final ss. Total: 1+310 = 311 tz_runs. 310+1 = 311 ss pairs.
    #     YES! This matches!
    
    # So the pattern is:
    # tz_0 (initial, for u), ss_0 (u >= N), 
    # tz_1 (for u, from subtraction result), ss_1,
    # tz_2 (for u, from subtraction result), ss_2,
    # ..., 
    # tz_k (for u, from subtraction result), ss_k, [now u < N]
    # tz_{k+1} (for v, since v > u), ss_{k+1},
    # tz_{k+2} (for u or v, alternating), ...
    
    # The INITIAL tz is always for u (it's u's TZ before any subtraction).
    
    # So: run[0] = initial u TZ
    # Then: for i in 1..N-1:
    #     subtraction i-1 determines if run[i] is for u or v
    
    # To determine: the subtraction direction depends on the VALUES.
    # For the first many iterations: u >= N (since u ~ N^2, and TZ only removes
    # some bits). These are all u >= v subtractions. Runs 1..k are for u.
    
    # After u < N: v > u for one iteration (run for v), then v < u (run for u),
    # then they alternate.
    
    # In practice, the u >= v subtractions continue for O(log(u/N)) iterations.
    # Since u ≈ random in [0, N^2], the first iteration U -= N reduces u by N but
    # u is still ~ N^2. After about log2(N) ≈ 256 iterations, u drops below N^2/2^256 = N.
    
    # BUT each iteration ALSO removes TZ (halving u). So u decreases by roughly
    # 1 bit per iteration (from TZ) + N reduction.
    
    # The reduction is: u_i = u_{i-1} / 2^(t_i) - N (where t_i is TZ count)
    # ≈ u_{i-1} / 2 - N on average
    
    # Starting from ~2^511: after 1 iteration ≈ 2^510 - 2^256 ≈ 2^510
    # After ~255 iterations: u ≈ 2^511/2^255 - 255*2^256 ≈ 2^256
    # Now u ≈ N. The NEXT iteration: u < N or u >= N depending.
    
    # So about half the iterations are u >= N, and half are u < N.
    
    # Since total iterations ≈ 311: first ~155 are u >= N, rest alternate.
    
    # SIMPLER APPROACH: Instead of tracking values, just try ALL POSSIBLE
    # subtraction direction sequences and check which is consistent.
    
    # At each step, there are 2 choices (u>=v or v>u).
    # But most choices will lead to inconsistency.
    
    # With 311 steps, that's 2^311 possibilities. Way too many.
    
    # BUT: using the constraint that after each subtraction, the RESULT
    # is even (odd-odd=even), and the NEXT TZ run removes those TZ...
    # Wait, we know the TZ COUNT for each run! So we can NARROW it down.
    
    # Specifically: if the subtraction is u >= v:
    #   u_new = u_odd - v_odd = even
    #   v_new = v_odd
    #   t_next = v2(u_new)
    #   NEXT run is for u with t_next TZ
    # If the subtraction is v > u:
    #   v_new = v_odd - u_odd = even
    #   u_new = u_odd
    #   t_next = v2(v_new)
    #   NEXT run is for v with t_next TZ
    
    # So we know: if run[i] is for u with t_i TZ:
    #   Previous subtraction was u >= v: u_new = u_odd - v_odd, v2(u_new) = t_i
    #   AND: u_new >= v_odd (by the rule)
    # If run[i] is for v with t_i TZ:
    #   Previous subtraction was v > u: v_new = v_odd - u_odd, v2(v_new) = t_i
    #   AND: v_old > u (by the rule)
    
    # This gives a constraint on the values!
    # If I track possible ranges for u and v, I can constrain the direction.
    
    # But tracking exact values is hard because the TZ counts only give partial info.
    
    # APPROACH: Just assume the first k runs are for u (until u < N), then alternate.
    # Compute k from the total TZ counts.
    
    # For the initial: u = nonce_mask * k (unknown but < N^2)
    # After initial TZ: u_odd = u / 2^t₀
    # First subtraction (always u >= v since u_odd > N): u' = u_odd - N (even)
    # Next: run[1] removes TZ from u', giving u'_odd
    # Continue...
    
    # After enough subtractions: u drops below N. Then v > u for one step.
    # Then they alternate.
    
    # Let me just count the cumulative effect of TZ.
    # Each TZ run reduces u by a factor of ~2^t (on average). The subtraction
    # reduces u by N. We need about log2(u/N) ≈ 255 iterations of u >= v.
    
    # From the data: 311 iterations total. So ~255 u >= N, ~56 alternating.
    
    # Actually, the binary GCD of a 512-bit and 256-bit value takes about
    # O(n) = 256 steps total (where n = 256). Total iterations ≈ 256.
    # But we see 311. Hmm.
    
    # Let me just try both patterns and see which works.
    
    return []
    
print("Connecting...")

try:
    r = get_sig(["half", "add", "sub", "div"])
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

t = ''.join(r.get("trace", []))
div_pos = t.find('v')
if div_pos < 0:
    print("No div entry found!")
    sys.exit(1)

seg = t[div_pos + 1:]  # Skip 'v'

# Parse into runs
runs = []
i = 0
while i < len(seg):
    c = seg[i]
    if c == 's':
        i += 2  # skip ss pair
        runs.append(('sub', 0))
    elif c in 'ha':
        h_cnt = a_cnt = 0
        while i < len(seg) and seg[i] in 'ha':
            if seg[i] == 'h': h_cnt += 1
            elif seg[i] == 'a': a_cnt += 1
            i += 1
        runs.append(('tz', h_cnt, a_cnt))
    else:
        i += 1

# Now try to simulate the GCD
hash_int = int(r['hash'], 16)
r_val = int(r['r'], 16)
s_val = int(r['s'], 16)

print(f"hash: {hex(hash_int)}")
print(f"r: {hex(r_val)}")
print(f"s: {hex(s_val)}")
print(f"Total runs: {len(runs)}")

# Count tz and sub runs
tz_runs = [x for x in runs if x[0] == 'tz']
sub_runs = [x for x in runs if x[0] == 'sub']
print(f"TZ runs: {len(tz_runs)}, Subs: {len(sub_runs)}")

# First TZ run (if any) is for u
# Determine if initial u was even or odd
if runs[0][0] == 'tz':
    print(f"Initial TZ run: h={runs[0][1]}, a={runs[0][2]}")
    print(f"v2(initial u) = {runs[0][1] // 2}")
    initial_u_even = True
else:
    print("No initial TZ - u was odd!")
    initial_u_even = False

# Try to reconstruct using forward simulation
# Strategy: track possible ranges for u
# For the first ~255 iterations, u >= v, so direction is u >= v
# After u < N, the direction depends on the values

# APPROACH: Just try with the assumption that all subtractions are u >= v
# and see what initial u we get

# Simulate forward from initial u = unknown, v = N
# After each TZ run with t TZ: v = v (unchanged if u), u = u / 2^t (odd)
# After sub u >= v: u = u - v (even)

# We know from trace: how many TZ runs and subtractions
# For the reverse: start from u=1, v? and reverse

# Let me try the simplest approach: infer the subtraction direction from
# the TZ count pattern using the constraint:
# - For u >= v: after subtraction, u = u_odd - v_odd. v2(u-v) determines next TZ count.
# - The next TZ run's count must match v2(u-v)

# This means: if run[i] is for u, then v2(u_{i-1}_odd - v_{i-1}_odd) = TZ_count_of_run[i]

# Since we know TZ_count of each run, we can check consistency.
# But we don't know u and v values!

# ALTERNATIVE: Since u = nonce_mask * k (full product approximately random in [0, N^2]),
# and v = N (fixed), the first many iterations are deterministic given u.
# 
# Specifically: the number of u >= v iterations = number of times u stays above N.
# This is determined solely by u and the TZ counts.

# Let me just enumerate possible initial u values from the first few TZ runs!
# From the first run (t₀ TZ): u = u_init / 2^t₀ (odd)
# Subtract: u = u_odd - N (even). v2(u_odd - N) = t₁ (from second TZ run)
# So: u_init / 2^t₀ ≡ N (mod 2^t₁)

# Since u_init / 2^t₀ = u_odd:
# u_odd ≡ N (mod 2^t₁)
# u_odd = N + m * 2^t₁ (for odd m, since u_odd is odd)

# And u_init = u_odd * 2^t₀ = (N + m * 2^t₁) * 2^t₀

# The next subtraction:
# u_new = u_odd - N = m * 2^t₁ (even)
# After TZ removal: u_new_odd = m (odd, after dividing by 2^t₁)
# Then: u_new_odd >= N? If so, u_new_odd - N (even). v2(u_new_odd - N) = t₂

# So m >= N? (Since m = u_new_odd, if m >= N, subtraction is u >= v again)
# m = u_new / 2^t₁ = (u_odd - N) / 2^t₁ = m_original (the m from before)

# So m is some ODD number, and after removing t₁ TZ: m_odd = m (already odd)
# Then: if m >= N: m = m - N (even). t₂ = v2(m - N).
# if m < N: N > m, so N - m is even. t₂' = v2(N - m).

# This gives us a way to compute t₂ from t₀, t₁, and m.

# t₂ = v2(m - N) if m >= N, else v2(N - m)

# But m depends on u_init: m = (u_init/2^t₀ - N) / 2^t₁
# And u_init = nonce_mask * k

# I don't know u_init, but I can try solving for it.

# The key insight: u_init = nonce_mask * k is the product of two random values < N.
# Among such products, some are consistent with the TZ pattern and some aren't.

# With enough TZ runs (~311), the pattern should UNIQUELY determine u_init!

# Let me implement the search

def compute_initial_from_trace(ops, modulus, s_val, end_with_u=True):
    """
    Reverse the binary GCD given the TZ pattern.
    ops: list of (total_tz, n_odd) per run
    """
    N = modulus
    
    # Start from the end
    # End with u=1 or v=1
    if end_with_u:
        u = 1
        # x1 = s (mod N), but we need the actual x1 value
        x1 = s_val
        v = None
        x2 = None
    else:
        v = 1
        x2 = s_val
        u = None
        x1 = None
    
    # We need to track the FINAL state before the last operation
    # The last operation is either a TZ removal (making u=1 or v=1)
    # or a subtraction (making u=1 or v=1)
    
    # The trace tells us: TZ runs = subtraction events
    # So the pattern ends with: sub (or tz that makes u/v=1)
    
    # Case A: Last op is subtraction that makes u=1 or v=1
    #   Before: u_before - v_before = 1 (for u >= v)
    #   Or: v_before - u_before = 1 (for v > u)
    #   These were both odd before subtraction.
    
    # Case B: Last op is TZ that makes u=1 or v=1
    #   Before: u_before = 2 (even), halved to 1
    #   Or: v_before = 2 (even), halved to 1
    #   But then there would be no subtraction after this TZ, 
    #   meaning TZ runs = subs + 1, which doesn't match.
    
    # So Case A: the trace ends with a subtraction.
    # The very last 'ss' in the trace makes u=1 or v=1.
    
    return None

# Let me try a COMPLETELY different approach: use the brute-force for small d
# For small d, compute k, check if k divides u

# To test: get u from the trace by REVERSING
# But I need to solve the reversal first!
# Let me just check the actual TZ pattern

print(f"\nFirst 20 runs: {[(r[0], r[1] if r[0]=='tz' else '') for r in runs[:20]]}")
print(f"Last 10 runs: {[(r[0], r[1] if r[0]=='tz' else '') for r in runs[-10:]]}")

# Let me see if the TZ count decreases over time (as u decreases)
tz_counts = [(r[1]//2, r[2]) for r in tz_runs]  # (tz_count, odd_count)
print(f"First 10 TZ counts: {tz_counts[:10]}")
print(f"Last 10 TZ counts: {tz_counts[-10:]}")

# Check if there's a pattern change around the middle
mid = len(tz_counts) // 2
print(f"Middle TZ counts (around {mid}): {tz_counts[mid-5:mid+5]}")
