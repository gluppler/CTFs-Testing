#!/usr/bin/env python3

import json

# Load the output data
with open('output.txt', 'r') as f:
    data = json.load(f)

# Convert hex strings to bit arrays
def hex_to_bits(hex_str):
    bytes_data = bytes.fromhex(hex_str)
    bits = []
    for byte in bytes_data:
        for i in range(8):
            bits.append((byte >> (7-i)) & 1)
    return bits

def bits_to_hex(bits):
    byte_array = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i+j]
        byte_array.append(byte)
    return bytes(byte_array).hex()

# Extract zero encryption (this is our constant term c = E(0))
zero_pt = data['zero']['pt']
zero_ct = data['zero']['ct']
c = hex_to_bits(zero_ct)

# Build the linear transformation matrix M
M = [[0 for _ in range(128)] for _ in range(128)]

# Process basis pairs
for i, pair in enumerate(data['basis_pairs']):
    pt = pair['pt']
    ct = pair['ct']
    pt_bits = hex_to_bits(pt)
    ct_bits = hex_to_bits(ct)
    # L(basis_i) = E(basis_i) + E(0)
    L_basis_i = [ct_bits[j] ^ c[j] for j in range(128)]
    # This gives us column i of M
    for j in range(128):
        M[j][i] = L_basis_i[j]

# Function to multiply matrix by vector over GF(2)
def mat_vec_mul(M, v):
    result = [0] * 128
    for i in range(128):
        for j in range(128):
            result[i] ^= (M[i][j] & v[j])
    return result

# Function to compute matrix inverse over GF(2) using Gaussian elimination
def mat_inv_gf2(M):
    n = len(M)
    aug = [[M[i][j] for j in range(n)] + [1 if i == j else 0 for j in range(n)] 
           for i in range(n)]
    for col in range(n):
        pivot_row = -1
        for row in range(col, n):
            if aug[row][col] == 1:
                pivot_row = row
                break
        if pivot_row == -1:
            raise ValueError("Matrix is singular")
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        for row in range(n):
            if row != col and aug[row][col] == 1:
                for j in range(2*n):
                    aug[row][j] ^= aug[col][j]
    inv = [[aug[i][j+n] for j in range(n)] for i in range(n)]
    return inv

# Compute inverse of M
Minv = mat_inv_gf2(M)

# Verify with a few basis pairs
print("Verifying basis pairs:")
for i in range(min(8, len(data['basis_pairs']))):
    pair = data['basis_pairs'][i]
    pt = pair['pt']
    expected_ct = pair['ct']
    pt_bits = hex_to_bits(pt)
    # Compute M * pt + c
    M_pt = mat_vec_mul(M, pt_bits)
    computed_ct_bits = [M_pt[j] ^ c[j] for j in range(128)]
    computed_ct = bits_to_hex(computed_ct_bits)
    if computed_ct == expected_ct:
        print(f"  Basis pair {i}: OK")
    else:
        print(f"  Basis pair {i}: FAILED")
        print(f"    Expected: {expected_ct}")
        print(f"    Computed: {computed_ct}")

# Verify zero encryption
pt_bits = hex_to_bits(zero_pt)
M_pt = mat_vec_mul(M, pt_bits)
computed_ct_bits = [M_pt[j] ^ c[j] for j in range(128)]
computed_ct = bits_to_hex(computed_ct_bits)
if computed_ct == zero_ct:
    print("  Zero encryption: OK")
else:
    print("  Zero encryption: FAILED")

# Now decrypt the flag
flag_ct_hex = data['flag_ct']
flag_ct_bits = hex_to_bits(flag_ct_hex)
flag_pt_bits = mat_vec_mul(Minv, [flag_ct_bits[i] ^ c[i] for i in range(128)])
flag_pt_hex = bits_to_hex(flag_pt_bits)
print(f"\nFlag plaintext (hex): {flag_pt_hex}")

try:
    flag_bytes = bytes.fromhex(flag_pt_hex)
    flag_ascii = flag_bytes.decode('utf-8')
    print(f"Flag (ASCII): {flag_ascii}")
except Exception as e:
    print(f"Could not decode as UTF-8: {e}")
    print(f"Raw bytes: {flag_bytes}")
