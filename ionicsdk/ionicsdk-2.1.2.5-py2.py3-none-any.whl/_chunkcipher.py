from ionicsdk._common import *
from ionicsdk._agent import *
from ionicsdk._services import *

class CChunkCipher(Structure):
    pass

class CChunkInfo(Structure):
    __slots__ = [
            'bIsEncrypted',
            'pszCipherId',
            'pszKeyId',
            ]
    _fields_ = [
            ('bIsEncrypted', c_bool),
            ('pszCipherId', c_char_p),
            ('pszKeyId', c_char_p),
            ]

cLib.ionic_chunkcipher_create_auto.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_chunkcipher_create_auto.restype = OWNED_POINTER(CChunkCipher)

cLib.ionic_chunkcipher_create_auto_services.argtypes = [POINTER(CServices)]
cLib.ionic_chunkcipher_create_auto_services.restype = OWNED_POINTER(CChunkCipher)

cLib.ionic_chunkcipher_create_v1.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_chunkcipher_create_v1.restype = OWNED_POINTER(CChunkCipher)

cLib.ionic_chunkcipher_create_v1_services.argtypes = [POINTER(CServices)]
cLib.ionic_chunkcipher_create_v1_services.restype = OWNED_POINTER(CChunkCipher)

cLib.ionic_chunkcipher_create_v2.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_chunkcipher_create_v2.restype = OWNED_POINTER(CChunkCipher)

cLib.ionic_chunkcipher_create_v2_services.argtypes = [POINTER(CServices)]
cLib.ionic_chunkcipher_create_v2_services.restype = OWNED_POINTER(CChunkCipher)

cLib.ionic_chunkcipher_create_v3.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_chunkcipher_create_v3.restype = OWNED_POINTER(CChunkCipher)

cLib.ionic_chunkcipher_create_v3_services.argtypes = [POINTER(CServices)]
cLib.ionic_chunkcipher_create_v3_services.restype = OWNED_POINTER(CChunkCipher)

cLib.ionic_chunkcipher_create_v4.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_chunkcipher_create_v4.restype = OWNED_POINTER(CChunkCipher)

cLib.ionic_chunkcipher_create_v4_services.argtypes = [POINTER(CServices)]
cLib.ionic_chunkcipher_create_v4_services.restype = OWNED_POINTER(CChunkCipher)

cLib.ionic_chunkcipher_getinfo_str.argtypes = [c_char_p, POINTER(POINTER(CChunkInfo))]
cLib.ionic_chunkcipher_getinfo_str.restype = c_int
cLib.ionic_chunkcipher_getinfo_str.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_getinfo_bytes.argtypes = [POINTER(CBytes), POINTER(POINTER(CChunkInfo))]
cLib.ionic_chunkcipher_getinfo_bytes.restype = c_int
cLib.ionic_chunkcipher_getinfo_bytes.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_encrypt_str.argtypes = [OWNED_POINTER(CChunkCipher), c_char_p, POINTER(POINTER(c_char))]
cLib.ionic_chunkcipher_encrypt_str.restype = c_int
cLib.ionic_chunkcipher_encrypt_str.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_encrypt_str2.argtypes = [OWNED_POINTER(CChunkCipher), c_char_p, OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(POINTER(c_char)), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_chunkcipher_encrypt_str2.restype = c_int
cLib.ionic_chunkcipher_encrypt_str2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_encrypt_str3.argtypes = [OWNED_POINTER(CChunkCipher), c_char_p, OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(OWNED_POINTER(CKeyData)), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_chunkcipher_encrypt_str3.restype = c_int
cLib.ionic_chunkcipher_encrypt_str3.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_encrypt_str4.argtypes = [OWNED_POINTER(CChunkCipher), c_char_p, OWNED_POINTER(CAttributesMap), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(OWNED_POINTER(CKeyData)), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_chunkcipher_encrypt_str4.restype = c_int
cLib.ionic_chunkcipher_encrypt_str4.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_encrypt_bytes.argtypes = [OWNED_POINTER(CChunkCipher), POINTER(CBytes), POINTER(POINTER(c_char))]
cLib.ionic_chunkcipher_encrypt_bytes.restype = c_int
cLib.ionic_chunkcipher_encrypt_bytes.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_encrypt_bytes2.argtypes = [OWNED_POINTER(CChunkCipher), POINTER(CBytes), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(POINTER(c_char)), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_chunkcipher_encrypt_bytes2.restype = c_int
cLib.ionic_chunkcipher_encrypt_bytes2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_encrypt_bytes3.argtypes = [OWNED_POINTER(CChunkCipher), POINTER(CBytes), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(OWNED_POINTER(CKeyData)), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_chunkcipher_encrypt_bytes3.restype = c_int
cLib.ionic_chunkcipher_encrypt_bytes3.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_encrypt_bytes4.argtypes = [OWNED_POINTER(CChunkCipher), POINTER(CBytes), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(OWNED_POINTER(CKeyData)), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_chunkcipher_encrypt_bytes4.restype = c_int
cLib.ionic_chunkcipher_encrypt_bytes4.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_decrypt_str.argtypes = [OWNED_POINTER(CChunkCipher), c_char_p, POINTER(POINTER(c_char))]
cLib.ionic_chunkcipher_decrypt_str.restype = c_int
cLib.ionic_chunkcipher_decrypt_str.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_decrypt_str2.argtypes = [OWNED_POINTER(CChunkCipher), c_char_p, OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(OWNED_POINTER(CAttributesMap)), POINTER(POINTER(c_char)), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_chunkcipher_decrypt_str2.restype = c_int
cLib.ionic_chunkcipher_decrypt_str2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_decrypt_str3.argtypes = [OWNED_POINTER(CChunkCipher), c_char_p, OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(OWNED_POINTER(CKeyData)), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_chunkcipher_decrypt_str3.restype = c_int
cLib.ionic_chunkcipher_decrypt_str3.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_decrypt_bytes.argtypes = [OWNED_POINTER(CChunkCipher), c_char_p, POINTER(POINTER(CBytes))]
cLib.ionic_chunkcipher_decrypt_bytes.restype = c_int
cLib.ionic_chunkcipher_decrypt_bytes.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_decrypt_bytes2.argtypes = [OWNED_POINTER(CChunkCipher), c_char_p, OWNED_POINTER(CMetadataMap), POINTER(POINTER(CBytes)), POINTER(OWNED_POINTER(CAttributesMap)), POINTER(POINTER(c_char)), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_chunkcipher_decrypt_bytes2.restype = c_int
cLib.ionic_chunkcipher_decrypt_bytes2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_decrypt_bytes3.argtypes = [OWNED_POINTER(CChunkCipher), c_char_p, OWNED_POINTER(CMetadataMap), POINTER(POINTER(CBytes)), POINTER(OWNED_POINTER(CKeyData)), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_chunkcipher_decrypt_bytes3.restype = c_int
cLib.ionic_chunkcipher_decrypt_bytes3.errcheck = ctypesFunctionErrorCheck

cLib.ionic_chunkcipher_get_id.argtypes = [OWNED_POINTER(CChunkCipher)]
cLib.ionic_chunkcipher_get_id.restype = POINTER(c_char)

cLib.ionic_chunkcipher_get_label.argtypes = [OWNED_POINTER(CChunkCipher)]
cLib.ionic_chunkcipher_get_label.restype = POINTER(c_char)
