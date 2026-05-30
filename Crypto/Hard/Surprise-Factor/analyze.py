#!/usr/bin/env python3
"""Analyze Surprise-Factor trace patterns."""
import json, subprocess, sys

HOST = '154.57.164.80'
PORT = 30118
N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF

def get_sig(track):
    import socket
    s = socket.socket()
    s.settimeout(15)
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

# 1) Track half ONLY - raw binary GCD half operations
r1 = get_sig(["half"])
t1 = ''.join(r1.get("trace", []))
print(f"half only: {len(t1)} ops")
print(f"Expected 2 * (total trailing zeros from both binary GCDs): {len(t1)}")

# 2) Track half + sub - see the structure (half runs separated by subs)
r2 = get_sig(["half", "sub"])
t2 = ''.join(r2.get("trace", []))
# Parse into runs of same character
runs = []
i = 0
while i < len(t2):
    c = t2[i]
    j = i
    while j < len(t2) and t2[j] == c:
        j += 1
    runs.append((c, j-i))
    i = j
print(f"\nhalf+sub: {len(t2)} ops, {len(runs)} runs")
print(f"First 30 runs: {runs[:30]}")
print(f"Last 10 runs: {runs[-10:]}")

# Count sub runs
sub_runs = [l for c,l in runs if c == 's']
print(f"Number of sub operations: {sum(l for c,l in runs if c == 's')}")
print(f"Number of s-runs (each is 1 sub call): {len(sub_runs)}")
print(f"S-runs: {sub_runs}")

# 3) Track half + sub + add
r3 = get_sig(["half", "sub", "add"])
t3 = ''.join(r3.get("trace", []))
runs3 = []
i = 0
while i < len(t3):
    c = t3[i]
    j = i
    while j < len(t3) and t3[j] == c:
        j += 1
    runs3.append((c, j-i))
    i = j
print(f"\nhalf+sub+add: {len(t3)} ops, {len(runs3)} runs")
print(f"First 30 runs: {runs3[:30]}")
print(f"Counts: h={t3.count('h')}, s={t3.count('s')}, a={t3.count('a')}")

# 4) Track binary_division_odd_modulus explicitly
r4 = get_sig(["binary_division_odd_modulus"])
t4 = ''.join(r4.get("trace", []))
print(f"\nbinary_division_odd_modulus only: {len(t4)} ops - all 'y'")
print(f"Trace: {t4}")
