from ionicsdk._common import *
from ionicsdk._profilemanager import *

class CAgent(Structure):
    pass

class CGetKeyQueryResult(Structure):
    __slots__ = [
             'pszExternalKeyId',
             'nErrorCode',
             'pszErrorMessage',
             'ppszKeyIds',
             'nKeyIdCount',
             ]
    _fields_ = [
             ('pszExternalKeyId', c_char_p),
             ('nErrorCode', c_int),
             ('pszErrorMessage', c_char_p),
             ('ppszKeyIds', POINTER(c_char_p)),
             ('nKeyIdCount', c_int),
             ]

class CGetKeyQueryList(Structure):
    __slots__ = [
            'ppQueryResults',
            'nSize',
            ]
    _fields_ = [
            ('ppQueryResults', POINTER(POINTER(CGetKeyQueryResult))),
            ('nSize', c_int),
            ]

class CGetKeyError(Structure):
    __slots__ = [
            'pszKeyId',
            'nClientError',
            'nServerError',
            'pszServerMessage',
            ]
    _fields_ = [
            ('pszKeyId', c_char_p),
            ('nClientError', c_int),
            ('nServerError', c_int),
            ('pszServerMessage', c_char_p),
            ]

class CGetKeyErrorList(Structure):
    __slots__ = [
            'ppErrors',
            'nSize',
            ]
    _fields_ = [
            ('ppErrors', POINTER(POINTER(CGetKeyError))),
            ('nSize', c_int),
            ]

class CAgentConfig(Structure):
    __slots__ = [
            'pszUserAgent',
            'pszHttpImpl',
            'nHttpTimeoutSecs',
            'nMaxRedirects',
            ]
    _fields_ = [
            ('pszUserAgent', c_char_p),
            ('pszHttpImpl', c_char_p),
            ('nHttpTimeoutSecs', c_int),
            ('nMaxRedirects', c_int),
            ]

class CResourceRequest(Structure):
    __slots__ = [
            'pszRefId',
            'pszResourceId',
            'pszArgs',
            ]
    _fields_ = [
            ('pszRefId', c_char_p),
            ('pszResourceId', c_char_p),
            ('pszArgs', c_char_p),
            ]

class CResourceResponse(Structure):
    __slots__ = [
            'pszRefId',
            'pszData',
            'pszError',
            ]
    _fields_ = [
            ('pszRefId', c_char_p),
            ('pszData', c_char_p),
            ('pszError', c_char_p),
            ]

class CResourceResponseArray(Structure):
    __slots__ = [
            'ppResponseArray',
            'nSize',
            ]
    _fields_ = [
            ('ppResponseArray', POINTER(POINTER(CResourceResponse))),
            ('nSize', c_size_t),
            ]

class CKeyspaceResponse(Structure):
    __slots__ = [
            'pszFqdn',
            'pszTenantId',
            'pszEnrollUrl',
            'pszApiUrl',
            ]
    _fields_ = [
            ('pszFqdn', c_char_p),
            ('pszTenantId', c_char_p),
            ('pszEnrollUrl', c_char_p),
            ('pszApiUrl', c_char_p),
            ]

class CCreateKeysRequest(Structure):
    pass

cLib.ionic_agent_create.argtypes = [OWNED_POINTER(CProfilePersistor), POINTER(CAgentConfig)]
cLib.ionic_agent_create.restype = OWNED_POINTER(CAgent)

cLib.ionic_agent_create_without_profiles.argtypes = [POINTER(CAgentConfig)]
cLib.ionic_agent_create_without_profiles.restype = OWNED_POINTER(CAgent)

cLib.ionic_agent_create_with_manager.argtypes = [OWNED_POINTER(CProfileManager), POINTER(CAgentConfig)]
cLib.ionic_agent_create_with_manager.restype = OWNED_POINTER(CAgent) 

cLib.ionic_agent_clone.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_agent_clone.restype = OWNED_POINTER(CAgent)

cLib.ionic_agent_get_profile_manager.argtypes = [POINTER(CAgent)]
cLib.ionic_agent_get_profile_manager.restype = OWNED_POINTER(CProfileManager)

cLib.ionic_agent_has_active_profile.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_agent_has_active_profile.restype = c_bool

cLib.ionic_agent_set_active_profile.argtypes = [OWNED_POINTER(CAgent), c_char_p]
cLib.ionic_agent_set_active_profile.restype = c_int
cLib.ionic_agent_set_active_profile.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_get_active_profile.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_agent_get_active_profile.restype = OWNED_POINTER(CDeviceProfile)

cLib.ionic_agent_has_any_profiles.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_agent_has_any_profiles.restype = c_bool

cLib.ionic_agent_get_all_profiles.argtypes = [OWNED_POINTER(CAgent), POINTER(c_size_t)]
cLib.ionic_agent_get_all_profiles.restype = OWNED_POINTER(POINTER(CDeviceProfile))

cLib.ionic_agent_get_profile_for_key_id.argtypes = [OWNED_POINTER(CAgent), c_char_p]
cLib.ionic_agent_get_profile_for_key_id.restype = OWNED_POINTER(CDeviceProfile)

cLib.ionic_agent_set_all_profiles.argtypes = [OWNED_POINTER(CAgent), POINTER(POINTER(CDeviceProfile)), c_size_t]
cLib.ionic_agent_set_all_profiles.restype = c_int
cLib.ionic_agent_set_all_profiles.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_add_profile.argtypes = [OWNED_POINTER(CAgent), POINTER(CDeviceProfile), c_bool]
cLib.ionic_agent_add_profile.restype = c_int
cLib.ionic_agent_add_profile.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_rmv_profile.argtypes = [OWNED_POINTER(CAgent), c_char_p]
cLib.ionic_agent_rmv_profile.restype = c_int
cLib.ionic_agent_rmv_profile.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_get_metadata_all.argtypes = [OWNED_POINTER(CAgent)]
cLib.ionic_agent_get_metadata_all.restype = OWNED_POINTER(CMetadataMap)

cLib.ionic_agent_set_metadata_all.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CMetadataMap)]
cLib.ionic_agent_set_metadata_all.restype = c_int
cLib.ionic_agent_set_metadata_all.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_set_metadata.argtypes = [OWNED_POINTER(CAgent), c_char_p, c_char_p]
cLib.ionic_agent_set_metadata.restype = c_int
cLib.ionic_agent_set_metadata.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_add_metadata.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CMetadataMap)]
cLib.ionic_agent_add_metadata.restype = c_int
cLib.ionic_agent_add_metadata.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_rmv_metadata.argtypes = [OWNED_POINTER(CAgent), c_char_p]
cLib.ionic_agent_rmv_metadata.restype = c_int
cLib.ionic_agent_rmv_metadata.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_get_metadata.argtypes = [OWNED_POINTER(CAgent), c_char_p]
cLib.ionic_agent_get_metadata.restype = OWNED_POINTER(c_char)

cLib.ionic_agent_get_metadata_keys_array.argtypes = [OWNED_POINTER(CAgent), POINTER(c_size_t)]
cLib.ionic_agent_get_metadata_keys_array.restype = OWNED_POINTER(c_char)

cLib.ionic_metadata_collector_process_environment.argtypes = [POINTER(c_char_p), c_size_t]
cLib.ionic_metadata_collector_process_environment.restype = OWNED_POINTER(CMetadataMap)

cLib.ionic_metadata_collector_network.argtypes = []
cLib.ionic_metadata_collector_network.restype = OWNED_POINTER(CMetadataMap)

IONIC_AGENT_META_CLIENT_TYPE = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_AGENT_META_CLIENT_TYPE').value)
IONIC_AGENT_META_CLIENT_VERSION = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_AGENT_META_CLIENT_VERSION').value)
IONIC_AGENT_META_APPLICATION_NAME = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_AGENT_META_APPLICATION_NAME').value)
IONIC_AGENT_META_APPLICATION_VERSION = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_AGENT_META_APPLICATION_VERSION').value)
IONIC_AGENT_META_SAVED_FROM = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_AGENT_META_SAVED_FROM').value)
IONIC_AGENT_META_HOSTNAME = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_AGENT_META_HOSTNAME').value)
IONIC_AGENT_META_MAC_ADDRS = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_AGENT_META_MAC_ADDRS').value)
IONIC_AGENT_META_IFACE_ADDRS = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_AGENT_META_IFACE_ADDRS').value)

cLib.ionic_create_keydata_array.argtypes = [c_size_t,]
cLib.ionic_create_keydata_array.restype = OWNED_POINTER(CKeyDataArray)

cLib.ionic_set_keydata_in_array.argtypes = [OWNED_POINTER(CKeyDataArray), c_size_t, OWNED_POINTER(CKeyData)]
cLib.ionic_set_keydata_in_array.restype = c_int

cLib.ionic_set_keydata_in_array_with_ref.argtypes = [OWNED_POINTER(CKeyDataArray), c_size_t, OWNED_POINTER(CKeyData), c_char_p]
cLib.ionic_set_keydata_in_array_with_ref.restype = c_int

cLib.ionic_create_updatekeydata_array.argtypes = [c_size_t,]
cLib.ionic_create_updatekeydata_array.restype = OWNED_POINTER(CUpdateKeyDataArray)

cLib.ionic_set_updatekeydata_in_array.argtypes = [OWNED_POINTER(CUpdateKeyDataArray), c_size_t, OWNED_POINTER(CUpdateKeyData)]
cLib.ionic_set_updatekeydata_in_array.restype = c_int

cLib.ionic_agent_load_profiles.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CProfilePersistor)]
cLib.ionic_agent_load_profiles.restype = c_int
cLib.ionic_agent_load_profiles.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_save_profiles.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CProfilePersistor)]
cLib.ionic_agent_save_profiles.restype = c_int
cLib.ionic_agent_save_profiles.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_create_device.argtypes = [OWNED_POINTER(CAgent), c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, POINTER(POINTER(CDeviceProfile)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_create_device.restype = c_int
cLib.ionic_agent_create_device.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_create_key.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(CKeyData)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_create_key.restype = c_int
cLib.ionic_agent_create_key.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_create_key2.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CMetadataMap), POINTER(POINTER(CKeyData)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_create_key2.restype = c_int
cLib.ionic_agent_create_key2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_create_keys3.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CCreateKeysRequest), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_create_keys3.restype = c_int
cLib.ionic_agent_create_keys3.errcheck = ctypesFunctionErrorCheck

cLib.ionic_create_keys_request_create.argtypes = []
cLib.ionic_create_keys_request_create.restype = OWNED_POINTER(CCreateKeysRequest)

cLib.ionic_create_keys_request_add.argtypes = [OWNED_POINTER(CCreateKeysRequest), c_char_p, OWNED_POINTER(CAttributesMap), OWNED_POINTER(CAttributesMap), c_int]
cLib.ionic_create_keys_request_add.restype = c_int
cLib.ionic_create_keys_request_add.errcheck = ctypesFunctionErrorCheck

cLib.ionic_create_keys_request_get_count.argtypes = [OWNED_POINTER(CCreateKeysRequest), POINTER(c_int)]
cLib.ionic_create_keys_request_get_count.restype = c_int
cLib.ionic_create_keys_request_get_count.errcheck = ctypesFunctionErrorCheck

cLib.ionic_create_keys_request_get.argtypes = [OWNED_POINTER(CCreateKeysRequest), c_int, POINTER(POINTER(c_char)), POINTER(POINTER(CAttributesMap)), POINTER(POINTER(CAttributesMap)), POINTER(c_int)]
cLib.ionic_create_keys_request_get.restype = c_int
cLib.ionic_create_keys_request_get.errcheck = ctypesFunctionErrorCheck

cLib.ionic_create_keys_request_set_metadata.argtypes = [OWNED_POINTER(CCreateKeysRequest), OWNED_POINTER(CMetadataMap)]
cLib.ionic_create_keys_request_set_metadata.restype = c_int
cLib.ionic_create_keys_request_set_metadata.errcheck = ctypesFunctionErrorCheck

cLib.ionic_create_keys_request_get_metadata.argtypes = [OWNED_POINTER(CCreateKeysRequest), POINTER(POINTER(CMetadataMap))]
cLib.ionic_create_keys_request_get_metadata.restype = c_int
cLib.ionic_create_keys_request_get_metadata.errcheck = ctypesFunctionErrorCheck

cLib.ionic_create_keys_request_set_simulation.argtypes = [OWNED_POINTER(CCreateKeysRequest), c_bool]
cLib.ionic_create_keys_request_set_simulation.restype = c_int
cLib.ionic_create_keys_request_set_simulation.errcheck = ctypesFunctionErrorCheck

cLib.ionic_create_keys_request_get_simulation.argtypes = [OWNED_POINTER(CCreateKeysRequest), POINTER(c_bool)]
cLib.ionic_create_keys_request_get_simulation.restype = c_int
cLib.ionic_create_keys_request_get_simulation.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_create_keys.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CAttributesMap), c_size_t, OWNED_POINTER(CMetadataMap), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_create_keys.restype = c_int
cLib.ionic_agent_create_keys.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_create_keys2.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CAttributesMap), OWNED_POINTER(CAttributesMap), c_size_t, OWNED_POINTER(CMetadataMap), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_create_keys2.restype = c_int
cLib.ionic_agent_create_keys2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_get_key.argtypes = [OWNED_POINTER(CAgent), c_char_p, OWNED_POINTER(CMetadataMap), POINTER(POINTER(CKeyData)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_get_key.restype = c_int
cLib.ionic_agent_get_key.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_get_keys.argtypes = [OWNED_POINTER(CAgent), POINTER(c_char_p), c_size_t, OWNED_POINTER(CMetadataMap), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_get_keys.restype = c_int
cLib.ionic_agent_get_keys.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_get_keys2.argtypes = [OWNED_POINTER(CAgent), POINTER(c_char_p), c_size_t, POINTER(c_char_p), c_size_t, OWNED_POINTER(CMetadataMap), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CGetKeyQueryList)), POINTER(POINTER(CServerResponse)), POINTER(POINTER(CGetKeyErrorList))]
cLib.ionic_agent_get_keys.restype = c_int
cLib.ionic_agent_get_keys.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_update_key.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CUpdateKeyData), OWNED_POINTER(CMetadataMap), POINTER(POINTER(CKeyData)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_update_key.restype = c_int
cLib.ionic_agent_update_key.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_update_keys.argtypes = [OWNED_POINTER(CAgent), OWNED_POINTER(CUpdateKeyDataArray), OWNED_POINTER(CMetadataMap), POINTER(POINTER(CKeyDataArray)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_update_keys.restype = c_int
cLib.ionic_agent_update_keys.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_log_message.argtypes = [OWNED_POINTER(CAgent), c_char_p, c_char_p, OWNED_POINTER(CMetadataMap), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_log_message.restype = c_int
cLib.ionic_agent_log_message.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_log_messages.argtypes = [OWNED_POINTER(CAgent), POINTER(c_char_p), POINTER(c_char_p), c_size_t, OWNED_POINTER(CMetadataMap), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_log_messages.restype = c_int
cLib.ionic_agent_log_messages.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_create_id_assertion.argtypes = [OWNED_POINTER(CAgent), c_char_p, c_char_p, OWNED_POINTER(CMetadataMap), POINTER(POINTER(c_char)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_create_id_assertion.restype = c_int
cLib.ionic_agent_create_id_assertion.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_validate_assertion.argtypes = [OWNED_POINTER(CAgent), c_char_p, c_char_p, c_char_p, c_char_p, c_char_p]
cLib.ionic_agent_validate_assertion.restype = c_int
cLib.ionic_agent_validate_assertion.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_validate_assertion_via_enrollment.argtypes = [OWNED_POINTER(CAgent), c_char_p, c_char_p, c_char_p, c_char_p]
cLib.ionic_agent_validate_assertion_via_enrollment.restype = c_int
cLib.ionic_agent_validate_assertion_via_enrollment.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_get_resource.argtypes = [OWNED_POINTER(CAgent), POINTER(CResourceRequest), OWNED_POINTER(CMetadataMap), POINTER(POINTER(CResourceResponse)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_get_resource.restype = c_int
cLib.ionic_agent_get_resource.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_get_resources.argtypes = [OWNED_POINTER(CAgent), POINTER(POINTER(CResourceRequest)), c_size_t, OWNED_POINTER(CMetadataMap), POINTER(POINTER(CResourceResponseArray)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_get_resources.restype = c_int
cLib.ionic_agent_get_resources.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_get_keyspace_url.argtypes = [OWNED_POINTER(CAgent), c_char_p, c_char_p, POINTER(POINTER(CKeyspaceResponse)), POINTER(POINTER(CServerResponse))]
cLib.ionic_agent_get_keyspace_url.restype = c_int
cLib.ionic_agent_get_keyspace_url.errcheck = ctypesFunctionErrorCheck

cLib.ionic_agent_update_profile_from_kns.argtypes = [OWNED_POINTER(CAgent), c_char_p, c_char_p]
cLib.ionic_agent_update_profile_from_kns.restype = c_int
cLib.ionic_agent_update_profile_from_kns.errcheck = ctypesFunctionErrorCheck
