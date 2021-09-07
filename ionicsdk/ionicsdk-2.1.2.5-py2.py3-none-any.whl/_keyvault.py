from ionicsdk._common import *
import os, platform

class CKeyVault(Structure):
    pass

class CKeyVaultKey(Structure):
    pass

class CGetKeyVaultRecord(Structure):
    __slots__ = [
        'pszKeyId',
        'keyBytes',
        'pAttributesMap',
        'pMutableAttributesMap',
        'pObligationsMap',
        'lIssuedServerTimeUtcSeconds',
        'lExpirationServerTimeUtcSeconds',
        'eState',
        ]
    _fields_ = [
        ('pszKeyId', c_char_p),
        ('keyBytes', CBytes),
        ('pAttributesMap', POINTER(CAttributesMap)), # note that this is NOT an owned pointer because the parent struct actually owns it
        ('pMutableAttributesMap', POINTER(CAttributesMap)), # note that this is NOT an owned pointer because the parent struct actually owns it
        ('pObligationsMap', POINTER(CObligationsMap)), # similar
        ('lIssuedServerTimeUtcSeconds', c_int64),
        ('lExpirationServerTimeUtcSeconds', c_int64),
        ('eState', c_int),
        ]

class CGetKeyVaultRecordList(Structure):
    __slots__ = [
        'ppKeyArray',
        'nSize',
        ]
    _fields_ = [
        ('ppKeyArray', POINTER(POINTER(CGetKeyVaultRecord))),
        ('nSize', c_int),
        ]

KeyVaultCustomCallback_sync = CFUNCTYPE(c_int, c_void_p, POINTER(CGetKeyVaultRecordList))
KeyVaultCustomCallback_save = CFUNCTYPE(c_int, c_void_p, POINTER(CGetKeyVaultRecordList))
KeyVaultCustomCallback_load = CFUNCTYPE(c_int, c_void_p, POINTER(POINTER(CGetKeyVaultRecordList)))
KeyVaultCustomCallback_clean = CFUNCTYPE(c_int, c_void_p)
KeyVaultCustomCallback_release = CFUNCTYPE(None, POINTER(CGetKeyVaultRecordList))


cLib.ionic_keyvault_getcurrent_server_time_utc_seconds.argtypes = []
cLib.ionic_keyvault_getcurrent_server_time_utc_seconds.restype = c_int64

cLib.ionic_keyvault_create_custom_vault.argtypes = [c_char_p, c_char_p, c_int]
cLib.ionic_keyvault_create_custom_vault.restype = OWNED_POINTER(CKeyVault)

cLib.ionic_keyvaultcustom_set_sync_function.argtypes = [OWNED_POINTER(CKeyVault), KeyVaultCustomCallback_sync]
cLib.ionic_keyvaultcustom_set_file_functions.argtypes = [OWNED_POINTER(CKeyVault), KeyVaultCustomCallback_save, KeyVaultCustomCallback_load, KeyVaultCustomCallback_release]
cLib.ionic_keyvaultcustom_set_clean_functions.argtypes = [OWNED_POINTER(CKeyVault), KeyVaultCustomCallback_clean]
# key management functions (required by ISKeyVaultInterface)
cLib.ionic_keyvault_setkey.argtypes = [OWNED_POINTER(CKeyVault), POINTER(CGetKeyVaultRecord), c_int]
cLib.ionic_keyvault_setkey.restype = c_int

cLib.ionic_keyvault_getkey.argtypes = [OWNED_POINTER(CKeyVault), c_char_p, POINTER(POINTER(CGetKeyVaultRecord))]
cLib.ionic_keyvault_getkey.restype = c_int

cLib.ionic_keyvault_getkeys.argtypes = [OWNED_POINTER(CKeyVault), POINTER(c_char_p), c_int, POINTER(POINTER(CGetKeyVaultRecordList))]
cLib.ionic_keyvault_getkeys.restype = c_int

cLib.ionic_keyvault_getallkey_ids.argtypes = [OWNED_POINTER(CKeyVault), POINTER(POINTER(c_char_p)), POINTER(c_int)]
cLib.ionic_keyvault_getallkey_ids = c_int

cLib.ionic_keyvault_getallkeys.argtypes = [OWNED_POINTER(CKeyVault), POINTER(POINTER(CGetKeyVaultRecordList))]
cLib.ionic_keyvault_getallkeys.restype = c_int

cLib.ionic_keyvault_getkey_count.argtypes = [OWNED_POINTER(CKeyVault)]
cLib.ionic_keyvault_getkey_count.restype = c_int

cLib.ionic_keyvault_haskey.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]
cLib.ionic_keyvault_haskey.restype = c_bool

cLib.ionic_keyvault_removekey_by_key.argtypes = [OWNED_POINTER(CKeyVault), POINTER(CGetKeyVaultRecord)]
cLib.ionic_keyvault_removekey_by_key.restype = c_int

cLib.ionic_keyvault_removekey_by_id.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]
cLib.ionic_keyvault_removekey_by_id.restype = c_int

cLib.ionic_keyvault_removekeys.argtypes = [OWNED_POINTER(CKeyVault), POINTER(c_char_p), c_int, POINTER(POINTER(c_char_p)), POINTER(c_int)]
cLib.ionic_keyvault_removekeys.restype = c_int

cLib.ionic_keyvault_clearallkeys.argtypes = [OWNED_POINTER(CKeyVault)]
cLib.ionic_keyvault_clearallkeys.restype = c_int

# key expiration / purging functions (required by ISKeyVaultInterface)
cLib.ionic_keyvault_expirekeys.argtypes = [OWNED_POINTER(CKeyVault), c_int, POINTER(POINTER(c_char_p)), POINTER(c_int)]
cLib.ionic_keyvault_expirekeys.restype = c_int

# persistence functions (required by ISKeyVaultInterface)
cLib.ionic_keyvault_sync.argtypes = [OWNED_POINTER(CKeyVault)]
cLib.ionic_keyvault_sync.restype = c_int

cLib.ionic_keyvault_haschanges.argtypes = [OWNED_POINTER(CKeyVault)]
cLib.ionic_keyvault_haschanges.restype = c_bool

cLib.ionic_keyvault_clean_vault_store.argtypes = [OWNED_POINTER(CKeyVault)]

cLib.ionic_keyvaultcustom_updatekeystate.argtypes = [OWNED_POINTER(CKeyVault), c_char_p, c_int]
cLib.ionic_keyvaultcustom_updatekeystate.restype = c_int

cLib.ionic_keyvaultcustom_getkeystate.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]
cLib.ionic_keyvaultcustom_getkeystate.restype = c_int

cLib.ionic_keyvaultcustom_deletekey.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]
cLib.ionic_keyvaultcustom_deletekey.restype = c_int


def isWin():
    winVer = platform.win32_ver()
    if winVer is None or winVer[0] is None or 0 == len(winVer[0]):
        return False
    return True

def isMac():
    macVer = platform.mac_ver()
    if macVer is None or macVer[0] is None or 0 == len(macVer[0]):
        return False
    return True

def isLinux():
    return (os.name == 'posix') and not isMac()


if isMac():
    cLib.ionic_keyvault_create_apple_keychain_vault.argtypes = [POINTER(CBytes), POINTER(CBytes)]
    cLib.ionic_keyvault_create_apple_keychain_vault.restype = OWNED_POINTER(CKeyVault)

    cLib.ionic_keyvault_apple_keychain_get_protection_key.argtypes = [OWNED_POINTER(CKeyVault)]
    cLib.ionic_keyvault_apple_keychain_get_protection_key.restype = OWNED_POINTER(CBytes)

    cLib.ionic_keyvault_apple_keychain_get_protection_authdata.argtypes = [OWNED_POINTER(CKeyVault)]
    cLib.ionic_keyvault_apple_keychain_get_protection_authdata.restype = OWNED_POINTER(CBytes)

    cLib.ionic_keyvault_apple_keychain_get_service_name.argtypes = [OWNED_POINTER(CKeyVault)]
    cLib.ionic_keyvault_apple_keychain_get_service_name.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_apple_keychain_get_account_name.argtypes = [OWNED_POINTER(CKeyVault)]
    cLib.ionic_keyvault_apple_keychain_get_account_name.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_apple_keychain_get_access_group.argtypes = [OWNED_POINTER(CKeyVault)]
    cLib.ionic_keyvault_apple_keychain_get_access_group.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_apple_keychain_get_default_service_name.argtypes = []
    cLib.ionic_keyvault_apple_keychain_get_default_service_name.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_apple_keychain_get_default_account_name.argtypes = []
    cLib.ionic_keyvault_apple_keychain_get_default_account_name.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_apple_keychain_set_protection_key.argtypes = [OWNED_POINTER(CKeyVault), POINTER(CBytes)]

    cLib.ionic_keyvault_apple_keychain_set_protection_authdata.argtypes = [OWNED_POINTER(CKeyVault), POINTER(CBytes)]

    cLib.ionic_keyvault_apple_keychain_set_service_name.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]

    cLib.ionic_keyvault_apple_keychain_set_account_name.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]

    cLib.ionic_keyvault_apple_keychain_set_access_group.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]

if isMac():
    cLib.ionic_keyvault_create_mac_vault.argtypes = [c_char_p]
    cLib.ionic_keyvault_create_mac_vault.restype = OWNED_POINTER(CKeyVault)


    cLib.ionic_keyvault_mac_get_service_name.argtypes = [OWNED_POINTER(CKeyVault)]
    cLib.ionic_keyvault_mac_get_service_name.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_mac_get_account_name.argtypes = [OWNED_POINTER(CKeyVault)]
    cLib.ionic_keyvault_mac_get_account_name.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_mac_get_default_service_name.argtypes = []
    cLib.ionic_keyvault_mac_get_default_service_name.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_mac_get_default_account_name.argtypes = []
    cLib.ionic_keyvault_mac_get_default_account_name.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_mac_get_default_file_path.argtypes = []
    cLib.ionic_keyvault_mac_get_default_file_path.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_mac_get_file_path.argtypes = [OWNED_POINTER(CKeyVault)]
    cLib.ionic_keyvault_mac_get_file_path.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_mac_set_service_name.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]

    cLib.ionic_keyvault_mac_set_account_name.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]

    cLib.ionic_keyvault_mac_set_file_path.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]


if isWin():
    cLib.ionic_keyvault_create_windows_dpapi_vault.argtypes = [c_char_p]
    cLib.ionic_keyvault_create_windows_dpapi_vault.restype = OWNED_POINTER(CKeyVault)

    cLib.ionic_keyvault_windows_dpapi_get_default_file_path.argtypes = []
    cLib.ionic_keyvault_windows_dpapi_get_default_file_path.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_windows_dpapi_get_file_path.argtypes = [OWNED_POINTER(CKeyVault)]
    cLib.ionic_keyvault_windows_dpapi_get_file_path.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_windows_dpapi_set_file_path.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]

if isLinux():
    cLib.ionic_keyvault_create_linux_vault.argtypes = [c_char_p]
    cLib.ionic_keyvault_create_linux_vault.restype = OWNED_POINTER(CKeyVault)

    cLib.ionic_keyvault_linux_get_default_file_path.argtypes = []
    cLib.ionic_keyvault_linux_get_default_file_path.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_linux_get_file_path.argtypes = [OWNED_POINTER(CKeyVault)]
    cLib.ionic_keyvault_linux_get_file_path.restype = OWNED_POINTER(c_char)

    cLib.ionic_keyvault_linux_set_file_path.argtypes = [OWNED_POINTER(CKeyVault), c_char_p]

