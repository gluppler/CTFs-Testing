#!/usr/bin/env python3
"""
Reconstruct binary GCD inputs from trace.
Key insight: each 'h' is half(), 'a' is add(), 's' is sub().
Inside _binary_division_odd_modulus, the trace with h+a+s reveals:
- Consecutive h's with interleaved a's indicate TZ removal from u or v
- The s,s pairs indicate subtraction (u,v + x1,x2)
- a before a half means x was odd (needed add N before halving)

We can reverse the algorithm from the result (s) back to the initial values
if we can determine the operation sequence direction (u>=v or v>u).
"""
import json, socket

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

def analyze_div_gcd(trace, div_pos):
    """Analyze the div binary GCD trace (after 'v') in detail."""
    seg = trace[div_pos:]
    # Parse into operations: each step is:
    # - tz_u: [h, (a?)], h, [h, (a?)], h, ... (for u trailing zeros)
    # - tz_v: [h, (a?)], h, [h, (a?)], h, ... (for v trailing zeros)
    # - sub: s, s
    
    # Simplified: group consecutive same characters
    i = 0
    steps = []
    while i < len(seg):
        if seg[i] == 'v':
            i += 1
            continue
        if seg[i] == 's':
            # subtraction
            steps.append(('sub', seg[i:i+2]))
            i += 2
        elif seg[i] == 'h':
            # half operations (never alone - always pairs in GCD)
            # Look for (h,h) or (h,a,h) patterns
            # Each TZ removal = 2 halves or 1half+1add+1half
            tz_units = []
            j = i
            while j < len(seg) and seg[j] in 'ha':
                if j + 1 < len(seg) and seg[j] == 'h':
                    if j + 2 < len(seg) and seg[j+1] == 'a' and seg[j+2] == 'h':
                        # pattern: h,a,h = TZ with odd x
                        tz_units.append('odd_tz')
                        j += 3
                    elif j + 1 < len(seg) and seg[j+1] == 'h':
                        # pattern: h,h = TZ with even x
                        tz_units.append('even_tz')
                        j += 2
                    else:
                        j += 1
                else:
                    j += 1
            if tz_units:
                steps.append(('tz', tz_units))
            i = j
        else:
            i += 1
    return steps

# Get a trace and analyze
r = get_sig(["half", "add", "sub", "div"])
t = ''.join(r.get("trace", []))
div_pos = t.find('v')

print(f"Total trace: {len(t)} chars")
print(f"Div position: {div_pos}")
hash_int = int(r['hash'], 16)
r_val = int(r['r'], 16)
s_val = int(r['s'], 16)
print(f"hash: {hex(hash_int)}")
print(f"r: {hex(r_val)}")
print(f"s: {hex(s_val)}")

seg = t[div_pos:]
print(f"\nDiv segment length: {len(seg)}")

# Count TZ operations by looking for h,a,h or h,h patterns
h_count = seg.count('h')
a_count = seg.count('a')
sub_count = seg.count('s')

print(f"Div seg: h={h_count}, a={a_count}, s={sub_count}")
# Each TZ step has exactly 2 halves, sometimes with an 'a' between
# Total TZ removals = h_count / 2 (since each TZ=2 halves)
tz_total = h_count // 2
print(f"Total TZ removals: {tz_total}")
print(f"Total 'a' (odd x moments): {a_count}")
print(f"Odd ratio: {a_count/tz_total*100:.1f}%")

# Now let's look at the raw h+a pattern for the div seg
# Find runs
runs = []
i = 0
while i < len(seg):
    if seg[i] in 'ha':
        j = i
        while j < len(seg) and seg[j] in 'ha':
            j += 1
        runs.append(seg[i:j])
        i = j
    else:
        i += 1

print(f"\nNumber of TZ runs: {len(runs)}")
print(f"First 10 TZ runs: {runs[:10]}")
print(f"Last 5 TZ runs: {runs[-5:]}")
sample = runs[40:50]
print(f"Runs 40-50: {sample}")

# Check if all runs have even length (in terms of halves)
# A run should be: hh, hah, hhhh, hhah, etc.
# Each TZ unit is either 'hh' or 'hah'
# So total h-count in each run = sum of halves

# Let's verify: each run is made of 'hh' or 'hah' patterns
all_valid = True
for run in runs:
    j = 0
    while j < len(run):
        if j+1 < len(run) and run[j:j+2] == 'hh':
            j += 2
        elif j+2 < len(run) and run[j:j+3] == 'hah':
            j += 3
        else:
            print(f"Invalid pattern in run: {run} at position {j}")
            all_valid = False
            break
print(f"\nAll TZ runs valid (hh/hah patterns): {all_valid}")
