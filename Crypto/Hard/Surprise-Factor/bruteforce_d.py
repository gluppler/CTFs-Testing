#!/usr/bin/env python3
"""Try to brute-force the private key with common CTF patterns."""
import sys, os, socket, json, hashlib

sys.path.insert(0, os.path.expanduser('~/Downloads/CTFs-Testing/Crypto/Hard/Surprise-Factor/crypto_surprise_factor'))
from ec import N as CURVE_N, G, GX, GY, P

def modmul(a, b, m):
    return (a * b) % m

def modinv(a, m):
    return pow(a, -1, m)

def ec_add(p1, p2):
    """Add two points on secp256r1 (Jacobian or affine)."""
    if p1 is None: return p2
    if p2 is None: return p1
    
    x1, y1 = p1
    x2, y2 = p2
    
    if x1 == x2 and y1 == (-y2) % P:
        return None  # point at infinity
    
    if x1 == x2 and y1 == y2:
        if y1 == 0:
            return None
        lam = (3 * x1 * x1) % P * modinv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * modinv(x2 - x1, P) % P
    
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)

def ec_mul(k, point):
    """Scalar multiplication using double-and-add."""
    if k == 0 or point is None:
        return None
    
    result = None
    addend = point
    
    while k:
        if k & 1:
            result = ec_add(result, addend)
        addend = ec_add(addend, addend)
        k >>= 1
    
    return result

def verify_d(d, hash_int, r, s):
    """Check if d is the correct private key by verifying ECDSA signature."""
    N = CURVE_N
    
    # Compute the nonce: k = (hash + r*d) * s^(-1) mod N
    k = (hash_int + r * d) * modinv(s, N) % N
    
    if k == 0:
        return False
    
    # Compute R = k * G
    R = ec_mul(k, (GX, GY))
    
    if R is None:
        return False
    
    # Check: R.x == r mod N
    return R[0] % N == r

# Generate candidate private keys
def generate_candidates():
    N = CURVE_N
    candidates = set()
    
    # Small values
    for i in range(1, 100):
        candidates.add(i)
    
    # Common hex values
    for v in [0x1337, 0x31337, 0x42, 0xdeadbeef, 0xcafebabe, 0xbeef, 0xdead,
              0xdeadbeefcafebabe, 0xbadc0de, 0xbaadf00d, 0xdecaf, 0xc0ffee,
              0xcafe, 0xbabe, 0xface, 0xfeed, 0xdeaf, 0xbead]:
        if v < N:
            candidates.add(v)
    
    # Powers of 2
    for i in range(0, 256):
        candidates.add(1 << i)
    
    # Hashes of challenge-related strings
    strings = [
        b'surprise', b'Surprise Factor', b'surprise_factor',
        b'military-grade', b'ECDSA', b'broken',
        b'secret', b'flag', b'ctf', b'key',
        b'private_key', b'private', b'd',
    ]
    for s in strings:
        d = int(hashlib.sha256(s).hexdigest(), 16) % N
        candidates.add(d)
    
    # Public key derived
    # Try d = x-coordinate of public key
    pub_x = 0xf85c6c901010ec340330ed7bbce9db3a0ef34bcec49315639cdca27dcad3880e
    pub_y = 0xf8faa51c421cb7052cb6238c18d2d7cc9e25657d80e8f45a4e72e7d06aeeb790
    candidates.add(pub_x)
    candidates.add(pub_y)
    candidates.add(pub_x % N)
    candidates.add(pub_y % N if pub_y < N else pub_y % N)
    
    # Hash of public key coordinates
    for coord in [str(pub_x).encode(), str(pub_y).encode()]:
        d = int(hashlib.sha256(coord).hexdigest(), 16) % N
        candidates.add(d)
    
    # N - small values
    for i in range(1, 100):
        candidates.add(N - i)
    
    # N/2, N/3, etc
    for div in [2, 3, 5, 7, 11, 13]:
        candidates.add(N // div)
    
    print(f"Generated {len(candidates)} candidates")
    return candidates

# Get signature from server
def get_sig():
    s = socket.socket()
    s.settimeout(30)
    s.connect(('154.57.164.80', 30118))
    req = {'action': 'sign', 'track': []}
    s.sendall((json.dumps(req) + '\n').encode())
    data = b''
    while True:
        try:
            chunk = s.recv(100000)
            if not chunk: break
            data += chunk
        except: break
    s.close()
    return json.loads(data.decode())

# Get a fresh signature
print("Getting fresh signature...")
resp = get_sig()
hash_int = int(resp['hash'], 16)
r = int(resp['r'], 16)
s_val = int(resp['s'], 16)
print(f"hash: {hex(hash_int)[:30]}...")
print(f"r: {hex(r)[:30]}...")
print(f"s: {hex(s_val)[:30]}...")

# Try candidates
print("\nTrying candidate private keys...")
candidates = generate_candidates()
found = False
for d in sorted(candidates):
    if d == 0: continue
    if verify_d(d, hash_int, r, s_val):
        print(f"FOUND private key: {hex(d)}")
        # Submit to server
        result_s = socket.socket()
        result_s.settimeout(10)
        result_s.connect(('154.57.164.80', 30118))
        req = {'action': 'submit', 'd': hex(d)}
        result_s.sendall((json.dumps(req) + '\n').encode())
        data = b''
        while True:
            try:
                chunk = result_s.recv(10000)
                if not chunk: break
                data += chunk
            except: break
        result_s.close()
        result = json.loads(data.decode())
        print(f"Submit result: {result}")
        if result.get('flag'):
            print(f"FLAG: {result['flag']}")
        found = True
        break

if not found:
    print("No match found among candidates.")
