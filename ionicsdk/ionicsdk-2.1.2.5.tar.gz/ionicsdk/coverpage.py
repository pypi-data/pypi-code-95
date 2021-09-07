"""!Common functions allowing for Ionic-styled cover pages, which can provide explanation and enablement instructions
    for access to an Ionic-protected document.
"""

import ionicsdk._private as _private
from ionicsdk.common import *
from ionicsdk.exceptions import *
from ionicsdk.errors import *
from collections import defaultdict

class CoverPageService(object):
    """!Service object that provides cover pages to a File Cipher
        @details
        A user should sub class this object and override the GetCoverPage and
        GetAccessDeniedPage methods.  Create an instance of their subclass and
        finally pass this instance into their cipher constructor.  The cipher
        does not need a default instance passed to it.  If no coverpage service 
        is passed to the cipher, it will create a default service itself.
        
        The overridden methods are called as needed and passed the file type.  The
        method can return raw bytearray data for file types it recognizes and should
        return None otherwise.  If None is returned, or the method is not overridden, 
        then the coverpage service will fill in a default Ionic coverpage.
        """
    
    ##Enumeration constants for Filetype
    FILETYPE_UNKNOWN = 0,
    ##Enumeration constants for Filetype
    FILETYPE_DOCX = 1
    ##Enumeration constants for Filetype
    FILETYPE_PPTX = 2
    ##Enumeration constants for Filetype
    FILETYPE_XLSX = 3
    ##Enumeration constants for Filetype
    FILETYPE_DOCM = 4
    ##Enumeration constants for Filetype
    FILETYPE_PPTM = 5
    ##Enumeration constants for Filetype
    FILETYPE_XLSM = 6
    ##Enumeration constants for Filetype
    FILETYPE_PDF = 7
    ##Enumeration constants for Filetype
    FILETYPE_CSV = 8

    def __init__(self):
        """!Constructs a coverpage service with default values.
            NOTE: This class is designed to be subclassed for custom implementations.
            Do not use the base class alone.
        """
        self._pageRefs = {}

        def cb_get_cover_page(cCoverPageService, filetype):
            pagedata = self.GetCoverPage(filetype)
            if pagedata is None:
                return None

            pcpagedata = _private.pointer(_private.CMarshalUtil.bytesToC(pagedata))
       
            # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
            ref = _private.cast(pcpagedata,_private.c_void_p)
            self._pageRefs[ref.value] = [pagedata, pcpagedata, ref]
            
            return ref.value

        def cb_get_access_denied_page(cCoverPageService, filetype):
            pagedata = self.GetAccessDeniedPage(filetype)
            if pagedata is None:
                return None
            
            pcpagedata = _private.pointer(_private.CMarshalUtil.bytesToC(pagedata))

            # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
            ref = _private.cast(pcpagedata,_private.c_void_p)
            self._pageRefs[ref.value] = [pagedata, pcpagedata, ref]
                
            return ref.value

        def cb_release(pcpagedata):
            ref = _private.cast(pcpagedata,_private.c_void_p)
            del self._pageRefs[ref.value]
        
        self._getCoverPageCallback = _private.CoverPageCallback_GetPage(cb_get_cover_page)
        self._getAccessDeniedPageCallback = _private.CoverPageCallback_GetPage(cb_get_access_denied_page)
        self._releaseCallback = _private.CoverPageCallback_Release(cb_release)
        
        self._cCoverPageService = _private.cLib.ionic_cover_page_service_create_custom(self._getCoverPageCallback, self._getAccessDeniedPageCallback, self._releaseCallback)

    def GetCoverPage(self, filetype):
        """!Designed to be overridden.  Called by a Cipher when it needs to create a new file
        and needs cover page data for the newly encrypted file.
        
        @param
            filetype (int): The file type, compare to FILETYPE_DOCX, etc.. defined in this module.
        @return
            The page data, or None if that page is not implemented in this class
        """
        return None

    def GetAccessDeniedPage(self, filetype):
        """!Designed to be overridden.  Called by a Cipher when it attempts to decrypt a file
        and needs an access denied cover page data for the newly failed accessed file.
        
        @param
            filetype (int): The file type, compare to FILETYPE_DOCX, etc.. defined in this module.
        @return
            The page data, or None if that page is not implemented in this class
        """
        return None

