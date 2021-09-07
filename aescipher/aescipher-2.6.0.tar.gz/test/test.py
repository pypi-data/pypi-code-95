from aescipher import *


key = "ab一" or "ab一".encode()
plaintext = "ab一" or "ab一".encode()
ciphertext = AESCipher(key).encrypt(plaintext)
print(plaintext, ciphertext)
print(plaintext == AESCipher(key).decrypt(ciphertext))
