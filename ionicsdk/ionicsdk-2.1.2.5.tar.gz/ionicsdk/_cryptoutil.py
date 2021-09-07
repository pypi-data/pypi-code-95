from ionicsdk._common import *

cLib.ionic_crypto_sha256.argtypes = [POINTER(CBytes), POINTER(c_ubyte), c_size_t]
cLib.ionic_crypto_sha256.restype = c_int
cLib.ionic_crypto_sha256.errcheck = ctypesFunctionErrorCheck

cLib.ionic_crypto_sha512.argtypes = [POINTER(CBytes), POINTER(c_ubyte), c_size_t]
cLib.ionic_crypto_sha512.restype = c_int
cLib.ionic_crypto_sha512.errcheck = ctypesFunctionErrorCheck

cLib.ionic_crypto_hmac_sha256.argtypes = [POINTER(CBytes), POINTER(CBytes), POINTER(c_ubyte), c_size_t]
cLib.ionic_crypto_hmac_sha256.restype = c_int
cLib.ionic_crypto_hmac_sha256.errcheck = ctypesFunctionErrorCheck

cLib.ionic_crypto_hmac_sha512.argtypes = [POINTER(CBytes), POINTER(CBytes), POINTER(c_ubyte), c_size_t]
cLib.ionic_crypto_hmac_sha512.restype = c_int
cLib.ionic_crypto_hmac_sha512.errcheck = ctypesFunctionErrorCheck

cLib.ionic_crypto_pbkdf2.argtypes = [POINTER(CBytes), POINTER(CBytes), c_size_t, POINTER(c_ubyte), c_size_t, c_size_t]
cLib.ionic_crypto_pbkdf2.restype = c_int
cLib.ionic_crypto_pbkdf2.errcheck = ctypesFunctionErrorCheck

cLib.ionic_crypto_initialize.argtypes = []
cLib.ionic_crypto_initialize.restype = c_int
cLib.ionic_crypto_initialize.errcheck = ctypesFunctionErrorCheck

cLib.ionic_crypto_shutdown.argtypes = []
cLib.ionic_crypto_shutdown.restype = c_int
cLib.ionic_crypto_shutdown.errcheck = ctypesFunctionErrorCheck

cLib.ionic_crypto_set_crypto_shared_library_fips_mode.argtypes = [c_bool]

cLib.ionic_crypto_set_crypto_shared_library_custom_directory.argtypes = [c_char_p]

cLib.ionic_crypto_set_crypto_shared_library_custom_path.argtypes = [c_char_p]

cLib.ionic_crypto_get_crypto_shared_library_loaded_filename.argtypes = []
cLib.ionic_crypto_get_crypto_shared_library_loaded_filename.restype = c_char_p
