from ionicsdk._common import *
from sys import maxsize

class CCoverPageService(Structure):
    pass


from sys import maxsize

ServicesCallback_has_active_profile = CFUNCTYPE(c_bool, c_void_p)

if maxsize > 2**32: # The return type should be c_void_p but a bug in ctypes corrupts the pointer
    CoverPageCallback_GetPage = CFUNCTYPE(c_uint64, POINTER(CCoverPageService), c_int)
    CoverPageCallback_Release = CFUNCTYPE(None, POINTER(CBytes))
else:
    CoverPageCallback_GetPage = CFUNCTYPE(c_ulong, POINTER(CCoverPageService), c_int)
    CoverPageCallback_Release = CFUNCTYPE(None, POINTER(CBytes))

cLib.ionic_cover_page_service_create.argtypes = []
cLib.ionic_cover_page_service_create.restype = OWNED_POINTER(CCoverPageService)

cLib.ionic_cover_page_service_create_custom.argtypes = [CoverPageCallback_GetPage, CoverPageCallback_GetPage, CoverPageCallback_Release]
cLib.ionic_cover_page_service_create_custom.restype = OWNED_POINTER(CCoverPageService)

cLib.ionic_coverpage_service_get_cover_page.argtypes = [OWNED_POINTER(CCoverPageService), c_int]
cLib.ionic_coverpage_service_get_cover_page.restype = OWNED_POINTER(CBytes)

cLib.ionic_coverpage_service_get_access_denied_page.argtypes = [OWNED_POINTER(CCoverPageService), c_int]
cLib.ionic_coverpage_service_get_access_denied_page.restype = OWNED_POINTER(CBytes)
