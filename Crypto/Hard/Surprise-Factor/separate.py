#!/usr/bin/env python3
"""Separate inv and div binary GCDs using targeted tracking."""
import json, socket

HOST = '154.57.164.80'
PORT = 30118
N_val = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
P_val = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF

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

# Track half + inv to separate inv's binary GCD from div's
# 'i' = inv entry, 'h' = half calls
r = get_sig(["half", "inv"])
t = ''.join(r.get("trace", []))
print(f"half+inv: {len(t)} ops")
print(f"h count: {t.count('h')}, i count: {t.count('i')}")

# Find inv entries - there should be 1 (the one in to_affine)
inv_positions = [i for i, c in enumerate(t) if c == 'i']
print(f"'i' positions: {inv_positions}")
if len(inv_positions) == 1:
    inv_pos = inv_positions[0]
    # Everything before the 'i' is from scalar multiplication etc (no 'h')
    # Its binary GCD is AFTER the 'i'
    h_after_i = t[inv_pos:].count('h')
    print(f"h after inv entry: {h_after_i}")
    print(f"h before inv entry: {t[:inv_pos].count('h')}")
    print(f"Total h in inv segment: {t[inv_pos:].count('h')}")
    # Show the first 100 chars after the 'i'
    post_i = t[inv_pos:inv_pos+100]
    print(f"After 'i': {post_i}")

# Track half + div to separate div's binary GCD
r2 = get_sig(["half", "div"])
t2 = ''.join(r2.get("trace", []))
print(f"\nhalf+div: {len(t2)} ops")
print(f"h count: {t2.count('h')}, v count: {t2.count('v')}")
# Find div entries
div_positions = [i for i, c in enumerate(t2) if c == 'v']
print(f"'v' positions: {div_positions}")
if len(div_positions) == 1:
    div_pos = div_positions[0]
    h_after_div = t2[div_pos:].count('h')
    print(f"h after div entry: {h_after_div}")
    print(f"h before div entry: {t2[:div_pos].count('h')}")
    print(f"Total h: {t2.count('h')}")

# Now try to extract just inv's binary GCD by tracking half, inv, mod, mul
# The inv binary GCD is surrounded by: mod calls, mul calls
r3 = get_sig(["half", "inv", "mod"])
t3 = ''.join(r3.get("trace", []))
print(f"\nhalf+inv+mod: {len(t3)} ops")
idx_i = t3.find('i')
if idx_i >= 0:
    # Find first non-half/mod after inv's GCD ends (look for 'i' then more ops)
    after_i = t3[idx_i+1:]
    # The inv binary GCD produces only 'h' and 'r' ops (half and mod inside the GCD)
    # It ends when we see other operations
    h_count_in_gcd = 0
    r_count_in_gcd = 0
    for c in after_i:
        if c in 'hr':
            if c == 'h': h_count_in_gcd += 1
            if c == 'r': r_count_in_gcd += 1
        else:
            break
    print(f"Inv binary GCD: {h_count_in_gcd} half ops, {r_count_in_gcd} mod ops")
    
    # Now find the div binary GCD: look for 'v' after the above operations
    # Actually let's also track 'div' to find it

# Let me try tracking half, inv, div together to see both GCDs
r4 = get_sig(["half", "inv", "div"])
t4 = ''.join(r4.get("trace", []))
print(f"\nhalf+inv+div: {len(t4)} ops")
idx_i4 = t4.find('i')
idx_v4 = t4.find('v')
print(f"inv at {idx_i4}, div at {idx_v4}")

# h-runs between inv and div
if idx_i4 >= 0 and idx_v4 >= 0 and idx_i4 < idx_v4:
    # Everything between inv entry and div entry is inv's binary GCD + intermediate ops
    # Everything after div entry is div's binary GCD
    inv_segment = t4[idx_i4:idx_v4]
    div_segment = t4[idx_v4:]
    
    h_in_inv_seg = inv_segment.count('h')
    h_in_div_seg = div_segment.count('h')
    print(f"h in inv segment: {h_in_inv_seg}")
    print(f"h in div segment: {h_in_div_seg}")
    print(f"Total h: {h_in_inv_seg + h_in_div_seg}")

# Now let's try to extract the binary GCD half patterns for inv only
# by using the position of 'i' in the trace
r5 = get_sig(["half", "inv", "to_affine"])
t5 = ''.join(r5.get("trace", []))
print(f"\nhalf+inv+to_affine: {len(t5)} ops")
idx_f = t5.find('F')  # to_affine entry
idx_i5 = t5.find('i')
print(f"to_affine at {idx_f}, inv at {idx_i5}")
