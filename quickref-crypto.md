# Crypto Quick Reference

```bash
# RSA basics
python3 -c "from Crypto.Util.number import *; p=getPrime(1024); print(p)"

# Factor DB lookup
curl -s "http://factordb.com/api?query=<n>"

# Wiener attack (low d)
python3 wiener.py n e c

# Common modulus
python3 -c "from sympy import gcdex"

# Hash identification
hash-identifier <hash>
hashid <hash>

# XOR brute force
python3 -c "from pwn import xor; xor(data, key)"
```
