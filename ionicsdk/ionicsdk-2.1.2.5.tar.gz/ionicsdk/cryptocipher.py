"""!
    Ionic cryptographic ciphers.
"""
import ionicsdk._private as _private
from ionicsdk.exceptions import *

class CryptoCipherBase(object):
    """!
        Root Cipher class that defines the interface and includes a number of utility functions shared by all Cipher classes.
    """
    def __new__(cls, *args, **kwargs): # The base class should not be used directly
        if cls is CryptoCipherBase:
            raise NotImplementedError()
        return super(CryptoCipherBase, cls).__new__(cls)
    
    def __init__(self, ):
        """!Constructs a cipher with default values
        """
        self._cCipher = None
    
    def encryptstr(self, plaintext):
        """!Encrypts a Unicode or UTF-8 encoded string in memory.  Throws an exception on any error.
            
        @param
            plaintext (unicode or UTF-8 string): The text to encrypt
            
        @return 
            (bytes) The encrypted bytes
        """
        # inputs
        cPlainText = _private.CMarshalUtil.stringToC(plaintext)

        # outputs
        cCipherTextBytes = _private.OWNED_POINTER(_private.CBytes)()
        
        # call into C library to perform the work
        _private.cLib.ionic_rawcipher_encrypt_str(
            self._cCipher,
            cPlainText,
            _private.byref(cCipherTextBytes))

        # marshal C outputs to Python
        return _private.CMarshalUtil.bytesFromC(cCipherTextBytes)

    def encryptbytes(self, plaintextbytes):
        """!Encrypts a byte array in memory.  Throws an exception on any error.
            
        @param
            plaintextbytes (bytes): The bytes to encrypt
            
        @return
            (bytes) The encrypted bytes
        """
        # inputs
        cPlainTextBytes = _private.CMarshalUtil.bytesToC(plaintextbytes)
        
        # outputs
        cCipherTextBytes = _private.OWNED_POINTER(_private.CBytes)()
        
        # call into C library to perform the work
        _private.cLib.ionic_rawcipher_encrypt_bytes(
            self._cCipher,
            cPlainTextBytes,
            _private.byref(cCipherTextBytes))
        
        # marshal C outputs to Python
        return _private.CMarshalUtil.bytesFromC(cCipherTextBytes)

    def decryptstr(self, ciphertext):
        """!
        Decrypts ciphertext in memory to a unicode string.  Throws an exception on any error.
        
        @param
            ciphertext (bytes): The bytes to decrypt

        @return
            (unicode) The decrypted string
        """
        # inputs
        cCipherTextBytes = _private.CMarshalUtil.bytesToC(ciphertext)
        
        # outputs
        cPlainText = _private.OWNED_POINTER(_private.c_char)()
        
        # call into C library to perform the work
        _private.cLib.ionic_rawcipher_decrypt_str(
            self._cCipher,
            cCipherTextBytes,
            _private.byref(cPlainText))

        # marshal C outputs to Python
        return _private.CMarshalUtil.stringFromC(cPlainText)

    def decryptbytes(self, ciphertext):
        """!
        Decrypts ciphertext in memory to a byte array.  Throws an exception on any error.
        
        @param
            ciphertext (bytes): The bytes to decrypt
        @return
            (bytes) The decrypted bytes
        """
        # inputs
        cCipherTextBytes = _private.CMarshalUtil.bytesToC(ciphertext)
        
        # outputs
        cPlainTextBytes = _private.OWNED_POINTER(_private.CBytes)()
        
        # call into C library to perform the work
        _private.cLib.ionic_rawcipher_decrypt_bytes(
            self._cCipher,
            cCipherTextBytes,
            _private.byref(cPlainTextBytes))

        # marshal C outputs to Python
        return _private.CMarshalUtil.bytesFromC(cPlainTextBytes)

class AesCtrCipher(CryptoCipherBase):
    """!
        Cipher class that implements AES CTR.
    """
    def __init__(self, keydata):
        """!@details
            Constructs a cipher with key data.

            @param
                keydata (bytes): The key to use for encryption or decryption.
        """
        super(AesCtrCipher, self).__init__()
        self._cCipher = _private.cLib.ionic_rawcipher_create_aesctr(
            _private.CMarshalUtil.bytesToC(keydata))

class AesGcmCipher(CryptoCipherBase):
    """!
        Cipher class that implements AES GCM.
        The authentication tag is 16 bytes and will be appended to the end of the ciphertext.
    """
    def __init__(self, keydata, authdata):
        """!Constructs a cipher with key and auth data.
            @param
                keydata (bytes): The key to use for encryption or decryption.
            @param
                authdata (bytes): The AES GCM Additional Authenticated Data (AAD). If None or empty, no AAD will be used.
        """
        super(AesGcmCipher, self).__init__()
        self._cCipher = _private.cLib.ionic_rawcipher_create_aesgcm(
            _private.CMarshalUtil.bytesToC(keydata), 
            _private.CMarshalUtil.bytesToC(authdata))
