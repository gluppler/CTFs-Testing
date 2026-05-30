#!/usr/bin/env python3
import socket, time, sys
from math import gcd, isqrt

HOST = '154.57.164.64'
PORT = 30994

def connect():
    s = socket.socket()
    s.settimeout(30)
    s.connect((HOST, PORT))
    return s

def recv_all(s, timeout=2):
    data = b""
    s.settimeout(timeout)
    while True:
        try:
            chunk = s.recv(65536)
            if not chunk:
                break
            data += chunk
        except socket.timeout:
            break
    return data.decode(errors='replace')

def send_line(s, msg):
    s.sendall((str(msg) + '\n').encode())
    time.sleep(0.5)

def convergents(num, den):
    a, b = num, den
    cf = []
    while b:
        q = a // b
        cf.append(q)
        a, b = b, a % b
    h0, h1 = 0, 1
    k0, k1 = 1, 0
    for q in cf:
        h2 = q * h1 + h0
        k2 = q * k1 + k0
        yield h2, k2
        h0, h1 = h1, h2
        k0, k1 = k1, k2

def find_r(primes):
    for i in range(len(primes)):
        for j in range(i+1, len(primes)):
            p0, p1 = primes[i], primes[j]
            for a0, a1 in convergents(p0, p1):
                if a0 >= 2**384 or a1 >= 2**384:
                    continue
                if a0 == 0 or a1 == 0:
                    continue
                r = max(p0 // a0, p1 // a1)
                if r.bit_length() > 650 or r.bit_length() < 600:
                    continue
                if p0 % r < 2**256 and p1 % r < 2**256:
                    if all(p % r < 2**256 for p in primes):
                        return r
    return None

s = connect()
data = recv_all(s)
print("BANNER:", repr(data[:200]))

# Collect primes
primes = []
for _ in range(15):
    send_line(s, 1)
    resp = recv_all(s)
    for line in resp.split('\n'):
        line = line.strip()
        if line and line[0].isdigit() and len(line) > 200:
            primes.append(int(line))
            break

print(f"\nCollected {len(primes)} primes")

# Get RSA params
send_line(s, 3)
resp3 = recv_all(s)
print(f"Option 3 raw: {resp3[:300]}")

n, e, c = None, None, None
for line in resp3.split('\n'):
    line = line.strip()
    if '(' in line and ')' in line:
        start = line.find('(')
        end = line.rfind(')') + 1
        n, e, c = eval(line[start:end])
        break

if n is None:
    print("Failed to parse n, e, c!")
    print("Full response:", resp3)
    sys.exit(1)

print(f"n bits: {n.bit_length()}")
print(f"e = {e}")

# Find r
r = find_r(primes)
if r is None:
    print("Failed to find r!")
    sys.exit(1)
print(f"r = {r}")
print(f"r bits: {r.bit_length()}")

ab_pairs = [(p // r, p % r) for p in primes]

# Try approach: maybe option 2 sets the RSA key, not AES key
# And when we call option 3, it uses the "updated" key
# So: generate primes, then option 2 with the generated primes,
# then option 3 encrypts with our key

# Actually, let me try: what if option 3's (n, e, c) is the RSA encryption
# of the flag itself, and we just need to factor n using the 
# knowledge that n = (a1*b1 + r) * (a2*b2 + r) ... no that's not right

# Let me try to factor n given r
# n = (a1 * r + b1) * (a2 * r + b2)
# n_r = b1 * b2 (exact since < r)
# n_q2 = n // (r*r) = a1 * a2 (approx)

n_r = n % r
n_q2 = n // (r * r)

print(f"\nn_r = n % r = {n_r}")
print(f"n_r bits: {n_r.bit_length()}")
print(f"n_q2 = n // r^2 = {n_q2}")
print(f"n_q2 bits: {n_q2.bit_length()}")

# Factor n_r: two numbers < 2^256 whose product is n_r
# For 511-bit number, both factors must be roughly 255-256 bits
# This is hard with basic methods but let me try Pollard rho more aggressively
# and also check if n_r has small factors

def factor_ecm(n, limit=200000):
    """Pollard's rho with Brent's improvement"""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    y, c, m = 1, 1, 100
    g, r, q = 1, 1, 1
    while g == 1 and r <= limit:
        x = y
        for _ in range(r):
            y = (y * y + c) % n
        k = 0
        while k < r and g == 1 and r <= limit:
            ys = y
            for _ in range(min(m, r - k)):
                y = (y * y + c) % n
                q = q * abs(x - y) % n
            g = gcd(q, n)
            k += m
        r *= 2
    if g == n:
        while True:
            ys = (ys * ys + c) % n
            g = gcd(abs(x - ys), n)
            if g > 1:
                break
    return g if g != n else None

fac = factor_ecm(n_r, 1000000)
if fac:
    fac2 = n_r // fac
    print(f"\nFactored n_r = {fac} * {fac2}")
    
    for bL, bR in [(fac, fac2), (fac2, fac)]:
        if bL.bit_length() > 260 or bR.bit_length() > 260:
            continue
        
        T = (n - bL * bR) // r
        M = T // r
        
        for offset in range(-10, 11):
            M2 = M + offset
            if M2 <= 0:
                continue
            
            # Try each known a value
            for aL, _ in ab_pairs:
                if M2 % aL == 0:
                    aR = M2 // aL
                    if aR.bit_length() > 385:
                        continue
                    
                    for (bbL, bbR) in [(bL, bR), (bR, bL)]:
                        p_try = aL * r + bbL
                        q_try = aR * r + bbR
                        if n == p_try * q_try:
                            print(f"\nFACTORED n!")
                            d = pow(e, -1, (p_try - 1) * (q_try - 1))
                            m = pow(c, d, n)
                            try:
                                m_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
                                print(f"FLAG: {m_bytes}")
                            except:
                                print(f"m = {m}")
                            sys.exit(0)
else:
    print("Failed to factor n_r with Pollard's rho")

# Alternative: maybe n doesn't use the same r at all
# Let me try a completely different approach
print("\nAlternative approaches:")

# 1. Check if any two primes have gcd > 1
for i in range(len(primes)):
    for j in range(i+1, len(primes)):
        g = gcd(primes[i], primes[j])
        if g > 1:
            print(f"gcd(p{i}, p{j}) = {g}")

# 2. Maybe n is the product of two consecutive primes we generated
print("Checking if any pair of generated primes product = n...")
for i in range(len(primes)):
    for j in range(i, len(primes)):
        if primes[i] * primes[j] == n:
            print(f"FOUND: n = p{i} * p{j}")
            d = pow(e, -1, (primes[i]-1)*(primes[j]-1))
            m = pow(c, d, n)
            m_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
            print(f"FLAG: {m_bytes}")
            sys.exit(0)

print("n is not product of any two generated primes")

# 3. Try option 2 with various inputs
s2 = connect()
data = recv_all(s2)

# Try option 2 with hex zero
send_line(s2, "2")
time.sleep(0.5)
prompt = recv_all(s2, timeout=2)
print(f"\nOption 2 prompt: {repr(prompt[:200])}")

# Send a 32-byte zero hex key
send_line(s2, "00" * 32)
time.sleep(0.5)
resp = recv_all(s2, timeout=3)
print(f"After sending key: {repr(resp[:300])}")

# Now option 3
send_line(s2, "3")
time.sleep(0.5)
resp3_2 = recv_all(s2, timeout=3)
print(f"Option 3 after key update: {repr(resp3_2[:300])}")

s2.close()

# 4. Try option 2 with our own key that we control
# If option 2 sets the AES key, and we provide a hex-encoded key,
# then option 3 should give us the flag encrypted with our key

print("\nTrying another approach for option 2...")
s3 = connect()
data = recv_all(s3)

# Try option 2 with a decimal integer 0
send_line(s3, "2")
time.sleep(0.5)
_ = recv_all(s3, timeout=2)
send_line(s3, "0")
time.sleep(0.5)
resp = recv_all(s3, timeout=3)
print(f"Option 2 (key=0) response: {repr(resp[:200])}")

send_line(s3, "3")
time.sleep(0.5)
resp3_3 = recv_all(s3, timeout=3)
print(f"Option 3 (key=0): {repr(resp3_3[:200])}")

s3.close()
