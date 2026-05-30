#!/usr/bin/env python3
"""
Complete solver for Surprise Factor.
Strategy: reverse the binary GCD from the div operation trace,
extract u=denominator, check divisibility by k=(hash+r*d)/s mod N.
"""
import sys, os, socket, json, secrets

sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
from ec import N as CURVE_N
from bignum import _binary_division_odd_modulus
from trace import TRACE

def connect_and_sign(track_fns, host='154.57.164.80', port=30118):
    s = socket.socket()
    s.settimeout(30)
    s.connect((host, port))
    req = {'action': 'sign', 'track': track_fns}
    s.sendall((json.dumps(req) + '\n').encode())
    data = b''
    while True:
        try:
            chunk = s.recv(1000000)
            if not chunk: break
            data += chunk
            if data.count(b'\n') > 0: break
        except: break
    s.close()
    return json.loads(data.decode())

def connect_and_submit(d, host='154.57.164.80', port=30118):
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

# Local test first
def run_local_test():
    """Test solver end-to-end with local bignum module."""
    from ec import N as N_EC
    
    # Generate a "private key" (small for test)
    d = 0x1337
    m2 = 0x42  # second nonce_mask (small for test)
    k = 0xdeadbeef  # nonce (small for test)
    
    hash_int = secrets.randbelow(N_EC)
    r = secrets.randbelow(N_EC)
    
    numerator = (hash_int + r * d) * m2 % N_EC
    denominator = m2 * k
    
    print(f"d={hex(d)}, m2={hex(m2)}, k={hex(k)}")
    print(f"denominator={denominator} ({denominator.bit_length()} bits)")
    
    TRACE.configure({"half", "add", "sub"})
    TRACE.reset()
    s = _binary_division_odd_modulus(numerator, denominator, N_EC)
    trace_str = ''.join(TRACE.get_trace())
    
    expected_s = (hash_int + r * d) * pow(k, -1, N_EC) % N_EC
    print(f"s={hex(s)}, expected={hex(expected_s)}, match={s==expected_s}")
    print(f"Trace: h={trace_str.count('h')}, a={trace_str.count('a')}, s={trace_str.count('s')}")
    
    # Parse trace
    runs = []
    i = 0
    while i < len(trace_str):
        if trace_str[i] == 's':
            runs.append(('sub',))
            i += 2
        elif trace_str[i] in 'ha':
            h = a = 0
            while i < len(trace_str) and trace_str[i] in 'ha':
                if trace_str[i] == 'h': h += 1
                elif trace_str[i] == 'a': a += 1
                i += 1
            runs.append(('tz', h, a))
        else:
            i += 1
    
    tz_runs = [r for r in runs if r[0] == 'tz']
    total_tz_units = sum(r[1] for r in tz_runs) // 2
    print(f"TZ runs: {len(tz_runs)}, total TZ units: {total_tz_units}")
    
    # Test: reconstruct u from the u-phase
    # First, find where v becomes even (u-phase ends)
    # For a test with small values: denominator = 0x42 * 0xdeadbeef = 0x38e0e8bce
    
    print(f"\nUsing manual GCD to determine phase boundary...")
    
    # Manual GCD tracking
    u, v = denominator, N_EC
    x1_tz_pattern = []
    was_u_phase = True
    u_phase_tz_counts = []
    v_phase_tz_counts = []
    
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
        
        if was_u_phase and u_tz > 0:
            u_phase_tz_counts.append(u_tz)
        elif was_u_phase and v_tz > 0:
            was_u_phase = False
            print(f"  v-phase starts at step {step} with tz={v_tz}")
            v_phase_tz_counts.append(v_tz)
        elif not was_u_phase and v_tz > 0:
            v_phase_tz_counts.append(v_tz)
        elif not was_u_phase and u_tz > 0:
            pass  # u gets TZ too in alternating phase
        
        if u >= v:
            if u != v: u -= v
            else: u = 0; break
        else:
            v -= u
        
        step += 1
    
    print(f"u-phase TZ counts (first {len(u_phase_tz_counts)}): {u_phase_tz_counts}")
    print(f"Total u-phase runs: {len(u_phase_tz_counts)}")
    
    # Now reconstruct u_0 from the u-phase
    # u_i = (u_{i-1} - N) / 2^{t_i}
    # Working backwards from u_switch (unknown odd value < N):
    # u_0 = u_switch * 2^S + N * sum_terms
    
    # For a TEST where I know the actual u_0:
    # Can I check that the reconstructed u_0 (for some u_switch) matches?
    
    # For small values: denominator = 0x42 * 0xdeadbeef = 0x38e0e8bce = 15279383494
    # But with N ≈ 2^256, the u-phase has many iterations.
    # Let me check: is u_0 really m2 * k?
    
    actual_u0 = m2 * k
    print(f"\nActual u_0 = m2 * k = {actual_u0} = {hex(actual_u0)}")
    
    # For SMALL m2, k values: the denominator is ~64 bits
    # N is 256 bits. So u < v from the start!
    # This means there's NO u-phase at all! The first comparison is v > u.
    
    print(f"N = {N_EC}")
    print(f"Is u_0 < N? {actual_u0 < N_EC}")
    
    # For small values: u_0 < N, so the algorithm starts with v > u immediately.
    # This wouldn't match the REAL server (where m2 and k are both ~256 bits).
    
    print(f"\nRe-run with 256-bit values...")
    m2_big = int.from_bytes(os.urandom(32), 'big') % N_EC
    if m2_big == 0: m2_big = 1
    k_big = int.from_bytes(os.urandom(32), 'big') % N_EC
    if k_big == 0: k_big = 1
    
    denominator_big = m2_big * k_big
    print(f"Big denominator: {denominator_big.bit_length()} bits")
    
    # Manual GCD
    u, v = denominator_big, N_EC
    u_phase_runs = 0
    v_first = None
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
        
        has_v_tz = v_tz > 0
        if v_first is None and has_v_tz:
            v_first = step
        
        if u >= v:
            if u != v: u -= v
            else: u = 0; break
        else:
            v -= u
        step += 1
    
    print(f"Total steps: {step}, First v-TZ at step: {v_first}")
    print(f"u-phase runs (steps with only u-TZ): {v_first}")
    
    return None

if __name__ == '__main__':
    run_local_test()
    
    # Also try connecting to server
    print("\n\n=== Trying server connection ===")
    result = connect_and_sign(['half'])
    h = result.get('trace', '').count('h')
    print(f"Server hash: {result.get('hash')}")
    print(f"Server trace len: {len(result.get('trace', []))}")
    print(f"Server h count: {h}")
    print(f"Server pubkey: {result.get('public_key')}")
