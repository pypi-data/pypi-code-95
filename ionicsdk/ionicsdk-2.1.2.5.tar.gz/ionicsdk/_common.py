import os, sys, types
import weakref
from ctypes import *
from ionicsdk.exceptions import *
from ionicsdk._util import *
    
class IonicDll(object):
    @staticmethod
    def loadDll():
        cLibReturn = None
        cDLLPath = os.path.dirname(os.path.realpath(__file__))
        cDLLName = ''
        if os.name == 'posix':
            if sys.platform == 'mac' or sys.platform == 'darwin':
                cDLLPath = os.path.join(cDLLPath,'lib')
                cDLLNames = ('libISAgentSDKC.dylib',)
            else:
                cDLLPath = os.path.join(cDLLPath,'lib')
                cDLLNames = ('libISAgentSDKC.so',)
        else:
            if sys.maxsize > 2**32:
                cDLLPath = os.path.join(cDLLPath,'lib\\x64')
            else:
                cDLLPath = os.path.join(cDLLPath,'lib\\win32')
            cDLLNames = ('ISAgentSDKC.dll',)

        for cDLLName in cDLLNames:
            cLib = None
            cDLLFilePath = os.path.join(cDLLPath,cDLLName)
            if os.path.isfile(cDLLFilePath):
                # found library in expected location
                cLib = CDLL(cDLLFilePath)
            else:
                # search python path for alternate locations
                for d in sys.path:
                    cDLLFilePath = os.path.join(d,cDLLName)
                    if os.path.isfile(cDLLFilePath):
                        cLib = CDLL(cDLLFilePath)
                        break
            if not cLib:
                raise Exception('Could not find the native C Ionic library, please verify your Ionic Python module installation: ' + cDLLName)

            cLibReturn = cLib

        # Last lib in the lists above should be the 'C' SDK shared library
        return cLibReturn, cDLLPath

# load our Ionic SDK C library
cLib, cryptoPath = IonicDll.loadDll()
cLib.ionic_crypto_set_crypto_shared_library_custom_directory.argtypes = [c_char_p]
cCryptoPath = CMarshalUtil.stringToC(cryptoPath)
cLib.ionic_crypto_set_crypto_shared_library_custom_directory(cCryptoPath)


class CProfilePersistor(Structure):
    pass

class CMetadataMap(Structure):
    pass

class CAttributesMap(Structure):
    pass

class CObligationsMap(Structure):
    pass

class CKeyData(Structure):
    __slots__ = [
            'pszKeyId',
            'keyBytes',
            'pAttributesMap',
            'pObligationsMap',
            'pszOrigin',
            'pMutableAttributesMap',
            'pMutableAttributesFromServer',
            'pszAttributesSigBase64FromServer',
            'pszMutableAttributesSigBase64FromServer',
            ]
    _fields_ = [
            ('pszKeyId', c_char_p),
            ('keyBytes', CBytes),
            ('pAttributesMap', POINTER(CAttributesMap)), # note that this is NOT an owned pointer because the parent struct actually owns it
            ('pObligationsMap', POINTER(CObligationsMap)), # similar
            ('pszOrigin', c_char_p),
            ('pMutableAttributesMap', POINTER(CAttributesMap)), # note that this is NOT an owned pointer because the parent struct actually owns it
            ('pMutableAttributesFromServer', POINTER(CAttributesMap)), # note that this is NOT an owned pointer because the parent struct actually owns it
            ('pszAttributesSigBase64FromServer', c_char_p),
            ('pszMutableAttributesSigBase64FromServer', c_char_p),
            ]

class CKeyDataArray(Structure):
    __slots__ = [
            'ppKeyArray',
            'nSize',
            'ppszRefs',
            ]
    _fields_ = [
            ('ppKeyArray', POINTER(POINTER(CKeyData))),
            ('nSize', c_size_t),
            ('ppszRefs', POINTER(c_char_p)),
            ]

class CUpdateKeyData(Structure):
    __slots__ = [
                 'pszKeyId',
                 'keyBytes',
                 'pAttributesMap',
                 'pMutableAttributesMap',
                 'pObligationsMap',
                 'pszOrigin',
                 'pMutableAttributesFromServer',
                 'pszAttributesSigBase64FromServer',
                 'pszMutableAttributesSigBase64FromServer',
                 'bForceUpdate',
                 ]
    _fields_ = [
                 ('pszKeyId', c_char_p),
                 ('keyBytes', CBytes),
                 ('pAttributesMap', POINTER(CAttributesMap)), # note that this is NOT an owned pointer because the parent struct actually owns it
                 ('pMutableAttributesMap', POINTER(CAttributesMap)), # note that this is NOT an owned pointer because the parent struct actually owns it
                 ('pObligationsMap', POINTER(CObligationsMap)), # similar
                 ('pszOrigin', c_char_p),
                 ('pMutableAttributesFromServer', POINTER(CAttributesMap)), # note that this is NOT an owned pointer because the parent struct actually owns it
                 ('pszAttributesSigBase64FromServer', c_char_p),
                 ('pszMutableAttributesSigBase64FromServer', c_char_p),
                 ('bForceUpdate', c_int64),
                 ]

class CUpdateKeyDataArray(Structure):
    __slots__ = [
                 'ppKeyArray',
                 'nSize',
                 ]
    _fields_ = [
                 ('ppKeyArray', POINTER(POINTER(CUpdateKeyData))),
                 ('nSize', c_size_t),
                 ]

class CDeviceProfile(Structure):
    __slots__ = [
            'pszName',
            'pszDeviceId',
            'pszKeySpace',
            'pszServer',
            'nCreationTimestampSecs',
            'aesCdIdcProfileKey',
            'aesCdEiProfileKey',
            ]
    _fields_ = [
            ('pszName', c_char_p),
            ('pszDeviceId', c_char_p),
            ('pszKeySpace', c_char_p),
            ('pszServer', c_char_p),
            ('nCreationTimestampSecs', c_int64),
            ('aesCdIdcProfileKey', CBytes),
            ('aesCdEiProfileKey', CBytes),
            ]

# ----------------------------------------------------------------------------
# The OWNED_POINTER is a complement to ctypes.POINTER with the added benefit
# of automatically freeing the pointer when the pointer object is deleted (via
# ionic_release) during GC.
# ----------------------------------------------------------------------------
# this cache maps types to their owned-pointer types
_ownedPointerTypeCache = {}

def _ownedPointerDeleter(self):
    if self and cLib and cLib._handle:
        e = cLib.ionic_release(self)

def OWNED_POINTER(cls):
    try:
        return _ownedPointerTypeCache[cls]
    except KeyError:
        pass
    # create a new pointer type which is derived from ctypes.POINTER(cls). the
    # new pointer type has a __del__ function to call ionic_release() to free
    # the pointer
    ptrclass = POINTER(cls)
    newptrclassname = ptrclass.__name__ + '_OWNED'
    newptrclass = type(newptrclassname, (ptrclass, ), {'_type_' : ptrclass._type_, '__del__' : _ownedPointerDeleter })
    _ownedPointerTypeCache[cls] = newptrclass
    return newptrclass
# ----------------------------------------------------------------------------

# this function is called by CTypes to process the return value of a function
# and raise an exception if needed
def ctypesFunctionErrorCheck(nErr, func=None, arguments=None):
    # func and arguments are necessary for ctypes but unneeded here
    if nErr != 0:
        cErrorText = cLib.ionic_get_error_str(nErr)
        errorText = CMarshalUtil.stringFromC(cErrorText)
        raise IonicException(errorText, nErr)
    
# this function is called by Ionic code which handles communication with Ionic
# servers.  it is useful for correctly throwing IonicServerException in the case
# of a server error being received by the client.
def raiseExceptionWithServerResponse(cServerResponse, ex):
    if cServerResponse and isinstance(ex, IonicException):
        if ex.code == 40011:
            ex = IonicServerException._marshalFromC(ex.message, ex.code, cServerResponse.contents)
    raise ex


cLib.ionic_attributesmap_create.argtypes = []
cLib.ionic_attributesmap_create.restype = POINTER(CAttributesMap)

cLib.ionic_attributesmap_clone.argtypes = [OWNED_POINTER(CAttributesMap)]
cLib.ionic_attributesmap_clone.restype = OWNED_POINTER(CAttributesMap)

cLib.ionic_attributesmap_set.argtypes = [OWNED_POINTER(CAttributesMap), c_char_p, c_char_p]
cLib.ionic_attributesmap_set.restype = c_int
cLib.ionic_attributesmap_set.errcheck = ctypesFunctionErrorCheck

cLib.ionic_attributesmap_rmv_value.argtypes = [OWNED_POINTER(CAttributesMap), c_char_p, c_char_p]
cLib.ionic_attributesmap_rmv_value.restype = c_int
cLib.ionic_attributesmap_rmv_value.errcheck = ctypesFunctionErrorCheck

cLib.ionic_attributesmap_rmv_key.argtypes = [OWNED_POINTER(CAttributesMap), c_char_p]
cLib.ionic_attributesmap_rmv_key.restype = c_int
cLib.ionic_attributesmap_rmv_key.errcheck = ctypesFunctionErrorCheck

cLib.ionic_attributesmap_get_values_array.argtypes = [OWNED_POINTER(CAttributesMap), c_char_p, POINTER(c_size_t)]
cLib.ionic_attributesmap_get_values_array.restype = OWNED_POINTER(POINTER(c_char))

cLib.ionic_attributesmap_get_keys_array.argtypes = [OWNED_POINTER(CAttributesMap), POINTER(c_size_t)]
cLib.ionic_attributesmap_get_keys_array.restype = OWNED_POINTER(POINTER(c_char))


cLib.ionic_obligationsmap_create.argtypes = []
cLib.ionic_obligationsmap_create.restype = POINTER(CObligationsMap)

cLib.ionic_obligationsmap_clone.argtypes = [OWNED_POINTER(CObligationsMap)]
cLib.ionic_obligationsmap_clone.restype = OWNED_POINTER(CObligationsMap)

cLib.ionic_obligationsmap_set.argtypes = [OWNED_POINTER(CObligationsMap), c_char_p, c_char_p]
cLib.ionic_obligationsmap_set.restype = c_int
cLib.ionic_obligationsmap_set.errcheck = ctypesFunctionErrorCheck

cLib.ionic_obligationsmap_rmv_value.argtypes = [OWNED_POINTER(CObligationsMap), c_char_p, c_char_p]
cLib.ionic_obligationsmap_rmv_value.restype = c_int
cLib.ionic_obligationsmap_rmv_value.errcheck = ctypesFunctionErrorCheck

cLib.ionic_obligationsmap_rmv_key.argtypes = [OWNED_POINTER(CObligationsMap), c_char_p]
cLib.ionic_obligationsmap_rmv_key.restype = c_int
cLib.ionic_obligationsmap_rmv_key.errcheck = ctypesFunctionErrorCheck

cLib.ionic_obligationsmap_get_values_array.argtypes = [OWNED_POINTER(CObligationsMap), c_char_p, POINTER(c_size_t)]
cLib.ionic_obligationsmap_get_values_array.restype = OWNED_POINTER(POINTER(c_char))

cLib.ionic_obligationsmap_get_keys_array.argtypes = [OWNED_POINTER(CObligationsMap), POINTER(c_size_t)]
cLib.ionic_obligationsmap_get_keys_array.restype = OWNED_POINTER(POINTER(c_char))


cLib.ionic_metadatamap_create.argtypes = []
cLib.ionic_metadatamap_create.restype = OWNED_POINTER(CMetadataMap)

cLib.ionic_metadatamap_clone.argtypes = [OWNED_POINTER(CMetadataMap)]
cLib.ionic_metadatamap_clone.restype = OWNED_POINTER(CMetadataMap)

cLib.ionic_metadatamap_set.argtypes = [OWNED_POINTER(CMetadataMap), c_char_p, c_char_p]
cLib.ionic_metadatamap_set.restype = c_int
cLib.ionic_metadatamap_set.errcheck = ctypesFunctionErrorCheck

cLib.ionic_metadatamap_rmv.argtypes = [OWNED_POINTER(CMetadataMap), c_char_p]
cLib.ionic_metadatamap_rmv.restype = c_int
cLib.ionic_metadatamap_rmv.errcheck = ctypesFunctionErrorCheck

cLib.ionic_metadatamap_get.argtypes = [OWNED_POINTER(CMetadataMap), c_char_p]
cLib.ionic_metadatamap_get.restype = OWNED_POINTER(c_char)

cLib.ionic_metadatamap_get_keys_array.argtypes = [OWNED_POINTER(CMetadataMap), POINTER(c_size_t)]
cLib.ionic_metadatamap_get_keys_array.restype = OWNED_POINTER(POINTER(c_char))


cLib.ionic_profile_persistor_create_default.argtypes = []
cLib.ionic_profile_persistor_create_default.restype = OWNED_POINTER(CProfilePersistor)

cLib.ionic_profile_persistor_create_pw_file.argtypes = [c_char_p, c_char_p]
cLib.ionic_profile_persistor_create_pw_file.restype = OWNED_POINTER(CProfilePersistor)

cLib.ionic_profile_persistor_create_aesgcm_file.argtypes = [c_char_p, POINTER(CBytes), POINTER(CBytes)]
cLib.ionic_profile_persistor_create_aesgcm_file.restype = OWNED_POINTER(CProfilePersistor)

cLib.ionic_profile_persistor_create_plaintext_file.argtypes = [c_char_p]
cLib.ionic_profile_persistor_create_plaintext_file.restype = OWNED_POINTER(CProfilePersistor)

if os.name == 'posix':
    if sys.platform == 'mac' or sys.platform == 'darwin':
        cLib.ionic_profile_persistor_create_mac.argtypes = [c_char_p, c_char_p]
        cLib.ionic_profile_persistor_create_mac.restype = OWNED_POINTER(CProfilePersistor)
    else:
        cLib.ionic_profile_persistor_create_linux.argtypes = [c_char_p]
        cLib.ionic_profile_persistor_create_linux.restype = OWNED_POINTER(CProfilePersistor)
else:
    cLib.ionic_profile_persistor_create_windows.argtypes = [c_char_p]
    cLib.ionic_profile_persistor_create_windows.restype = OWNED_POINTER(CProfilePersistor)

cLib.ionic_profile_persistor_get_version.argtypes = [POINTER(CProfilePersistor)]
cLib.ionic_profile_persistor_get_version.restype = OWNED_POINTER(c_char)

cLib.ionic_profile_persistor_set_version.argtypes = [POINTER(CProfilePersistor), c_char_p]
cLib.ionic_profile_persistor_set_version.restype = c_int
cLib.ionic_profile_persistor_set_version.errcheck = ctypesFunctionErrorCheck 

IONIC_PROFILE_PERSISTOR_VERSION_1_0 = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_PROFILE_PERSISTOR_VERSION_1_0').value)
IONIC_PROFILE_PERSISTOR_VERSION_1_1 = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_PROFILE_PERSISTOR_VERSION_1_1').value)

cLib.ionic_release.argtypes = [c_void_p]
cLib.ionic_release.restype = c_int

cLib.ionic_get_error_str.argtypes = [c_int]
cLib.ionic_get_error_str.restype = OWNED_POINTER(c_char)

IONIC_SDK_VERSION = CMarshalUtil.stringFromC((c_char_p).in_dll(cLib, 'IONIC_SDK_C_VERSION').value)
