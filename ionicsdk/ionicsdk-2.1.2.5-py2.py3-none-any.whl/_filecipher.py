from ionicsdk._common import *
from ionicsdk._agent import *
from ionicsdk._coverpage import *
from ionicsdk._services import *

class CFileCipher(Structure):
    pass

class CFileInfo(Structure):
    __slots__ = [
        'bIsEncrypted',
        'eFamily',
        'pszCipherVersion',
        'pszKeyId',
        'pszServer',
        ]
    _fields_ = [
        ('bIsEncrypted', c_bool),
        ('eFamily', c_int),
        ('pszCipherVersion', c_char_p),
        ('pszKeyId', c_char_p),
        ('pszServer', c_char_p),
        ]

class CFileEncryptAttributes(Structure):
    __slots__ = [
        'nStructSize',
        'pAttributes',
        'pMutableAttributes',
        'pMetadata',
        'bEnablePortionMarking',
        'pszVersionOut',
        'eFamilyOut',
        'pKeyResponseOut',
        'pServerResponseOut'
        ]
    _fields_ = [
        ('nStructSize', c_size_t),
        ('pAttributes', POINTER(CAttributesMap)),
        ('pMutableAttributes', POINTER(CAttributesMap)),
        ('pMetadata', POINTER(CMetadataMap)),
        ('bEnablePortionMarking', c_bool),
        ('pszVersionOut', c_char_p),
        ('eFamilyOut', c_int),
        ('pKeyResponseOut', POINTER(CKeyData)),
        ('pServerResponseOut', POINTER(CServerResponse))
        ]

class CFileDecryptAttributes(Structure):
    __slots__ = [
        'nStructSize',
        'pMetadata',
        'bProvideAccessDeniedPageOut',
        'pszVersionOut',
        'eFamilyOut',
        'pAccessDeniedPageOut',
        'pKeyResponseOut',
        'pServerResponseOut'
        ]
    _fields_ = [
        ('nStructSize', c_size_t),
        ('pMetadata', POINTER(CMetadataMap)),
        ('bProvideAccessDeniedPageOut', c_bool),
        ('pszVersionOut', c_char_p),
        ('eFamilyOut', c_int),
        ('pAccessDeniedPageOut', POINTER(CBytes)),
        ('pKeyResponseOut', POINTER(CKeyData)),
        ('pServerResponseOut', POINTER(CServerResponse))
        ]

cLib.ionic_filecipher_create_auto.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_filecipher_create_auto.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_auto_coverpage.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CCoverPageService)]
cLib.ionic_filecipher_create_auto_coverpage.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_auto_services.argtypes = [POINTER(CServices)]
cLib.ionic_filecipher_create_auto_services.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_auto_services_coverpage.argtypes = [POINTER(CServices), OWNED_POINTER(CCoverPageService)]
cLib.ionic_filecipher_create_auto_services_coverpage.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_generic.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_filecipher_create_generic.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_generic_services.argtypes = [POINTER(CServices)]
cLib.ionic_filecipher_create_generic_services.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_openxml.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_filecipher_create_openxml.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_openxml_coverpage.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CCoverPageService)]
cLib.ionic_filecipher_create_openxml_coverpage.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_openxml_services.argtypes = [POINTER(CServices)]
cLib.ionic_filecipher_create_openxml_services.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_openxml_services_coverpage.argtypes = [POINTER(CServices), OWNED_POINTER(CCoverPageService)]
cLib.ionic_filecipher_create_openxml_services_coverpage.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_pdf.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_filecipher_create_pdf.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_pdf_coverpage.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CCoverPageService)]
cLib.ionic_filecipher_create_pdf_coverpage.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_pdf_services.argtypes = [POINTER(CServices)]
cLib.ionic_filecipher_create_pdf_services.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_pdf_services_coverpage.argtypes = [POINTER(CServices), OWNED_POINTER(CCoverPageService)]
cLib.ionic_filecipher_create_pdf_services_coverpage.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_csv.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_filecipher_create_csv.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_csv_coverpage.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CCoverPageService)]
cLib.ionic_filecipher_create_csv_coverpage.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_csv_services.argtypes = [POINTER(CServices)]
cLib.ionic_filecipher_create_csv_services.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_csv_services_coverpage.argtypes = [POINTER(CServices), OWNED_POINTER(CCoverPageService)]
cLib.ionic_filecipher_create_csv_services_coverpage.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_cms.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_filecipher_create_cms.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_create_cms_services.argtypes = [POINTER(CServices)]
cLib.ionic_filecipher_create_cms_services.restype = OWNED_POINTER(CFileCipher)

cLib.ionic_filecipher_encrypt_attributes_create.argtypes = [POINTER(CAttributesMap), POINTER(CAttributesMap), POINTER(CMetadataMap), c_bool]
cLib.ionic_filecipher_encrypt_attributes_create.restype = OWNED_POINTER(CFileEncryptAttributes)

cLib.ionic_filecipher_encrypt_attributes_create2.argtypes = [POINTER(CAttributesMap), POINTER(CAttributesMap), POINTER(CMetadataMap), c_char_p, c_bool]
cLib.ionic_filecipher_encrypt_attributes_create2.restype = OWNED_POINTER(CFileEncryptAttributes)

cLib.ionic_filecipher_decrypt_attributes_create.argtypes = [POINTER(CMetadataMap), c_bool]
cLib.ionic_filecipher_decrypt_attributes_create.restype = OWNED_POINTER(CFileDecryptAttributes)

cLib.ionic_filecipher_getinfo.argtypes = [c_char_p, POINTER(POINTER(CFileInfo))]
cLib.ionic_filecipher_getinfo.restype = c_int
cLib.ionic_filecipher_getinfo.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_getinfo_bytes.argtypes = [POINTER(CBytes), POINTER(POINTER(CFileInfo))]
cLib.ionic_filecipher_getinfo_bytes.restype = c_int
cLib.ionic_filecipher_getinfo_bytes.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt_bytes.argtypes = [OWNED_POINTER(CFileCipher), POINTER(CBytes), POINTER(POINTER(CBytes))]
cLib.ionic_filecipher_encrypt_bytes.restype = c_int
cLib.ionic_filecipher_encrypt_bytes.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt_bytes2.argtypes = [OWNED_POINTER(CFileCipher), POINTER(CBytes), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(CBytes)), POINTER(POINTER(c_char)), POINTER(c_int), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_encrypt_bytes2.restype = c_int
cLib.ionic_filecipher_encrypt_bytes2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt_bytes3.argtypes = [OWNED_POINTER(CFileCipher), POINTER(CBytes), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(CBytes)), POINTER(OWNED_POINTER(CKeyData)), POINTER(c_int), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_encrypt_bytes3.restype = c_int
cLib.ionic_filecipher_encrypt_bytes3.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt_bytes4.argtypes = [OWNED_POINTER(CFileCipher), POINTER(CBytes), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(CBytes)), POINTER(OWNED_POINTER(CKeyData)), POINTER(c_int), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_encrypt_bytes4.restype = c_int
cLib.ionic_filecipher_encrypt_bytes4.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt_bytesA.argtypes = [OWNED_POINTER(CFileCipher), POINTER(CBytes), POINTER(POINTER(CBytes)), OWNED_POINTER(CFileEncryptAttributes)]
cLib.ionic_filecipher_encrypt_bytesA.restype = c_int
cLib.ionic_filecipher_encrypt_bytesA.errcheck = ctypesFunctionErrorCheck


cLib.ionic_filecipher_decrypt_bytes.argtypes = [OWNED_POINTER(CFileCipher), POINTER(CBytes), POINTER(POINTER(CBytes))]
cLib.ionic_filecipher_decrypt_bytes.restype = c_int
cLib.ionic_filecipher_decrypt_bytes.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_decrypt_bytes2.argtypes = [OWNED_POINTER(CFileCipher), POINTER(CBytes), OWNED_POINTER(CMetadataMap), POINTER(POINTER(CBytes)), POINTER(OWNED_POINTER(CAttributesMap)), POINTER(POINTER(c_char)), POINTER(c_int), POINTER(POINTER(c_char)), POINTER(POINTER(CBytes)), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_decrypt_bytes2.restype = c_int
cLib.ionic_filecipher_decrypt_bytes2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_decrypt_bytes3.argtypes = [OWNED_POINTER(CFileCipher), POINTER(CBytes), OWNED_POINTER(CMetadataMap), POINTER(POINTER(CBytes)), POINTER(OWNED_POINTER(CKeyData)), POINTER(c_int), POINTER(POINTER(c_char)), POINTER(POINTER(CBytes)), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_decrypt_bytes3.restype = c_int
cLib.ionic_filecipher_decrypt_bytes3.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_decrypt_bytesA.argtypes = [OWNED_POINTER(CFileCipher), POINTER(CBytes), POINTER(POINTER(CBytes)), OWNED_POINTER(CFileDecryptAttributes)]
cLib.ionic_filecipher_decrypt_bytesA.restype = c_int
cLib.ionic_filecipher_decrypt_bytesA.errcheck = ctypesFunctionErrorCheck


cLib.ionic_filecipher_encrypt.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, c_char_p]
cLib.ionic_filecipher_encrypt.restype = c_int
cLib.ionic_filecipher_encrypt.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt2.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, c_char_p, OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(c_int), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_encrypt2.restype = c_int
cLib.ionic_filecipher_encrypt2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt3.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, c_char_p, OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(OWNED_POINTER(CKeyData)), POINTER(c_int), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_encrypt3.restype = c_int
cLib.ionic_filecipher_encrypt3.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt4.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, c_char_p, OWNED_POINTER(CAttributesMap), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(OWNED_POINTER(CKeyData)), POINTER(c_int), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_encrypt4.restype = c_int
cLib.ionic_filecipher_encrypt4.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encryptA.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, c_char_p, OWNED_POINTER(CFileEncryptAttributes)]
cLib.ionic_filecipher_encryptA.restype = c_int
cLib.ionic_filecipher_encryptA.errcheck = ctypesFunctionErrorCheck


cLib.ionic_filecipher_decrypt.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, c_char_p]
cLib.ionic_filecipher_decrypt.restype = c_int
cLib.ionic_filecipher_decrypt.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_decrypt2.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, c_char_p, OWNED_POINTER(CMetadataMap), POINTER(OWNED_POINTER(CAttributesMap)), POINTER(POINTER(c_char)), POINTER(c_int), POINTER(POINTER(c_char)), POINTER(POINTER(CBytes)), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_decrypt2.restype = c_int
cLib.ionic_filecipher_decrypt2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_decrypt3.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, c_char_p, OWNED_POINTER(CMetadataMap), POINTER(OWNED_POINTER(CKeyData)), POINTER(c_int), POINTER(POINTER(c_char)), POINTER(POINTER(CBytes)), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_decrypt3.restype = c_int
cLib.ionic_filecipher_decrypt3.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_decryptA.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, c_char_p, OWNED_POINTER(CFileDecryptAttributes)]
cLib.ionic_filecipher_decryptA.restype = c_int
cLib.ionic_filecipher_decryptA.errcheck = ctypesFunctionErrorCheck


cLib.ionic_filecipher_encrypt_inplace.argtypes = [OWNED_POINTER(CFileCipher), c_char_p]
cLib.ionic_filecipher_encrypt_inplace.restype = c_int
cLib.ionic_filecipher_encrypt_inplace.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt_inplace2.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(c_int), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_encrypt_inplace2.restype = c_int
cLib.ionic_filecipher_encrypt_inplace2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt_inplace3.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(OWNED_POINTER(CKeyData)), POINTER(c_int), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_encrypt_inplace3.restype = c_int
cLib.ionic_filecipher_encrypt_inplace3.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt_inplace4.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, OWNED_POINTER(CAttributesMap), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(OWNED_POINTER(CKeyData)), POINTER(c_int), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_encrypt_inplace4.restype = c_int
cLib.ionic_filecipher_encrypt_inplace4.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_encrypt_inplaceA.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, OWNED_POINTER(CFileEncryptAttributes)]
cLib.ionic_filecipher_encrypt_inplaceA.restype = c_int
cLib.ionic_filecipher_encrypt_inplaceA.errcheck = ctypesFunctionErrorCheck


cLib.ionic_filecipher_decrypt_inplace.argtypes = [OWNED_POINTER(CFileCipher), c_char_p]
cLib.ionic_filecipher_decrypt_inplace.restype = c_int
cLib.ionic_filecipher_decrypt_inplace.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_decrypt_inplace2.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, OWNED_POINTER(CMetadataMap), POINTER(OWNED_POINTER(CAttributesMap)), POINTER(POINTER(c_char)), POINTER(c_int), POINTER(POINTER(c_char)), POINTER(POINTER(CBytes)), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_decrypt_inplace2.restype = c_int
cLib.ionic_filecipher_decrypt_inplace2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_decrypt_inplace2.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, OWNED_POINTER(CMetadataMap), POINTER(OWNED_POINTER(CKeyData)), POINTER(c_int), POINTER(POINTER(c_char)), POINTER(POINTER(CBytes)), POINTER(POINTER(CServerResponse))]
cLib.ionic_filecipher_decrypt_inplace2.restype = c_int
cLib.ionic_filecipher_decrypt_inplace2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_decrypt_inplaceA.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, OWNED_POINTER(CFileDecryptAttributes)]
cLib.ionic_filecipher_decrypt_inplaceA.restype = c_int
cLib.ionic_filecipher_decrypt_inplaceA.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_getinfo_cipher.argtypes = [OWNED_POINTER(CFileCipher), c_char_p, POINTER(POINTER(CFileInfo))]
cLib.ionic_filecipher_getinfo_cipher.restype = c_int
cLib.ionic_filecipher_getinfo_cipher.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_getinfo_cipher_bytes.argtypes = [OWNED_POINTER(CFileCipher), POINTER(CBytes), POINTER(POINTER(CFileInfo))]
cLib.ionic_filecipher_getinfo_cipher_bytes.restype = c_int
cLib.ionic_filecipher_getinfo_cipher_bytes.errcheck = ctypesFunctionErrorCheck


cLib.ionic_filecipher_get_family.argtypes = [OWNED_POINTER(CFileCipher)]
cLib.ionic_filecipher_get_family.restype = c_int
cLib.ionic_filecipher_get_family.errcheck = ctypesFunctionErrorCheck

cLib.ionic_filecipher_get_family_string.argtypes = [OWNED_POINTER(CFileCipher)]
cLib.ionic_filecipher_get_family_string.restype = POINTER(c_char)

cLib.ionic_filecipher_is_version_supported.argtypes = [OWNED_POINTER(CFileCipher), c_char_p]
cLib.ionic_filecipher_is_version_supported.restype = c_bool

cLib.ionic_filecipher_get_supported_versions.argtypes = [OWNED_POINTER(CFileCipher), POINTER(c_size_t)]
cLib.ionic_filecipher_get_supported_versions.restype = POINTER(c_char_p)

cLib.ionic_filecipher_family_to_string.argtypes = [c_int]
cLib.ionic_filecipher_family_to_string.restype = POINTER(c_char)

cLib.ionic_filecipher_family_to_enum.argtypes = [c_char_p]
cLib.ionic_filecipher_family_to_enum.restype = c_int
cLib.ionic_filecipher_family_to_enum.errcheck = ctypesFunctionErrorCheck
