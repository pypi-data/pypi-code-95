from ionicsdk._common import *

LogCallback = CFUNCTYPE(c_int, c_int, c_char_p)

cLib.ionic_log.argtypes = [c_int, c_char_p, c_int, c_char_p, c_char_p]
cLib.ionic_log.restype = c_int
cLib.ionic_log.errcheck = ctypesFunctionErrorCheck

cLib.ionic_log_setup_simple.argtypes = [c_char_p, c_bool, c_int]
cLib.ionic_log_setup_simple.restype = c_int
cLib.ionic_log_setup_simple.errcheck = ctypesFunctionErrorCheck

cLib.ionic_log_setup_from_config_json.argtypes = [c_char_p, c_char_p]
cLib.ionic_log_setup_from_config_json.restype = c_int
cLib.ionic_log_setup_from_config_json.errcheck = ctypesFunctionErrorCheck

cLib.ionic_log_setup_from_config_file.argtypes = [c_char_p, c_char_p]
cLib.ionic_log_setup_from_config_file.restype = c_int
cLib.ionic_log_setup_from_config_file.errcheck = ctypesFunctionErrorCheck

cLib.ionic_log_register_logger_from_callback.argtypes = [LogCallback, c_char_p]

cLib.ionic_log_setup_from_callback.argtypes = [LogCallback, c_int]
cLib.ionic_log_setup_from_callback.restype = c_int
cLib.ionic_log_setup_from_callback.errcheck = ctypesFunctionErrorCheck

cLib.ionic_log_shutdown.argtypes = []
cLib.ionic_log_shutdown.restype = c_int
cLib.ionic_log_shutdown.errcheck = ctypesFunctionErrorCheck

cLib.ionic_log_is_setup.argtypes = []
cLib.ionic_log_is_setup.restype = c_bool
