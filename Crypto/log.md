# Crypto Action Log

## 2026-05-22

- **Hidden-Handshake** — Solved AES-CTR nonce reuse challenge. Exploit: send two queries with same pass2 within one connection; XOR aligned ciphertexts to recover flag. Flag: `HTB{v3ry_n1c3!___4_b1t_sp1cy_k3ystr34m_r3us3}`
- **Kewiri** — Solved six-question crypto challenge. Implemented Smart's attack on anomalous curve in Jacobian coordinates. Flag: `HTB{Welcome_to_CA_2k25!...}`
- **MadMath** — Solved RSA challenge. Recovered modulus n by factoring `ed-1` into p,q via enumeration of prime power partitions. AES-ECB decryption yielded the flag.
