#!/usr/bin/env python3
"""Quick test of Surprise-Factor server."""
import socket, json, sys

HOST = '154.57.164.80'
PORT = 30118

def get_sig(track):
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

r = get_sig(["half", "sub", "add"])
t = ''.join(r.get("trace", []))
print(f"Trace ({len(t)}): {t[:2000]}")
print(f"\nhash: {r['hash']}")
print(f"r: {r['r']}")
print(f"s: {r['s']}")

# count h-runs
runs = []
i = 0
while i < len(t):
    if t[i] == 'h':
        j = i
        while j < len(t) and t[j] == 'h':
            j += 1
        runs.append(j - i)
        i = j
    else:
        i += 1
print(f"h-runs (first 30): {runs[:30]}")
print(f"h-runs count: {len(runs)}, total h: {sum(runs)}")

# Count ss pairs (subtractions)
sub_count = trace.count('s')
print(f"sub count: {sub_count}")

# count ah pairs (add + half)
add_count = trace.count('a')
print(f"add count: {add_count}")
