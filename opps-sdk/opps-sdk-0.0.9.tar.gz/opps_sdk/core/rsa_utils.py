# -*- coding: utf-8 -*-
import base64

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5  # 加密解密模块
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15  # 加签验签模块


#  公钥加密，单次加密串的长度最大为(key_size/8 - 11)，本次以2048为例
# 公钥加密
def rsa_long_encrypt(message, my_rsa_public):
    try:
        if not message:
            return ""
        msg = message.encode('utf-8')  # 待加密信息转成utf-8形式
        length = len(msg)
        default_length = 245
        pubobj = Cipher_pkcs1_v1_5.new(RSA.importKey(my_rsa_public))
        # 长度不用分段
        if length < default_length:
            return base64.b64encode(pubobj.encrypt(msg))
        # 需要分段
        offset = 0
        res = []
        while length - offset > 0:
            if length - offset > default_length:
                res.append(pubobj.encrypt(msg[offset:offset + default_length]))
            else:
                res.append(pubobj.encrypt(msg[offset:]))
            offset += default_length
        byte_data = b''.join(res)
        return base64.b64encode(byte_data)  # 对返回内容以base64编码
    except Exception as ex:
        return str(ex)

# 私钥解密
def rsa_long_decrypt(message, my_rsa_private):
    try:
        msg = base64.b64decode(message)
        length = len(msg)
        default_length = 256
        # 私钥解密
        priobj = Cipher_pkcs1_v1_5.new(RSA.importKey(my_rsa_private))
        # 长度不用分段
        if length < default_length:
            return b''.join(priobj.decrypt(msg, b'xyz'))
        # 需要分段
        offset = 0
        res = []
        while length - offset > 0:
            if length - offset > default_length:
                res.append(priobj.decrypt(msg[offset:offset + default_length], b'xyz'))
            else:
                res.append(priobj.decrypt(msg[offset:], b'xyz'))
            offset += default_length
            m = b''.join(res)
            n = m.decode("utf-8")
        return n
    except Exception as ex:
        return str(ex)

# 私钥加签
def rsa_sign(private_key, message, charset):
    try:
        private_key = add_start_end(private_key, "-----BEGIN PRIVATE KEY-----\n", "\n-----END PRIVATE KEY-----")
        msg = message.encode(charset)
        private_key = RSA.importKey(private_key)
        # message做“哈希”处理，RSA签名这么要求的
        hash_obj = SHA256.new(msg)
        signature = pkcs1_15.new(private_key).sign(hash_obj)
        return True, base64.b64encode(signature).decode(charset)
    except Exception as ex:
        return False, str(ex)


# 公钥验签
def rsa_design(signature, message, my_rsa_public):
    try:
        my_rsa_public = fill_public_key_marker(my_rsa_public)
        message = message.encode("utf-8")
        public_key = RSA.importKey(my_rsa_public)
        # message做“哈希”处理，RSA签名这么要求的
        hash_obj = SHA256.new(message)

        pkcs1_15.new(public_key).verify(hash_obj, base64.b64decode(signature))
        return True, ''
    except (ValueError, TypeError) as ex:
        return False, str(ex)


def add_start_end(key, start_marker, end_marker):
    if key.find(start_marker) < 0:
        key = start_marker + key
    if key.find(end_marker) < 0:
        key = key + end_marker
    return key


def fill_private_key_marker(private_key):
    return add_start_end(private_key, "-----BEGIN PRIVATE KEY-----\n", "\n-----END PRIVATE KEY-----")


def fill_public_key_marker(public_key):
    return add_start_end(public_key, "-----BEGIN PUBLIC KEY-----\n", "\n-----END PUBLIC KEY-----")
