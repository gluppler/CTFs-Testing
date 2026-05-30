from secret import PASSPHRASE, curve_a, curve_p, g_order
from Crypto.Util.number import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import random, time, hashlib

Gx, Gy = (40733212845287381659537354559134076551920727536123123802035255333770142251507, 5939195932044123182011708420242714254691399994280021264443261849355562421816)

class FactorWalker:
    def __init__(self, bits, ff_b=70):
        self.target_bits = bits
        self.ff_b = ff_b
        self.factors = []
        self.current = 1
        
        while self.current.bit_length() < self.target_bits:
            remaining = self.target_bits - self.current.bit_length()
            limit = min(remaining, self.ff_b)
            if limit < 2: limit = 2
            p = getPrime(limit)
            self.factors.append(p)
            self.current *= p
            
    def next(self):
        idx = random.randrange(len(self.factors))
        old_p = self.factors[idx]
        
        lower = int(old_p * 0.9)
        upper = int(old_p * 1.1)
        
        while True:
            new_p = random.randint(lower, upper) | 1
            if isPrime(new_p):
                break
        
        self.current //= old_p
        self.current *= new_p
        self.factors[idx] = new_p
        
        return self.current
        
    
def gen(bits, timeout=0.4):
    gbits = bits // 4
    abits = bits // 8
    
    while True:
        start_time = time.time()
        g_walker = FactorWalker(gbits)
        a_walker = FactorWalker(abits)
        b_walker = FactorWalker(abits)

        while True:
            if time.time() - start_time > timeout:
                break

            g = g_walker.next()
            if g % 2 != 0:
                g *= 2 

            a = 0
            p = None

            while True:
                if time.time() - start_time > timeout:
                    break

                a = a_walker.next()
                p = a**2 * g + 1
                
                if isPrime(p):
                    break

            if not p:
                if time.time() - start_time > timeout:
                    break
                continue

            while True:
                if time.time() - start_time > timeout:
                    break

                b = b_walker.next()
                if a == b:
                    continue

                q = b**2 * g + 1
                
                if isPrime(q) and GCD(a, b) == 1:
                    return p, q
            
            if time.time() - start_time > timeout:
                break
            
def point_mul(k, Px=Gx, Py=Gy):
    def inv(n, p):
        return pow(n, p - 2, p)
    def add(P, Q):
        if P is None:
            return Q
        if Q is None:
            return P

        x1, y1 = P
        x2, y2 = Q

        if x1 == x2:
            if (y1 + y2) % curve_p == 0:
                return None
            else:
                l = (3 * x1 * x1 + curve_a) * inv(2 * y1, curve_p) % curve_p
        else:
            l = (y2 - y1) * inv(x2 - x1, curve_p) % curve_p
        x3 = (l * l - x1 - x2) % curve_p
        y3 = (l * (x1 - x3) - y1) % curve_p
        return (x3, y3)

    if k < 0:
        k = -k
        Py = (-Py) % curve_p

    R = None
    Q = (Px, Py)
    while k:
        if k & 1:
            R = add(R, Q)
        Q = add(Q, Q)
        k >>= 1
    return R



p,q = gen(1024)
e = 0x10001
n = p*q
phi = (p-1)*(q-1)
d = pow(e, -1, phi)

print(f"d = {d}")
print(f"c = {pow(bytes_to_long(PASSPHRASE.encode()), e, n)}")

FLAG = bytes_to_long(open("flag.txt", "rb").read())
assert FLAG < g_order <= 1 << 257

KEY = hashlib.sha256(PASSPHRASE.encode()).digest()
cipher = AES.new(KEY, AES.MODE_ECB)
while True:
    exp = int(input("Give me an exponent: "))
    if not (1 < exp < g_order):
        print("nope.")
        continue
    enc_point = point_mul(pow(FLAG, exp, g_order))
    print(cipher.encrypt(pad(str(enc_point).encode(), 16)).hex())