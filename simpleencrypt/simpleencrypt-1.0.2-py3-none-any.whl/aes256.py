# -*- coding: utf-8 -*-
# aes256.py
# This file is part of SimpleEncrypt project (https://github.com/shreyasnayak/SimpleEncrypt)
#
# Copyright Shreyas Nayak (c) 2021-2022 <shreyasnayak21@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__    = "Shreyas Nayak"
__email__     = "shreyasnayak21@gmail.com"
__copyright__ = "Copyright 2021-2022 Shreyas Nayak"
__license__   = "MIT"

from ctypes import *
CDLL("libcrypto.so.1.1", mode = RTLD_GLOBAL)
CDLL("libssl.so.1.1", mode = RTLD_GLOBAL)
lib = cdll.LoadLibrary('libSimpleEncrypt.so')

lib.freeme.argtypes = c_void_p,
lib.freeme.restype = None

lib.encryptMessage.argtypes = [c_char_p,c_char_p,c_char_p]
lib.encryptMessage.restype = c_void_p

lib.decryptMessage.argtypes = [c_char_p,c_char_p,c_char_p]
lib.decryptMessage.restype = c_void_p

def encrypt(plainText,iv,key):
    """
    Encrypt text with the initiation vector and key
    @param plainText: string Text to encrypt
    @param iv: string initiation vector
    @param key: string key
    @type plainText: string
    @type iv: string
    @type key: string
    @rtype: string
    """
    en_ptr = lib.encryptMessage(c_char_p(plainText),c_char_p(iv),c_char_p(key))
    value = cast(en_ptr, c_char_p).value
    lib.freeme(en_ptr)
    return value

def decrypt(ciphertext,iv,key):
    """
    Encrypt text with the initiation vector and key
    @param ciphertext: string ciphertext to decrypt
    @param iv: string initiation vector
    @param key: string key
    @type plainText: string
    @type iv: string
    @type key: string
    @rtype: string
    """
    de_ptr = lib.decryptMessage(c_char_p(ciphertext),c_char_p(iv),c_char_p(key))
    value = cast(de_ptr, c_char_p).value
    lib.freeme(de_ptr)
    return value


if __name__ == '__main__': 
    iv = b'171A065A7675A09AECEC118DBC008A822A041FC2EBF2B3E4CF7A4C966E5D5897'
    key = b'2B5442AD8739992F'
    plainText = b'TEXT'
    print(decrypt(encrypt(plainText, iv,key), iv,key))
