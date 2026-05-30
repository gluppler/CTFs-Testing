#!/usr/bin/env python3

from ast import literal_eval
from secrets import randbits

from Crypto.Cipher import AES
from Crypto.Util.number import getPrime, isPrime
from Crypto.Util.Padding import pad


A, B, P, R = 384, 256, 1024, 640

def a() -> int: return randbits(A)
def b() -> int: return randbits(B)

def n2v(n: int, k: int = B) -> list[int]: return list(map(int, f'{n:0{k}b}'))
def v2n(v: list[int]) -> int: return int(''.join(map(str, v)), 2)
def n2b(n: int, k: int = B // 8) -> bytes: return n.to_bytes(k, 'big')
def b2n(b: bytes) -> int: return int.from_bytes(b, 'big')
def v2b(v: list[int]) -> bytes: return n2b(v2n(v))
def b2v(b: bytes) -> list[int]: return n2v(b2n(b))


class Server:
    def __init__(self):
        self.r = getPrime(R)
        p, q = self.gen_prime(), self.gen_prime()
        self.n, self.e = p * q, 65537
        self.key = n2b(b())

    def gen_prime(self) -> int:
        while True:
            if (p := a() * self.r + b()).bit_length() == P and isPrime(p):
                return p

    def _public_key(self, private_key: list[int]) -> list[int]:
        m = [2 * b() + int(b_i) for b_i in private_key]
        return [a() * self.r + m_i for m_i in m]

    def update_key(self, k1: list[int]):
        k0 = self._public_key(b2v(self.key))
        assert isinstance(k1, list) and all(isinstance(k1_i, int) for k1_i in k1)
        assert len(k0) == len(k1)
        assert all(self.r < k1_i <= 2 ** A * self.r for k1_i in k1)
        k = [k0_i * k1_i for k0_i, k1_i in zip(k0, k1)]
        bits = [(k_i % self.r) % 2 for k_i in k]
        self.key = v2b(bits)

    def _aes_encrypt(self, pt: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_ECB)
        return cipher.encrypt(pad(pt, AES.block_size))

    def encrypt_flag(self) -> tuple[int, int, int]:
        try:
            with open('flag.txt', 'rb') as f:
                flag = f.read().strip()
        except FileNotFoundError:
            flag = b'HTB{f4k3_fl4g_f0r_t3st1ng}'

        enc_flag = self._aes_encrypt(flag)
        m = b2n(enc_flag)
        c = pow(m, self.e, self.n)
        return self.n, self.e, c


def menu() -> int:
    print('Choose an option:')
    print('1. Generate prime')
    print('2. Update key')
    print('3. Encrypt flag')
    print('4. Exit')
    try:
        return int(input('> '))
    except ValueError:
        return 4


if __name__ == '__main__':
    server = Server()

    while (option := menu()) != 4:
        if option == 1:
            print("It's raining primes!")
            print(server.gen_prime())
        elif option == 2:
            try:
                c1 = literal_eval(input('Encrypted key:\n'))
                server.update_key(c1)
            except AssertionError:
                break
        elif option == 3:
            print('Encrypted flag:')
            print(server.encrypt_flag())
