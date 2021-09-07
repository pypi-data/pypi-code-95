from ionicsdk._common import *

class CProfileManager(Structure):
    pass

cLib.ionic_profile_manager_create.argtypes = []
cLib.ionic_profile_manager_create.restype = OWNED_POINTER(CProfileManager)

cLib.ionic_profile_manager_create_from_json.argtypes = [c_char_p, ]
cLib.ionic_profile_manager_create_from_json.restype = OWNED_POINTER(CProfileManager)

cLib.ionic_profile_manager_has_active_profile.argtypes = [OWNED_POINTER(CProfileManager)]
cLib.ionic_profile_manager_has_active_profile.restype = c_bool

cLib.ionic_profile_manager_set_active_profile.argtypes = [OWNED_POINTER(CProfileManager), c_char_p]
cLib.ionic_profile_manager_set_active_profile.restype = c_int
cLib.ionic_profile_manager_set_active_profile.errcheck = ctypesFunctionErrorCheck

cLib.ionic_profile_manager_get_active_profile.argtypes = [OWNED_POINTER(CProfileManager)]
cLib.ionic_profile_manager_get_active_profile.restype = OWNED_POINTER(CDeviceProfile)

cLib.ionic_profile_manager_has_any_profiles.argtypes = [OWNED_POINTER(CProfileManager)]
cLib.ionic_profile_manager_has_any_profiles.restype = c_bool

cLib.ionic_profile_manager_get_all_profiles.argtypes = [OWNED_POINTER(CProfileManager), POINTER(c_size_t)]
cLib.ionic_profile_manager_get_all_profiles.restype = OWNED_POINTER(POINTER(CDeviceProfile))

cLib.ionic_profile_manager_get_profile_for_key_id.argtypes = [OWNED_POINTER(CProfileManager), c_char_p]
cLib.ionic_profile_manager_get_profile_for_key_id.restype = OWNED_POINTER(CDeviceProfile)

cLib.ionic_profile_manager_set_all_profiles.argtypes = [OWNED_POINTER(CProfileManager), POINTER(POINTER(CDeviceProfile)), c_size_t]
cLib.ionic_profile_manager_set_all_profiles.restype = c_int
cLib.ionic_profile_manager_set_all_profiles.errcheck = ctypesFunctionErrorCheck

cLib.ionic_profile_manager_add_profile.argtypes = [OWNED_POINTER(CProfileManager), POINTER(CDeviceProfile), c_bool]
cLib.ionic_profile_manager_add_profile.restype = c_int
cLib.ionic_profile_manager_add_profile.errcheck = ctypesFunctionErrorCheck

cLib.ionic_profile_manager_rmv_profile.argtypes = [OWNED_POINTER(CProfileManager), c_char_p]
cLib.ionic_profile_manager_rmv_profile.restype = c_int
cLib.ionic_profile_manager_rmv_profile.errcheck = ctypesFunctionErrorCheck

cLib.ionic_profile_manager_load_profiles.argtypes = [OWNED_POINTER(CProfileManager), OWNED_POINTER(CProfilePersistor)]
cLib.ionic_profile_manager_load_profiles.restype = c_int
cLib.ionic_profile_manager_load_profiles.errcheck = ctypesFunctionErrorCheck

cLib.ionic_profile_manager_save_profiles.argtypes = [OWNED_POINTER(CProfileManager), OWNED_POINTER(CProfilePersistor)]
cLib.ionic_profile_manager_save_profiles.restype = c_int
cLib.ionic_profile_manager_save_profiles.errcheck = ctypesFunctionErrorCheck

cLib.ionic_profile_manager_load_from_json.argtypes = [OWNED_POINTER(CProfileManager), c_char_p]
cLib.ionic_profile_manager_load_from_json.restype = c_int
cLib.ionic_profile_manager_load_from_json.errcheck = ctypesFunctionErrorCheck

cLib.ionic_profile_manager_save_to_json.argtypes = [OWNED_POINTER(CProfileManager)]
cLib.ionic_profile_manager_save_to_json.restype = OWNED_POINTER(c_char)
