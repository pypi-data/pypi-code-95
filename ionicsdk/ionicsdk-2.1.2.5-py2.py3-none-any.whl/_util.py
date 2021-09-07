import os, sys, types
import weakref
from ctypes import *

class CBytes(Structure):
    __slots__ = [
            'pbyData',
            'nSize',
            ]
    _fields_ = [
            ('pbyData', POINTER(c_ubyte)),
            ('nSize', c_size_t),
                ]
    def __init__(self, cbytedata, size):
        self.nSize = size
        self.pbyData = cbytedata

class CMarshalUtil(object):
    @staticmethod
    def bytesFromC(cBytes):
        """Convert C bytes structure (CBytes) into python bytes object."""
        if cBytes is None:
            return None
        elif isinstance(cBytes, POINTER(CBytes)):
            if cBytes:
                return string_at(cBytes[0].pbyData, cBytes[0].nSize)
            else:
                return None
        else:
            return string_at(cBytes.pbyData, cBytes.nSize)
        
    @staticmethod
    def bytesToC(pyBytes):
        """Convert Python bytes or bytearray object into C bytes structure (CBytes).
        The returned CBytes structure will be garbage collected by Python and does
        NOT need to be released manually in any way."""
        if pyBytes is None:
            return None
        nSize = len(pyBytes)
        return CBytes((c_ubyte * nSize).from_buffer_copy(pyBytes), nSize)
    
    @staticmethod
    def stringFromC(cString):
        """Convert C string (c_char_p or LP_c_char) into python unicode string."""
        if cString is None:
            return None
        elif isinstance(cString, POINTER(c_char)):
            if cString:
                try:
                    return string_at(cString).decode('utf-8')
                except UnicodeDecodeError as e:
                    return string_at(cString).decode('latin-1')
            else:
                return None
        else:
            try:
                return cString.decode('utf-8')
            except UnicodeDecodeError as e:
                return cString.decode('latin-1')
        
    @staticmethod
    def stringToC(pyString):
        """Convert Python unicode string object into C string (c_char_p).
        The returned C string will be garbage collected by Python and does
        NOT need to be released manually in any way."""
        if pyString is None:
            return None
        return c_char_p(pyString.encode('utf-8'))
    
    @staticmethod
    def stringArrayFromC(cStringArray, nCount):
        """Convert c string  array (array of c_char_p) into Python list of 
            Unicode strings."""
        if cStringArray is None:
            return []
        pyStringList = []
        for i in range(nCount):
            cString = cStringArray[i]
            if cString != None:
                if isinstance(cString, POINTER(c_char)):
                    if cString:
                        try:
                            pyStringList.append( string_at(cString).decode('utf-8') )
                        except UnicodeDecodeError as e:
                            pyStringList.append( string_at(cString).decode('latin-1') )
                else:
                    try:
                        pyStringList.append( cString.decode('utf-8') )
                    except UnicodeDecodeError as e:
                        pyStringList.append( cString.decode('latin-1') )

        return pyStringList

    @staticmethod
    def stringArrayToC(pyStringArray):
        """Convert Python unicode string array/list into C string array (array
        of c_char_p). The returned C string array will be garbage collected by
        Python and does NOT need to be released manually in any way."""
        if pyStringArray is None:
            return None
        nCount = len(pyStringArray)
        cStringArray = (c_char_p * nCount)()
        for i in range(0, nCount):
            cStringArray[i] = c_char_p(pyStringArray[i].encode('utf-8'))
        return cStringArray

