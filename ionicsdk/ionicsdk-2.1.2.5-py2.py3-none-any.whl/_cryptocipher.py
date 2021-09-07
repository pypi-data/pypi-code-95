from ionicsdk._common import *

class CRawCipher(Structure):
    pass

cLib.ionic_rawcipher_create_aesctr.argtypes = [POINTER(CBytes)]
cLib.ionic_rawcipher_create_aesctr.restype = OWNED_POINTER(CRawCipher)

cLib.ionic_rawcipher_create_aesgcm.argtypes = [POINTER(CBytes), POINTER(CBytes)]
cLib.ionic_rawcipher_create_aesgcm.restype = OWNED_POINTER(CRawCipher)

cLib.ionic_rawcipher_encrypt_str.argtypes = [OWNED_POINTER(CRawCipher), c_char_p, POINTER(POINTER(CBytes))]
cLib.ionic_rawcipher_encrypt_str.restype = c_int
cLib.ionic_rawcipher_encrypt_str.errcheck = ctypesFunctionErrorCheck

cLib.ionic_rawcipher_encrypt_bytes.argtypes = [OWNED_POINTER(CRawCipher), POINTER(CBytes), POINTER(POINTER(CBytes))]
cLib.ionic_rawcipher_encrypt_bytes.restype = c_int
cLib.ionic_rawcipher_encrypt_bytes.errcheck = ctypesFunctionErrorCheck

cLib.ionic_rawcipher_decrypt_str.argtypes = [OWNED_POINTER(CRawCipher), POINTER(CBytes), POINTER(POINTER(c_char))]
cLib.ionic_rawcipher_decrypt_str.restype = c_int
cLib.ionic_rawcipher_decrypt_str.errcheck = ctypesFunctionErrorCheck

cLib.ionic_rawcipher_decrypt_bytes.argtypes = [OWNED_POINTER(CRawCipher), POINTER(CBytes), POINTER(POINTER(CBytes))]
cLib.ionic_rawcipher_decrypt_bytes.restype = c_int
cLib.ionic_rawcipher_decrypt_bytes.errcheck = ctypesFunctionErrorCheck
