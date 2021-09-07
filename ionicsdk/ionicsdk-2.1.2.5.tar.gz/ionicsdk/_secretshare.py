from ionicsdk._common import *
from sys import maxsize

class CSecretShareData(Structure):
    pass

class CSecretSharePersistor(Structure):
    pass

class CSecretShareProfilePersistor(Structure):
    pass

class CSecretShareKeyValuePair(Structure):
    __slots__ = [
                'pszKey',
                'pszValue',
                ]
    _fields_ = [
                ('pszKey', c_char_p),
                ('pszValue', c_char_p),
                ]


class CSecretShareKeyValuePairArray(Structure):
    __slots__ = [
                'pKeyValuePairArray',
                'nSize',
                ]
    _fields_ = [
                ('pKeyValuePairArray', POINTER(CSecretShareKeyValuePair)),
                ('nSize', c_size_t),
                ]

class CSecretShareBucket(Structure):
    __slots__ = [
                'ppszKeyList',
                'nThreshold',
                'nSize',
                ]
    _fields_ = [
                ('ppszKeyList', POINTER(c_char_p)),
                ('nThreshold', c_size_t),
                ('nSize', c_size_t),
                ]

class CSecretShareBucketArray(Structure):
    __slots__ = [
                'pBucketList',
                'nSize',
                ]
    _fields_ = [
                ('pBucketList', POINTER(CSecretShareBucket)),
                ('nSize', c_size_t),
                ]

if maxsize > 2**32: # The return type should be c_void_p but a bug in ctypes corrupts the
    SecretShareCallback_getdata = CFUNCTYPE(c_uint64, POINTER(CSecretShareData))
    SecretShareCallback_getbuckets = CFUNCTYPE(c_uint64, POINTER(CSecretShareData))
else:
    SecretShareCallback_getdata = CFUNCTYPE(c_ulong, POINTER(CSecretShareData))
    SecretShareCallback_getbuckets = CFUNCTYPE(c_ulong, POINTER(CSecretShareData))

SecretShareCallback_releasedata = CFUNCTYPE(None, POINTER(CSecretShareKeyValuePairArray))
SecretShareCallback_releasebuckets = CFUNCTYPE(None, POINTER(CSecretShareBucketArray))


# Secret Share object functions
cLib.ionic_secret_share_create.argtypes = [SecretShareCallback_getdata, SecretShareCallback_getbuckets, SecretShareCallback_releasedata, SecretShareCallback_releasebuckets]
cLib.ionic_secret_share_create.restype = OWNED_POINTER(CSecretShareData)

cLib.ionic_secret_share_persistor_create.argtypes = [OWNED_POINTER(CSecretShareData)]
cLib.ionic_secret_share_persistor_create.restype = OWNED_POINTER(CSecretSharePersistor)

cLib.ionic_secret_share_persistor_set_filepath.argtypes = [OWNED_POINTER(CSecretSharePersistor), c_char_p]
cLib.ionic_secret_share_persistor_set_filepath.restype = c_int
cLib.ionic_secret_share_persistor_set_filepath.errcheck = ctypesFunctionErrorCheck

cLib.ionic_secret_share_persistor_get_key.argtypes = [OWNED_POINTER(CSecretSharePersistor), POINTER(POINTER(CBytes))]
cLib.ionic_secret_share_persistor_get_key.restype = c_int
cLib.ionic_secret_share_persistor_get_key.errcheck = ctypesFunctionErrorCheck


cLib.ionic_secret_share_profile_persistor_create.argtypes = [OWNED_POINTER(CSecretShareData)]
cLib.ionic_secret_share_profile_persistor_create.restype = OWNED_POINTER(CSecretShareProfilePersistor)

cLib.ionic_secret_share_profile_persistor_set_filepath.argtypes = [OWNED_POINTER(CSecretShareProfilePersistor), c_char_p]
cLib.ionic_secret_share_profile_persistor_set_filepath.restype = c_int
cLib.ionic_secret_share_profile_persistor_set_filepath.errcheck = ctypesFunctionErrorCheck

cLib.ionic_secret_share_profile_persistor_get_filepath.argtypes = [OWNED_POINTER(CSecretShareProfilePersistor), POINTER(c_char_p)]
cLib.ionic_secret_share_profile_persistor_get_filepath.restype = c_int
cLib.ionic_secret_share_profile_persistor_get_filepath.errcheck = ctypesFunctionErrorCheck

cLib.ionic_secret_share_profile_persistor_set_secret_share_filepath.argtypes = [OWNED_POINTER(CSecretShareProfilePersistor), c_char_p]
cLib.ionic_secret_share_profile_persistor_set_secret_share_filepath.restype = c_int
cLib.ionic_secret_share_profile_persistor_set_secret_share_filepath.errcheck = ctypesFunctionErrorCheck

cLib.ionic_secret_share_profile_persistor_get_secret_share_filepath.argtypes = [OWNED_POINTER(CSecretShareProfilePersistor), POINTER(c_char_p)]
cLib.ionic_secret_share_profile_persistor_get_secret_share_filepath.restype = c_int
cLib.ionic_secret_share_profile_persistor_get_secret_share_filepath.errcheck = ctypesFunctionErrorCheck


cLib.ionic_convert_hexbytes_to_bytes.argtypes = [c_char_p, POINTER(CBytes)]
cLib.ionic_convert_hexbytes_to_bytes.restype = c_int
cLib.ionic_convert_hexbytes_to_bytes.errcheck = ctypesFunctionErrorCheck

cLib.ionic_load_all_device_profiles.argtypes = [OWNED_POINTER(CProfilePersistor), POINTER(OWNED_POINTER(POINTER(CDeviceProfile))), POINTER(c_size_t), POINTER(OWNED_POINTER(c_char))]
cLib.ionic_load_all_device_profiles.restype = c_int
cLib.ionic_load_all_device_profiles.errcheck = ctypesFunctionErrorCheck

cLib.ionic_save_all_device_profiles.argtypes = [OWNED_POINTER(CProfilePersistor), POINTER(POINTER(CDeviceProfile)), c_size_t, c_char_p]
cLib.ionic_save_all_device_profiles.restype = c_int
cLib.ionic_save_all_device_profiles.errcheck = ctypesFunctionErrorCheck


cLib.ionic_secret_share_profile_to_device_profile.argtypes = [OWNED_POINTER(CSecretShareProfilePersistor)]
cLib.ionic_secret_share_profile_to_device_profile.restype = POINTER(CProfilePersistor)


