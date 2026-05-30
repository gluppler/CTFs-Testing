---
title: "Hidden-Handshake"
ctf: "HTB"
date: 2026-05-22
category: crypto
difficulty: very-easy
points: 0
flag_format: "HTB{...}"
---

# Hidden-Handshake

## Summary

AES-CTR nonce reuse within the same TCP session allows recovering the flag via keystream alignment.

## Solution

The server uses `server_secret = generate_password(8)` **once per connection**, then enters a `while True` loop accepting multiple queries. Each query takes a `pass2` (8 chars) and `user`, then encrypts:
```
plaintext = f"Agent {user}, your clearance for Operation Blackout is: {FLAG}. It is mandatory..."
key = sha256(server_secret + pass2)
cipher = AES.new(key, AES.MODE_CTR, nonce=pass2)
```

Since `pass2` is both part of the key derivation and the CTR nonce, using the **same pass2** for two queries within one connection produces an identical keystream. With an empty user in query 1 and a 500-char user in query 2, the flag bytes in query 1 align with known `'A'` bytes in query 2's plaintext. XORing the two ciphertexts at those positions recovers the flag.

```python
import socket

HOST = "154.57.164.72"
PORT = 32039
PASS2 = b"aaaaaaaa"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(8)
s.connect((HOST, PORT))

buf = b""

def send_recv(pass2: bytes, user: bytes) -> bytes:
    global buf
    while b"secure access key:" not in buf:
        buf += s.recv(4096)
    s.sendall(pass2 + b"\n")
    while b"Agent Codename:" not in buf:
        buf += s.recv(4096)
    s.sendall(user + b"\n")
    marker = b"--- End of Transmission ---"
    while marker not in buf:
        buf += s.recv(4096)
    idx_start = buf.find(b"Encrypted transmission:")
    idx_end = buf.find(marker)
    hex_str = buf[idx_start:idx_end].split(b":")[-1].strip().decode()
    buf = buf[idx_end + len(marker):]
    return bytes.fromhex(hex_str)

ct1 = send_recv(PASS2, b"")
ct2 = send_recv(PASS2, b"A" * 500)
s.close()

PREFIX = b"Agent , your clearance for Operation Blackout is: "
flag_start = len(PREFIX)

flag = bytearray()
for i in range(min(len(ct1) - flag_start, len(ct2) - flag_start, 456)):
    flag.append(ct1[flag_start + i] ^ ct2[flag_start + i] ^ ord('A'))

print(flag.decode())
```

## Flag

```
HTB{v3ry_n1c3!___4_b1t_sp1cy_k3ystr34m_r3us3}
```
