# Crypto

Content catalog for cryptography challenges.

## Very Easy

- [Hidden-Handshake](Very-Easy/Hidden-Handshake/writeup.md) — AES-CTR nonce reuse within the same TCP session allows recovering the flag via keystream alignment.
- [Kewiri](Very-Easy/Kewiri/writeup.md) — Six-question crypto challenge covering prime bit length, p-1 factorization, generator testing, anomalous EC recognition, curve order over F_{p^3}, and Smart's attack on an anomalous curve.

## Hard

- [MadMath](Hard/MadMath/exploit.py) — RSA challenge with known private exponent `d` and unknown modulus `n`; recovers `n` via factorization of `ed-1`, then decrypts AES-ECB ciphertext.
