#!/usr/bin/env python3
"""Complete solver: reverse GCD trace by forward simulation for each K."""
import sys, os, json, socket
sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
from ec import N as CURVE_N
N = CURVE_N

def modinv(a, m): return pow(a, -1, m)

def parse_iterations(gcd_trace):
    """Parse h/a/s trace into iterations: [(total_tz, parity_bits), ...]"""
    iters = []
    i = 0
    while i < len(gcd_trace):
        units = []
        while i < len(gcd_trace) and gcd_trace[i] in 'ha':
            if gcd_trace[i] == 'h' and i+1 < len(gcd_trace) and gcd_trace[i+1] == 'a':
                units.append(1); i += 3
            elif gcd_trace[i] == 'h' and i+1 < len(gcd_trace) and gcd_trace[i+1] == 'h':
                units.append(0); i += 2
            else:
                i += 1
        if i < len(gcd_trace) and gcd_trace[i] == 's':
            i += 2
            if units: iters.append((len(units), units))
        elif units:
            iters.append((len(units), units))
            break
        else:
            i += 1
    return iters

def forward_simulate(u_0, x1_0, N, iters, K):
    """Forward-simulate the GCD given initial u_0 and x1_0.
    Returns (final_x1, final_u, final_v, matched) on success, or None.
    iters: [(total_tz, parity_bits), ...]
    K: number of iterations to treat as pure u-phase"""
    
    u = u_0
    v = N
    x1 = x1_0
    x2 = 0
    
    total_iters = len(iters)
    
    for it in range(total_iters):
        exp_tz, exp_parity = iters[it]
        
        # Count actual TZ of u and v
        utz = 0
        while u and (u & 1) == 0 and u != 1:
            u >>= 1
            parity = x1 & 1
            if parity:
                x1 = (x1 + N) >> 1
            else:
                x1 >>= 1
            utz += 1
        
        vtz = 0
        while v and (v & 1) == 0 and v != 1:
            v >>= 1
            parity = x2 & 1
            if parity:
                x2 = (x2 + N) >> 1
            else:
                x2 >>= 1
            vtz += 1
        
        actual_total = utz + vtz
        
        if actual_total != exp_tz:
            return None  # TZ counts don't match
        
        if u >= v:
            if u == v:
                u = 0
                break
            u -= v
            x1 -= x2
        else:
            v -= u
            x2 -= x1
    
    if u == 1:
        res = x1 % N
    elif v == 1:
        res = (-x2) % N
    elif u == 0:
        return None
    else:
        return None
    
    return (res, u, v)

def solve_for_K(iters, K, hash_int, r, s, N):
    """Try a candidate K for the u-phase length."""
    total_iters = len(iters)
    if K < 1 or K > total_iters:
        return None, None, None
    
    # Extract parity bits and TZ counts from first K iterations
    parity_bits = []
    tz_counts = []
    for i in range(K):
        tz, par = iters[i]
        tz_counts.append(tz)
        parity_bits.extend(par)
    
    b = len(parity_bits)
    S = sum(tz_counts)
    
    # x1_0 from parity bits
    B = sum(bit << i for i, bit in enumerate(parity_bits))
    x1_0 = (-N * B) % (1 << b)
    
    if x1_0 >= N:
        return None, x1_0, None
    
    # u_end from x1_0
    inv_s = modinv(s, N)
    inv_2S = modinv(pow(2, S, N), N)
    u_end = (x1_0 * inv_s % N) * inv_2S % N
    
    if u_end >= N or (u_end & 1) == 0:
        return None, x1_0, None
    
    # Backward reconstruct u_0 from u_end
    # For each u-phase iter (before transition): c = b - N, backward: a = (c + N) * 2^t
    # For transition iter: u unchanged, backward: a = u_end * 2^t
    u = u_end
    u *= (1 << tz_counts[-1])  # transition: no +N
    for t in reversed(tz_counts[:-1]):
        u = (u + N) * (1 << t)
    u_0 = u
    
    # Sanity check: u_0 should be ~512 bits
    if u_0.bit_length() < 490 or u_0.bit_length() > 530:
        return None, x1_0, u_0
    
    # Forward simulate and check result
    result = forward_simulate(u_0, x1_0, N, iters, K)
    if result is None:
        return None, x1_0, u_0
    
    res, u_end_val, v_end_val = result
    
    if res == s:
        return True, x1_0, u_0
    
    return None, x1_0, u_0

def solve_from_trace(trace, hash_int, r, s, N):
    """Find the correct K and recover GCD state."""
    trace_str = ''.join(trace)
    div_parts = trace_str.split('v')
    
    best_len = 0
    best_gcd = None
    for part in div_parts[1:]:
        if len(part) > best_len:
            best_len = len(part)
            best_gcd = part
    
    print(f"Best div: {best_len} chars")
    
    iters = parse_iterations(best_gcd)
    print(f"Total iterations: {len(iters)}")
    print(f"Total TZ units: {sum(it[0] for it in iters)}")
    
    for K in range(1, len(iters) + 1):
        success, x1_0, u_0 = solve_for_K(iters, K, hash_int, r, s, N)
        if success:
            print(f"K={K}: SUCCESS! x1_0={hex(x1_0)}, u_0={u_0.bit_length()}b")
            return {'x1_0': x1_0, 'u_0': u_0, 'K': K, 'iters': iters}
        elif K % 10 == 0:
            if u_0 is not None:
                total_tz = sum(iters[i][0] for i in range(K))
                print(f"  K={K}: fail, x1_0={hex(x1_0)[:30]}, u_0={u_0.bit_length()}b, tz={total_tz}")
            elif x1_0 is not None:
                total_tz = sum(iters[i][0] for i in range(K))
                print(f"  K={K}: fail, x1_0={hex(x1_0)[:30]}, u_0=None, tz={total_tz}")
            else:
                total_tz = sum(iters[i][0] for i in range(K))
                print(f"  K={K}: fail (early exit), tz={total_tz}")
    
    print("No K worked!")
    return None

def try_divisors(u_0, x1_0, hash_int, r, s, N, limit=200000):
    """Search small divisors of u_0 to find k = nonce."""
    for k_try in range(1, limit + 1):
        if u_0 % k_try == 0:
            m2 = u_0 // k_try
            if m2 < N:
                d_try = (k_try * s - hash_int) * modinv(r, N) % N
                kv = (hash_int + r * d_try) * modinv(s, N) % N
                if kv == k_try:
                    x1c = m2 * (hash_int + r * d_try) % N
                    if x1c == x1_0 % N:
                        return k_try, d_try
    return None, None

def main_local():
    """Local test."""
    sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
    from bignum import div
    from trace import TRACE
    
    d_test = 0x1337
    hash_int = 0x936062b5d1eab7ae33bd038260bc88f61bafda75d1b7f86c7455a5c810b20000
    r = 0xa23b92d900b788a44a1f03b6afe5f78b6ae497e47bfe9e03631e9d66427e9f03
    m2 = 0xfc6e91580c1936f44c3e4609a0aa10d0442e48c0facb84b74eca0effc2ebd7e0
    k = 0xfeadeedd779b203479d10e751b3c6fa1f50e85acc4ffc7e7d22cfcae0ba27228
    
    hd = hash_int + r * d_test
    numerator = m2 * hd
    denominator = m2 * k
    s = hd * pow(k, -1, N) % N
    
    print(f"denom bits: {denominator.bit_length()}")
    
    TRACE.configure({"half", "add", "sub", "div"})
    TRACE.reset()
    result = div(numerator, denominator, N)
    trace_list = TRACE.get_trace()
    
    print(f"result match s: {result == s}")
    
    info = solve_from_trace(trace_list, hash_int, r, s, N)
    if info is None:
        print("FAILED")
        return
    
    x1_0, u_0 = info['x1_0'], info['u_0']
    exp_x1 = (m2 * (hash_int + r * d_test)) % N  # a_mod = (nonce_mask * hd) % N
    print(f"\nx1_0 match: {x1_0 == exp_x1}")
    print(f"x1_0 = {hex(x1_0)[:50]}")
    print(f"exp  = {hex(exp_x1)[:50]}")
    print(f"u_0 match: {u_0 == denominator}")
    print(f"u_0  = {hex(u_0)[:50]}")
    print(f"den  = {hex(denominator)[:50]}")
    
    if x1_0 == exp_x1 and u_0 == denominator:
        print("\n*** FULL RECOVERY SUCCESSFUL ***")
        kf, df = try_divisors(u_0, x1_0, hash_int, r, s, N, 200000)
        if kf:
            print(f"d = {hex(df)}, expected = {hex(d_test)}, match: {df == d_test}")
        else:
            print(f"k = {hex(k)} ({k.bit_length()}b) not found by small-divisor search")

def get_sig(host, port, fns=None):
    if fns is None: fns = ["add", "sub", "half", "div"]
    req = json.dumps({"action": "sign", "track": fns}) + "\n"
    s = socket.socket(); s.settimeout(30)
    s.connect((host, port))
    s.sendall(req.encode())
    data = b""
    while True:
        try:
            c = s.recv(4096)
            if not c: break
            data += c
            if b"\n" in data: break
        except: break
    s.close()
    return json.loads(data.decode())

def submit(host, port, d):
    req = json.dumps({"action": "submit", "d": hex(d)}) + "\n"
    s = socket.socket(); s.settimeout(30)
    s.connect((host, port))
    s.sendall(req.encode())
    data = b""
    while True:
        try:
            c = s.recv(4096)
            if not c: break
            data += c
            if b"\n" in data: break
        except: break
    s.close()
    return json.loads(data.decode())

def main_remote():
    host, port = "154.57.164.80", 30118
    print("Getting signature...")
    resp = get_sig(host, port)
    if "error" in resp:
        print(f"Error: {resp['error']}")
        return
    
    hash_int = int(resp["hash"], 16)
    r = int(resp["r"], 16)
    s = int(resp["s"], 16)
    trace = resp["trace"]
    print(f"trace len: {len(trace)}")
    
    info = solve_from_trace(trace, hash_int, r, s, N)
    if info is None:
        print("FAILED")
        return
    
    u_0 = info['u_0']
    x1_0 = info['x1_0']
    print(f"\nu_0 bits: {u_0.bit_length()}")
    
    kf, df = try_divisors(u_0, x1_0, hash_int, r, s, N, 100000)
    if kf:
        print(f"Found: d={hex(df)}")
        sr = submit(host, port, df)
        print(f"Submit: {sr}")
        if sr.get("flag"):
            print(f"\n*** FLAG: {sr['flag']} ***")
        return
    
    # Try small prime divisors
    for p in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
        if u_0 % p == 0:
            k_try = p; m2 = u_0 // p
            if m2 < N:
                d_try = (k_try * s - hash_int) * modinv(r, N) % N
                if (hash_int + r * d_try) * modinv(s, N) % N == k_try:
                    if (m2 * (hash_int + r * d_try)) % N == x1_0 % N:
                        print(f"p={p}: d={hex(d_try)}")
                        sr = submit(host, port, d_try)
                        print(f"Submit: {sr}")
                        if sr.get("flag"):
                            print(f"\nFLAG: {sr['flag']}")
                            return

if __name__ == "__main__":
    if sys.argv[1:2] == ["remote"]:
        main_remote()
    else:
        main_local()
