import binascii

from Crypto.Cipher import AES
import base64

# 双向对称加密
key = 'haohaoxuexi'


def encrypt_oracle(text):
    # 秘钥
    # 待加密文本
    # 初始化加密器
    text = str(text)
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 先进行aes加密
    encrypt_aes = aes.encrypt(add_to_16(text))
    # 用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    return bytes.decode(binascii.b2a_hex(bytes(encrypted_text, encoding="utf8")))


def decrypt_oralce(text):
    # 秘钥
    text = bytes.decode(binascii.a2b_hex(bytes(text, encoding="utf8")))
    # 密文
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
    # 执行解密密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
    return decrypted_text


def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes
