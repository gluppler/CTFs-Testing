#!/usr/bin/env python3
"""
Surprise-Factor analysis.
We can separate inv and div binary GCDs using 'v' as delimiter.
Each binary GCD call produces 'h' ops (2 per trailing zero removal).
Key question: can we extract denominator = nonce_mask * k from the div trace,
and use the relationship s = numerator/denominator = (hash + r*d)/k to find d?
"""
import json, socket, struct
from collections import Counter

HOST = '154.57.164.80'
PORT = 30118

N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF

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

def get_samples(n=5):
    """Get n signature samples with half+div tracking."""
    samples = []
    for _ in range(n):
        r = get_sig(["half", "div"])
        t = ''.join(r.get("trace", []))
        div_pos = t.find('v')
        if div_pos < 0:
            continue
        inv_h = t[:div_pos].count('h')
        div_h = t[div_pos:].count('h')
        samples.append({
            "hash": int(r["hash"], 16),
            "r": int(r["r"], 16),
            "s": int(r["s"], 16),
            "inv_h": inv_h,
            "div_h": div_h,
            "total_h": inv_h + div_h,
            "public_key": r["public_key"]
        })
    return samples

samples = get_samples(5)
print("=== 5 Samples with half+div ===")
for i, s in enumerate(samples):
    print(f"Sample {i}: inv_h={s['inv_h']}, div_h={s['div_h']}, "
          f"hash={hex(s['hash'])[:20]}..., r={hex(s['r'])[:20]}...")

# Now track half+add+div to see the parity info
print("\n=== half+add+div sample ===")
r = get_sig(["half", "add", "div"])
t = ''.join(r.get("trace", []))
div_pos = t.find('v')
inv_seg = t[:div_pos]
div_seg = t[div_pos:]
print(f"Inv segment: {len(inv_seg)} ops, h={inv_seg.count('h')}, a={inv_seg.count('a')}")
print(f"Div segment: {len(div_seg)} ops, h={div_seg.count('h')}, a={div_seg.count('a')}")

# In the binary GCD, 'a' operations in the x1/x2 update indicate x1/x2 was ODD
# Let's analyze this: each trailing zero removal has 2 halves:
# half(value) + (half(x) or half(add(x, modulus)))
# a = add(x, modulus) appears when x is odd
# So a-count is the number of times x1 or x2 was ODD during TZ removal
print(f"\n% of TZ removals where x1/x2 was odd:")
print(f"  Inv: {inv_seg.count('a')}/{inv_seg.count('h')//2} = {inv_seg.count('a')*100/(inv_seg.count('h')//2+1):.1f}%")
print(f"  Div: {div_seg.count('a')}/{div_seg.count('h')//2} = {div_seg.count('a')*100/(div_seg.count('h')//2+1):.1f}%")

# Let's also try to see the h-run pattern for div's binary GCD
# Each pair of h's = one TZ removal. Runs of h's = consecutive TZ removals.
# Parse the runs
def parse_h_runs(segment):
    """Extract lengths of consecutive h runs."""
    runs = []
    i = 0
    while i < len(segment):
        if segment[i] == 'h':
            j = i
            while j < len(segment) and segment[j] == 'h':
                j += 1
            run_len = j - i
            runs.append(run_len)
            i = j
        else:
            i += 1
    return runs

inv_h_runs = parse_h_runs(inv_seg)
div_h_runs = parse_h_runs(div_seg)

print(f"\nDiv h-run lengths (first 30): {div_h_runs[:30]}")
print(f"Div h-run statistics: min={min(div_h_runs)}, max={max(div_h_runs)}, "
      f"avg={sum(div_h_runs)/len(div_h_runs):.2f}, "
      f"count={len(div_h_runs)}")

# Since each TZ removal produces 2 h's, the run length is always even
# div_h_runs should be all even numbers
print(f"Are all div h-runs even? {all(r % 2 == 0 for r in div_h_runs)}")

# Each pair of h's = one TZ removal
# The number of pairs = total h / 2
# A run of 2*h means 1 TZ removal
# A run of 4*h means 2 TZ removals
# etc.

tz_counts = [r // 2 for r in div_h_runs]
print(f"TZ removals per step (first 30): {tz_counts[:30]}")
print(f"Total TZ removals: {sum(tz_counts)}")
print(f"Steps (outer iterations): {len(tz_counts)}")
print(f"Avg TZ per step: {sum(tz_counts)/len(tz_counts):.2f}")
