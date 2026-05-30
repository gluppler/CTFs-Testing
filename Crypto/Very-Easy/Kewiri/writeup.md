---
title: "Kewiri"
ctf: "HackTheBox CTF - CA 2k25"
date: 2026-05-22
category: crypto
difficulty: very easy
points: ~500
flag_format: "HTB{...}"
author: "opencode"
---

# Kewiri

## Summary

A six-question crypto challenge covering prime bit length, p-1 factorization of GF(p) order, generator testing, anomalous elliptic curve recognition, curve order over F_{p^3}, and recovery of a discrete log via Smart's attack on an anomalous curve.

## Solution

### Step 1: Q1–Q5 (Preliminary questions)

- **Q1** — Compute `p.bit_length()` → `384`.
- **Q2** — Factor `p - 1` using sympy, send `p1,e1_p2,e2_...` format. p-1 = 2²·5·635599·2533393·4122411947·175521834973·206740999513·1994957217983·215264178543783483824207·10254137552818335844980930258636403.
- **Q3** — For each of 17 candidates, test if it's a generator mod p by checking `g^((p-1)/pi) != 1 mod p` for every prime factor pi.
- **Q4** — Server sends curve params `a, b` for E(F_p). The order equals p (anomalous curve, trace 1).
- **Q5** — Over F_{p³}, order = p·(p² + p + 1 - ...) = p·(p²+3). Factor: 2²·7²·p·(large composite). Send the factorization.

### Step 2: Q6 — Smart's attack (discrete log on anomalous curve)

An anomalous curve has `#E(F_p) = p`, making the ECDLP trivial via Smart's attack. The attack lifts points to Z/p²Z, multiplies by p (landing in the kernel of reduction), and extracts the discrete log via the formal logarithm.

Key implementation details:
- Use **Jacobian coordinates** throughout the lift to avoid modular inverses during `p * P` (dangerous when Z ≡ 0 mod p).
- After `p * G'` and `p * A'`, extract the formal log directly from projective coordinates: `φ = X · (Z/p) · Y⁻¹ mod p`.
- Randomize the lift curve parameters `ap = a + ka·p`, `bp = b + kb·p` until both `p·G'` and `p·A'` land in the kernel.

```python
import socket, re, sys, time, random

HOST = "154.57.164.75"
PORT = 30733
p = 21214334341047589034959795830530169972304000967355896041112297190770972306665257150126981587914335537556050020788061

ANS1 = b"384"
ANS2 = b"2,2_5,1_635599,1_2533393,1_4122411947,1_175521834973,1_206740999513,1_1994957217983,1_215264178543783483824207,1_10254137552818335844980930258636403,1"
ANS4 = str(p).encode()
ANS5 = b"2,2_7,2_21214334341047589034959795830530169972304000967355896041112297190770972306665257150126981587914335537556050020788061,1_2296163171090566549378609985715193912396821929882292947886890025295122370435191839352044293887595879123562797851002485690372901374381417938210071827839043175382685244226599901222328480132064138736290361668527861560801378793266019,1"
p1_factors = [2, 5, 635599, 2533393, 4122411947, 175521834973, 206740999513, 1994957217983, 215264178543783483824207, 10254137552818335844980930258636403]

def ts(n, p):
    if n == 0: return 0
    if pow(n, (p-1)//2, p) != 1: return None
    if p % 4 == 3: return pow(n, (p+1)//4, p)
    q, s = p - 1, 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (p-1)//2, p) != p - 1: z += 1
    m, c = s, pow(z, q, p)
    t, r = pow(n, q, p), pow(n, (q+1)//2, p)
    while t not in (0, 1):
        i, temp = 1, t
        while pow(temp, 2, p) != 1: temp = pow(temp, 2, p); i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c = i, (b * b) % p
        t, r = (t * c) % p, (r * b) % p
    return r

class JacPoint:
    def __init__(self, X, Y, Z, na, nb, n):
        self.X, self.Y, self.Z = X % n, Y % n, Z % n
        self.na, self.nb, self.n = na, nb, n
    def is_inf(self): return self.Z == 0
    def neg(self): return JacPoint(self.X, (-self.Y) % self.n, self.Z, self.na, self.nb, self.n)
    def add(self, o):
        n = self.n
        if self.is_inf(): return o
        if o.is_inf(): return self
        X1, Y1, Z1 = self.X, self.Y, self.Z
        X2, Y2, Z2 = o.X, o.Y, o.Z
        U1, U2 = (X1 * Z2 * Z2) % n, (X2 * Z1 * Z1) % n
        S1, S2 = (Y1 * Z2 * Z2 * Z2) % n, (Y2 * Z1 * Z1 * Z1) % n
        H, R = (U2 - U1) % n, (S2 - S1) % n
        if H == 0:
            if R == 0: return self.dbl()
            else: return JacPoint(0, 0, 0, self.na, self.nb, n)
        X3 = (R*R - H*H*H - 2*U1*H*H) % n
        Y3 = (R*(U1*H*H - X3) - S1*H*H*H) % n
        Z3 = (H * Z1 * Z2) % n
        return JacPoint(X3, Y3, Z3, self.na, self.nb, n)
    def dbl(self):
        n = self.n
        X1, Y1, Z1 = self.X, self.Y, self.Z
        if Y1 == 0: return JacPoint(0, 0, 0, self.na, self.nb, n)
        S = (4 * X1 * Y1 * Y1) % n
        M = (3 * X1 * X1) % n if self.na == 0 else (3 * X1 * X1 + self.na * pow(Z1, 4, n)) % n
        X3 = (M*M - 2*S) % n
        Y3 = (M*(S - X3) - 8 * pow(Y1, 4, n)) % n
        Z3 = (2 * Y1 * Z1) % n
        return JacPoint(X3, Y3, Z3, self.na, self.nb, n)
    def mul(self, k):
        r = JacPoint(0, 0, 0, self.na, self.nb, self.n)
        a = self
        while k:
            if k & 1: r = r.add(a)
            a = a.dbl()
            k >>= 1
        return r

def smart(p, a, b, Gx, Gy, Ax, Ay):
    for _ in range(30):
        try:
            ka, kb = random.randint(1, p-1), random.randint(1, p-1)
            ap, bp = a + ka * p, b + kb * p
            n = p * p
            def lift_J(x, y):
                rhs = (pow(x, 3, n) + ap*x + bp) % n
                lhs = (y*y) % n
                diff = (rhs - lhs) % n
                if diff == 0:
                    yl = y
                else:
                    k = (diff // p) * pow(2*y, -1, p) % p
                    yl = (y + p*k) % n
                return JacPoint(x, yl, 1, ap, bp, n)
            Gp, Ap = lift_J(Gx, Gy), lift_J(Ax, Ay)
            pG, pA = Gp.mul(p), Ap.mul(p)
            def formal_log(pt):
                if pt.is_inf() or pt.Z % p != 0: return 0
                return (pt.X * (pt.Z // p) * pow(pt.Y, -1, p)) % p
            lg, la = formal_log(pG), formal_log(pA)
            if lg != 0:
                d = (la * pow(lg, -1, p)) % p
                return d
        except Exception:
            continue
    raise RuntimeError("Smart's attack failed")

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30); s.connect((HOST, PORT))
    return s

def rd(s, marker=b"> "):
    d = b""
    while marker not in d:
        c = s.recv(4096)
        if not c: break
        d += c
    return d

def sd(s, d):
    s.sendall((d if isinstance(d, bytes) else d.encode()) + b"\n")

s = connect()
rd(s, b"> "); sd(s, ANS1)
rd(s, b"> "); sd(s, ANS2)

for qi in range(1, 18):
    data = rd(s, b"? >")
    g = int(re.search(rb'(\d+)\s*\?', data).group(1))
    isg = 1
    for pf in p1_factors:
        if pow(g, (p-1)//pf, p) == 1: isg = 0; break
    sd(s, str(isg))

q4data = rd(s, b"> ")
curve_a = int(re.search(r'a\s*=\s*(\d+)', q4data.decode()).group(1))
curve_b = int(re.search(r'b\s*=\s*(\d+)', q4data.decode()).group(1))
sd(s, ANS4)

rd(s, b"> "); sd(s, ANS5)

q6data = rd(s, b"? >")
q6txt = q6data.decode()
coords = re.findall(r'x-coordinate:\s*(\d+)', q6txt)
Gx, Ax = int(coords[0]), int(coords[1])

rG = (pow(Gx, 3, p) + curve_a*Gx + curve_b) % p
Gy = ts(rG, p)
rA = (pow(Ax, 3, p) + curve_a*Ax + curve_b) % p
Ay = ts(rA, p)

d = smart(p, curve_a, curve_b, Gx, Gy, Ax, Ay)
sd(s, str(d))

import time; time.sleep(2)
s.settimeout(3)
try:
    while True:
        c = s.recv(4096)
        if not c: break
        print(c.decode(errors="replace"), end="")
except: pass
s.close()
```

## Flag

```
HTB{Welcome_to_CA_2k25!Here_is_your_anomalous_flag_for_this_challenge_and_good_luck_with_the_rest:)}
```
