#!/usr/bin/env python3
import socket, time
from math import gcd, isqrt

HOST = '154.57.164.64'
PORT = 30994

def connect():
    s = socket.socket()
    s.settimeout(30)
    s.connect((HOST, PORT))
    return s

def recv_all(s, timeout=3):
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
    time.sleep(0.3)

def convergents(num, den):
    a, b = num, den
    while b:
        q = a // b
        a, b = b, a % b
        yield q

def find_r(primes):
    for i in range(len(primes)):
        for j in range(i + 1, len(primes)):
            p0, p1 = primes[i], primes[j]
            gen = convergents(p0, p1)
            h0, h1, k0, k1 = 0, 1, 1, 0
            for q in gen:
                h2 = q * h1 + h0
                k2 = q * k1 + k0
                if h2 >= 2**384 or k2 >= 2**384:
                    break
                if h2 > 0 and k2 > 0:
                    r_candidate = max(p0 // h2, p1 // k2)
                    if 600 <= r_candidate.bit_length() <= 650:
                        if p0 % r_candidate < 2**256 and p1 % r_candidate < 2**256:
                            if all(p % r_candidate < 2**256 for p in primes):
                                return r_candidate
                h0, h1, k0, k1 = h1, h2, k1, k2
    return None

def solve():
    s = connect()
    data = recv_all(s)

    primes = []
    for _ in range(20):
        send_line(s, 1)
        resp = recv_all(s)
        for line in resp.split('\n'):
            line = line.strip()
            if line and line[0].isdigit() and len(line) > 200:
                primes.append(int(line))
                break

    r = find_r(primes)
    if not r:
        print("Could not find r")
        return

    send_line(s, "2")
    time.sleep(0.5)
    _ = recv_all(s, timeout=2)
    send_line(s, repr([2 * r] * 256))
    time.sleep(0.5)
    _ = recv_all(s, timeout=3)

    send_line(s, "3")
    time.sleep(0.5)
    resp3 = recv_all(s, timeout=3)

    n, e, c = None, None, None
    for line in resp3.split('\n'):
        line = line.strip()
        if '(' in line and ')' in line:
            start = line.find('(')
            end = line.rfind(')') + 1
            n, e, c = eval(line[start:end])
            break

    s.close()

    n_r = n % r
    n_q2 = n // (r * r)
    n_qr = (n // r) % r

    D = n_qr * n_qr - 4 * n_r * n_q2
    sd = isqrt(D)

    R = (n_qr + sd) // 2
    b1 = gcd(R, n_r)
    b2 = n_r // b1
    a2 = R // b1

    for M in [n_q2, n_q2 - 1, n_q2 + 1]:
        if M <= 0 or M % a2 != 0:
            continue
        a1 = M // a2
        if a1.bit_length() > 385:
            continue
        p_test = a1 * r + b1
        q_test = a2 * r + b2
        if n == p_test * q_test:
            break
        p_test = a1 * r + b2
        q_test = a2 * r + b1
        if n == p_test * q_test:
            b1, b2 = b2, b1
            break
    else:
        print("Could not factor n")
        return

    d = pow(e, -1, (a1 * r + b1 - 1) * (a2 * r + b2 - 1))
    m = pow(c, d, n)

    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad

    key = b'\x00' * 32
    cipher = AES.new(key, AES.MODE_ECB)
    m_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
    flag = unpad(cipher.decrypt(m_bytes), AES.block_size)
    print(f"FLAG: {flag.decode()}")

if __name__ == '__main__':
    solve()
