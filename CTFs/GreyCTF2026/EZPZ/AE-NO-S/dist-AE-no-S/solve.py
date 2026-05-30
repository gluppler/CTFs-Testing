#!/usr/bin/env python3

import json

# Load the output data
with open('output.txt') as f:
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
            raise ValueError('Matrix is singular')
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        for row in range(n):
            if row != col and aug[row][col] == 1:
                for j in range(2*n):
                    aug[row][j] ^= aug[col][j]
    inv = [[aug[i][j+n] for j in range(n)] for i in range(n)]
    return inv

# Compute inverse of M
Minv = mat_inv_gf2(M)

# Decrypt each block of the flag ciphertext
flag_ct_hex = data['flag_ct']
print(f'Flag ciphertext: {flag_ct_hex}')
print(f'Length: {len(flag_ct_hex)} hex chars = {len(flag_ct_hex)//2} bytes')

# Split into 16-byte (32 hex char) blocks
blocks = []
for i in range(0, len(flag_ct_hex), 32):
    block = flag_ct_hex[i:i+32]
    blocks.append(block)
    print(f'Block {len(blocks)-1}: {block}')

# Decrypt each block
plaintext_blocks = []
for i, block_hex in enumerate(blocks):
    block_bits = hex_to_bits(block_hex)
    # Compute: pt = Minv * (ct + c)
    ct_plus_c = [block_bits[j] ^ c[j] for j in range(128)]
    pt_bits = mat_vec_mul(Minv, ct_plus_c)
    pt_hex = bits_to_hex(pt_bits)
    plaintext_blocks.append(pt_hex)
    print(f'Plaintext block {i}: {pt_hex}')

# Combine plaintext blocks
combined_hex = ''.join(plaintext_blocks)
print(f'Combined plaintext hex: {combined_hex}')

try:
    combined_bytes = bytes.fromhex(combined_hex)
    # Try to decode as UTF-8
    combined_ascii = combined_bytes.decode('utf-8')
    print(f'Combined plaintext (ASCII): {repr(combined_ascii)}')
    print(f'Combined plaintext (ASCII): {combined_ascii}')
except Exception as e:
    print(f'Could not decode as UTF-8: {e}')
    print(f'Raw bytes: {combined_bytes}')
    
    # Try to see if there's padding we need to remove
    # Look for PKCS7 padding
    if len(combined_bytes) > 0:
        last_byte = combined_bytes[-1]
        if 1 <= last_byte <= 16:
            # Check if the last 'last_byte' bytes all have value 'last_byte'
            padding_ok = True
            for i in range(last_byte):
                if combined_bytes[-(i+1)] != last_byte:
                    padding_ok = False
                    break
            if padding_ok:
                unpadded = combined_bytes[:-last_byte]
                try:
                    unpadded_ascii = unpadded.decode('utf-8')
                    print(f'After removing PKCS7 padding: {repr(unpadded_ascii)}')
                    print(f'After removing PKCS7 padding: {unpadded_ascii}')
                except:
                    print(f'Bytes after padding removal: {unpadded}')

