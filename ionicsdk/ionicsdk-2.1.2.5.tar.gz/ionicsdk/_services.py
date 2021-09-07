from ionicsdk._common import *
from ionicsdk._agent import *
from sys import maxsize

ServicesCallback_has_active_profile = CFUNCTYPE(c_bool, c_void_p)

if maxsize > 2**32: # The return type should be c_void_p but a bug in ctypes corrupts the pointer
    ServicesCallback_get_active_profile = CFUNCTYPE(c_uint64, c_void_p)
else:
    ServicesCallback_get_active_profile = CFUNCTYPE(c_ulong, c_void_p)

ServicesCallback_create_key = CFUNCTYPE(c_int, c_void_p, POINTER(CAttributesMap), POINTER(CMetadataMap), POINTER(POINTER(CKeyData)), POINTER(POINTER(CServerResponse)))
ServicesCallback_create_key2 = CFUNCTYPE(c_int, c_void_p, POINTER(CAttributesMap), POINTER(CAttributesMap), POINTER(CMetadataMap), POINTER(POINTER(CKeyData)), POINTER(POINTER(CServerResponse)))
ServicesCallback_create_keys = CFUNCTYPE(c_int, c_void_p, POINTER(CAttributesMap), c_size_t, POINTER(CMetadataMap), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse)))
ServicesCallback_create_keys2 = CFUNCTYPE(c_int, c_void_p, POINTER(CAttributesMap), POINTER(CAttributesMap), c_size_t, POINTER(CMetadataMap), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse)))
ServicesCallback_create_keys3 = CFUNCTYPE(c_int, c_void_p, POINTER(CCreateKeysRequest), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse)))
ServicesCallback_get_key = CFUNCTYPE(c_int, c_void_p, c_char_p, POINTER(CMetadataMap), POINTER(POINTER(CKeyData)), POINTER(POINTER(CServerResponse)))
ServicesCallback_get_keys = CFUNCTYPE(c_int, c_void_p, POINTER(c_char_p), c_size_t, POINTER(CMetadataMap), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse)))
ServicesCallback_update_key = CFUNCTYPE(c_int, c_void_p, POINTER(CUpdateKeyData), POINTER(CMetadataMap), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse)))
ServicesCallback_update_keys = CFUNCTYPE(c_int, c_void_p, POINTER(CUpdateKeyDataArray), POINTER(CMetadataMap), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse)))
ServicesCallback_release_key_data = CFUNCTYPE(c_int, c_void_p, c_void_p)
ServicesCallback_release_key_data_array = CFUNCTYPE(c_int, c_void_p, c_void_p)
ServicesCallback_release_update_key_data = CFUNCTYPE(c_int, c_void_p, c_void_p)
ServicesCallback_release_update_key_data_array = CFUNCTYPE(c_int, c_void_p, c_void_p)
ServicesCallback_release_server_response = CFUNCTYPE(c_int, c_void_p, c_void_p)
ServicesCallback_release_device_profile = CFUNCTYPE(c_int, c_void_p, c_void_p)


class CServices(Structure):
    __slots__ = [
        'pContext',
        'pfHasActiveProfile',
        'pfGetActiveProfile',
        'pfCreateKey',
        'pfCreateKeys',
        'pfGetKey',
        'pfGetKeys',
        'pfReleaseKeyData',
        'pfReleaseKeyDataArray',
        'pfReleaseServerResponse',
        'pfReleaseDeviceProfile',
        'pfCreateKey2',
        'pfCreateKeys2',
        'pfUpdateKey',
        'pfUpdateKeys',
        'pfReleaseUpdateKeyData',
        'pfReleaseUpdateKeyDataArray',
        'pfCreateKeys3',
    ]
    _fields_ = [
        ('pContext', c_void_p),
        ('pfHasActiveProfile', ServicesCallback_has_active_profile),
        ('pfGetActiveProfile', ServicesCallback_get_active_profile),
        ('pfCreateKey', ServicesCallback_create_key),
        ('pfCreateKeys', ServicesCallback_create_keys),
        ('pfGetKey', ServicesCallback_get_key),
        ('pfGetKeys', ServicesCallback_get_keys),
        ('pfReleaseKeyData', ServicesCallback_release_key_data),
        ('pfReleaseKeyDataArray', ServicesCallback_release_key_data_array),
        ('pfReleaseServerResponse', ServicesCallback_release_server_response),
        ('pfReleaseDeviceProfile', ServicesCallback_release_device_profile),
        ('pfCreateKey2', ServicesCallback_create_key2),
        ('pfCreateKeys2', ServicesCallback_create_keys2),
        ('pfUpdateKey', ServicesCallback_update_key),
        ('pfUpdateKeys', ServicesCallback_update_keys),
        ('pfReleaseUpdateKeyData', ServicesCallback_release_update_key_data),
        ('pfReleaseUpdateKeyDataArray', ServicesCallback_release_update_key_data_array),
        ('pfCreateKeys3', ServicesCallback_create_keys3),
    ]

