"""!Supports protection of files of all types.
"""

import ionicsdk._private as _private
from ionicsdk.exceptions import *
from ionicsdk.agent import *
from ionicsdk.services import _ServicesInternal

class FileCipherFamily(object):
    """!Enumeration of all supported cipher families.

    - UNKNOWN - Represents an unknown / invalid cipher family.
    - GENERIC - Represents the Generic cipher family implemented by FileCipherGeneric.
    - OPENXML - Represents the OpenXML cipher family implemented by FileCipherOpenXml.
    - AUTO    - Represents the automatic cipher family implemented by FileCipherAuto.
    - PDF     - Represents the PDF cipher family implemented by FileCipherPdf.
    - CSV     - Represents the CSV cipher family implemented by FileCipherCsv.
    - CMS     - Represents the CMS cipher family implemented by FileCipherCms.
    """
    ##FileType enumeration - Represents an unknown / invalid cipher family.
    UNKNOWN = 0
    ##FileType enumeration - Represents the Generic cipher family implemented by FileCipherGeneric.
    GENERIC = 1
    ##FileType enumeration - Represents the OpenXML cipher family implemented by FileCipherOpenXml.
    OPENXML = 2
    ##FileType enumeration - Represents the automatic cipher family implemented by FileCipherAuto.
    AUTO    = 3
    ##FileType enumeration - Represents the PDF cipher family implemented by FileCipherPdf.
    PDF     = 4
    ##FileType enumeration - Represents the CSV cipher family implemented by FileCipherCsv.
    CSV     = 5
    ##FileType enumeration - Represents the CMS cipher family implemented by FileCipherCms.
    CMS     = 6
    
    @classmethod
    def tostring(cls, familyenum):
        """!Gets a string representation of a FileCipherFamily enum value.
        @param
            familyenum (int): File type enumeration
            
        @return
            A text string containing a short label for the enum
        """
        stringlookup = {
            cls.UNKNOWN: "unknown",
            cls.GENERIC: "generic",
            cls.AUTO: "auto",
            cls.PDF: "pdf",
            cls.CSV: "csv",
            cls.CMS: "cms",
        }
        return stringlookup.get(familyenum, "unknown")
        
class FileInfo(object):
    """!Data class used to describe attributes of a file.
    """
    def __init__(self, isencrypted=False, keyid=None, cipherfamily=FileCipherFamily.UNKNOWN,
                 cipherversion=None, server=None):
        """!Constructs decrypt attributes from passed in arguments.
            
        @param
            isencrypted (boolean) Whether the file is encrypted
        @param
            keyid (string) Key ID
        @param
            cipherfamily (FileCipherFamily) Cipher family enumeration
        @param
            cipherversion (string) Cipher family version
        @param
            server (string) Ionic server that the key ID was issued from
        """

        ##(boolean) Whether the file is encrypted
        self.isencrypted = isencrypted
        ##(string) Key ID used to encrypt the file
        self.keyid = keyid
        ##(FileCipherFamily) Cipher family enumeration
        self.cipherfamily = cipherfamily
        ##(string) Cipher family version
        self.cipherversion = cipherversion
        ##(string) Ionic server that the key ID was issued from
        self.server = server
        
    @staticmethod
    def _marshalFromC(cFileInfo):
        info = FileInfo()
        info.isencrypted = bool(cFileInfo.bIsEncrypted)
        info.keyid = _private.CMarshalUtil.stringFromC(cFileInfo.pszKeyId)
        info.cipherfamily = int(cFileInfo.eFamily)
        info.cipherversion = _private.CMarshalUtil.stringFromC(cFileInfo.pszCipherVersion)
        info.server = _private.CMarshalUtil.stringFromC(cFileInfo.pszServer)
        return info

class FileCipherEncryptAttributes(object):
    """!Allows for extended input and output options during encryption.
    """
    def __init__(self, attributes=None, metadata=None, version=None, mutableAttributes=None, enablePortionMarking=False):
        """!Constructs encrypt attributes from passed in arguments.
            
        @param
            attributes (KeyAttributesDict) The key attributes to associate with the key used to encrypt the file
        @param
            metadata (MetadataDict) The metadata properties to send along with the HTTP request
        @param
            version (string) The file format version to encrypt with - It can be left empty to use the latest version (recommended).
        @param
            mutableAttributes (KeyAttributesDict) The key mutable attributes to associate with data chunk protection key
        @param
            enablePortionMarking (boolean) Determines if portion marking is enabled.
        """

        ##(string) The key ID (also known as the key tag)
        self.keyidOut = None
        ##(KeyData) The key bytes
        self.keydataOut = None
        ##(FileCipherFamily) The file cipher family the file was encrypted with
        self.familyOut = None
        ##(string) The file format version to encrypt with - It can be left empty to use the latest version (recommended).
        self.version = version
        ##(\link ionicsdk.common.KeyAttributesDict KeyAttributesDict \endlink) The key attributes to associate with the key used to encrypt the file
        self.attributes = attributes
        ##(\link ionicsdk.common.KeyAttributesDict KeyAttributesDict \endlink) The key mutable attributes to associate with data chunk protection key
        self.mutableAttributes = mutableAttributes
        ##(\link ionicsdk.common.MetadataDict MetadataDict \endlink) The metadata properties to send along with the HTTP request
        self.metadata = metadata
        ##(boolean) Determines if portion marking is enabled.
        self.enablePortionMarking = enablePortionMarking

    def _updateFromC(self, cFileEncryptAttributes):
        """
        We just need to update the outgoing members of this instance from the 'C' object.
        """
        self.keydataOut = KeyData._marshalFromC(cFileEncryptAttributes.contents.pKeyResponseOut.contents)
        self.keyidOut = self.keydataOut.id
        self.familyOut = int(cFileEncryptAttributes.contents.eFamilyOut)
        self.version = _private.CMarshalUtil.stringFromC(cFileEncryptAttributes.contents.pszVersionOut)
    
        # For now, we are only using the pServerResponseOut data in case we raise an exception on error.

    @staticmethod
    def _marshalToC(pyFileEncryptAttributes):
        """
        We only need to copy over the input parms in this case.
        """
        if pyFileEncryptAttributes is None:
            return None

        cAttributes = KeyAttributesDict._marshalToC(pyFileEncryptAttributes.attributes)
        cMutableAttributes = KeyAttributesDict._marshalToC(pyFileEncryptAttributes.mutableAttributes)
        cMetadata = MetadataDict._marshalToC(pyFileEncryptAttributes.metadata)
        cVersion = _private.CMarshalUtil.stringToC(pyFileEncryptAttributes.version)
        
        return _private.cLib.ionic_filecipher_encrypt_attributes_create2(cAttributes, cMutableAttributes, cMetadata, cVersion, pyFileEncryptAttributes.enablePortionMarking)


class FileCipherDecryptAttributes(object):
    """!Allows for extended input and output options during decryption.
    """
    def __init__(self, metadata=None, enableaccessdeniedpage=False):
        """!Constructor for decrypt attributes, can pass in metadata, and then assign any other member variables.
            
        @param
            metadata (MetadataDict) The metadata properties to send along with the HTTP request
        @param
            enableaccessdeniedpage (boolean) Indicate whether access denied page object should be populated in
                    the event that an access denied error is encountered.
        """

        ##(string) The key ID (also known as the key tag)
        self.keyidOut = None
        ##(bytes) The key bytes
        self.keydataOut = None
        ##(FileCipherFamily) The file cipher family the file was decrypted with
        self.familyOut = None
        ##(string) The file cipher version the file was decrypted with
        self.versionOut = None
        ##(\link ionicsdk.common.KeyAttributesDict KeyAttributesDict \endlink): The key attributes associated with the key used to decrypt the file
        self.attributesOut = None
        ##(\link ionicsdk.common.KeyAttributesDict KeyAttributesDict \endlink) The key mutable attributes to associate with data chunk protection key
        self.mutableAttributesOut = None
        ##(bytes) The access denied page
        self.accessdeniedpageOut = None
        ##(boolean) Indicate whether access denied page object should be populated in the event
        ##      that an access denied error is encountered.
        self.enableaccessdeniedpage = enableaccessdeniedpage
        ##(\link ionicsdk.common.MetadataDict MetadataDict \endlink) The metadata properties to send along with the HTTP request
        self.metadata = metadata
            
    def _updateFromC(self, cFileDecryptAttributes):
        """
        We just need to update the outgoing members of this instance from the 'C' object.
        """
        if cFileDecryptAttributes.contents.pKeyResponseOut:
            self.keydataOut = KeyData._marshalFromC(cFileDecryptAttributes.contents.pKeyResponseOut.contents)
            self.keyidOut = self.keydataOut.id
            self.attributesOut = self.keydataOut.attributes
            self.mutableAttributesOut = self.keydataOut.mutableAttributes
        self.familyOut = int(cFileDecryptAttributes.contents.eFamilyOut)
        self.versionOut = _private.CMarshalUtil.stringFromC(cFileDecryptAttributes.contents.pszVersionOut)
        self.accessdeniedpageOut = _private.CMarshalUtil.bytesFromC(cFileDecryptAttributes.contents.pAccessDeniedPageOut)
    
        # For now, we are only using the pServerResponseOut data in case we raise an exception on error.
    
    @staticmethod
    def _marshalToC(pyFileDecryptAttributes):
        """
        We only need to copy over the input parms in this case.
        """
        if pyFileDecryptAttributes is None:
            return None

        cMetadata = MetadataDict._marshalToC(pyFileDecryptAttributes.metadata)
        
        return _private.cLib.ionic_filecipher_decrypt_attributes_create(cMetadata, pyFileDecryptAttributes.enableaccessdeniedpage)


class FileCrypto(object):
    """!
        Utility functions to retrieve FileInfo for any type of file or data.
    """
    @staticmethod
    def getinfobytes(inputbytes):
        """!Determines if a file is Ionic protected and various pieces of information about the file.

        @param
            inputbytes (bytes): The data input.

        @return
            The FileInfo output object.
        """
        cFileInfo = _private.OWNED_POINTER(_private.CFileInfo)()
        _private.cLib.ionic_filecipher_getinfo_bytes(_private.CMarshalUtil.bytesToC(inputbytes),
                                                     _private.byref(cFileInfo))
        return FileInfo._marshalFromC(cFileInfo.contents)
    
    @staticmethod
    def getinfo(filepath):
        """!Determines if a file is Ionic protected and various pieces of information about the file.

        @param
            filepath (string): The input file path.

        @return
            The FileInfo output object.
        """
        cFileInfo = _private.OWNED_POINTER(_private.CFileInfo)()
        _private.cLib.ionic_filecipher_getinfo(_private.CMarshalUtil.stringToC(filepath),
                                               _private.byref(cFileInfo))
        return FileInfo._marshalFromC(cFileInfo.contents)
    
class FileCipherBase(object):
    """!Base class for all file encryption / decryption ciphers.
    
    Not to be used directly.  Use one of the appropriate subclasses:
    - FileCipherAuto - Cipher that automatically chooses the correct
                         cipher to use for file encryption / decryption.
                         See FileCipherAuto for limitations on choosing
                         the correct cipher during encryption.
    - FileCipherCms - Cipher that supports CMS (Cryptographic Message
                        Syntax) encryption / decryption.
    - FileCipherCsv - Cipher that supports CSV (Comma Separated
                        Values) file encryption / decryption.
    - FileCipherGeneric - Cipher that supports generic file encryption
                            / decryption.
    - FileCipherOpenXml - Cipher that supports OpenXML file encryption
                            / decryption.
    - FileCipherPdf - Cipher that supports PDF file encryption /
                        decryption.
    """
    def __new__(cls, *args, **kwargs): # The base class should not be used directly
        if cls is FileCipherBase:
            raise NotImplementedError()
        return super(FileCipherBase, cls).__new__(cls)
    
    def __init__(self):
        """!Constructs a file cipher with default values
        """
        self._cCipher = None
        self._cServerResponse = None
    
    @property
    def family(self):
        """!Access the instance FileCipherFamily enumeration
            
        @return
            (FileCipherFamily) File Cipher Family enumeration
        """
        return self.__class__.FAMILY
        
    @property
    def familystring(self):
        """!Access the instance FileCipherFamily string
            
        @return
            (string) File Cipher Family string
        """
        return self.__class__.FAMILY_STRING
    
    def getLastServerResponse(self):
        """!Return the Server Response object from the last Agent call.
            @return
            A valid ServerResponse object or None if no server calls have been made yet.
            """
        return ServerResponse._marshalFromC(self._cServerResponse)

    def encryptbytes(self, plaintextbytes, attributes = None, metadata = None, mutableAttributes = None):
        """!Encrypts an input byte buffer into an output byte buffer.

        This function performs file encryption using the method implied
        by the class name (e.g. FileCipherOpenXml).

        @param
            plaintextbytes (bytes): The binary plaintext input buffer.
        @param
            attributes (keyAttributesDict, optional): The
                        attributes to use when creating a key to protect data.
        @param
            metadata (metadataDict, optional): The metadata
                        properties to send along with the HTTP request.
        @param
            mutableAttributes (keyAttributesDict): The key mutable attributes
                        to associate with data chunk protection key.

        @return
            The ciphertext output buffer.
        """
        # inputs
        cPlainTextBytes = _private.CMarshalUtil.bytesToC(plaintextbytes)
        cAttributes = KeyAttributesDict._marshalToC(attributes)
        cMutableAttributes = KeyAttributesDict._marshalToC(mutableAttributes)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cCipherTextBytes = _private.OWNED_POINTER(_private.CBytes)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_encrypt_bytes4(
                self._cCipher,
                cPlainTextBytes,
                cAttributes,
                cMutableAttributes,
                cMetadata,
                _private.byref(cCipherTextBytes),
                None, # key id out
                None, # family out
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
        
        # marshal C outputs to Python
        return _private.CMarshalUtil.bytesFromC(cCipherTextBytes.contents)

    def encryptbytes2(self, plaintextbytes, encryptattributesInOut):
        """!Encrypts an input byte buffer into an output byte buffer.

        This function performs file encryption using the method implied
        by the class name (e.g. FileCipherOpenXml).

        @param
            plaintextbytes (bytes): The binary plaintext input buffer.
        @param
            encryptattributesInOut (FileCipherEncryptAttributes): Object
                             to provide and return detailed information.
        @return
            The ciphertext output buffer.  The encryptattributesInOut
            paramater will also be modified.
        """
        
        cCipherTextBytes = _private.OWNED_POINTER(_private.CBytes)()
        cFileEncryptAttrs = FileCipherEncryptAttributes._marshalToC(encryptattributesInOut)
        # inputs
        cPlainTextBytes = _private.CMarshalUtil.bytesToC(plaintextbytes)

        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_encrypt_bytesA(
                self._cCipher,
                cPlainTextBytes,
                _private.byref(cCipherTextBytes),
                cFileEncryptAttrs)
        except Exception as e:
            _private.raiseExceptionWithServerResponse(cFileEncryptAttrs.contents.pServerResponseOut, e)

        # marshal C outputs to Python
        encryptattributesInOut._updateFromC(cFileEncryptAttrs)

        return _private.CMarshalUtil.bytesFromC(cCipherTextBytes)
    
    def decryptbytes(self, ciphertextbytes, metadata = None):
        """!Decrypts an input buffer into an output buffer.

        This function performs file decryption using the method implied
        by the class name (e.g. FileCipherOpenXml).

        @param
            ciphertextbytes (bytes): The binary ciphertext input buffer.
        @param
            metadata (metadataDict, optional): The metadata
                         properties to send along with the HTTP request.

        @return
            The plaintext output buffer.
        """
        # inputs
        cCipherTextBytes = _private.CMarshalUtil.bytesToC(ciphertextbytes)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cPlainTextBytes = _private.OWNED_POINTER(_private.CBytes)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_decrypt_bytes2(
                self._cCipher,
                cCipherTextBytes,
                cMetadata,
                _private.byref(cPlainTextBytes),
                None, # attributes out
                None, # key id out
                None, # family out
                None, # version out
                None, # access denied page out
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
        
        # marshal C outputs to Python
        return _private.CMarshalUtil.bytesFromC(cPlainTextBytes.contents)
            
    def decryptbytes2(self, ciphertextbytes, decryptattributesInOut):
        """!Decrypts an input byte buffer into an output byte buffer.

        This function performs file encryption using the method implied
        by the class name (e.g. FileCipherOpenXml).

        @param
            ciphertextbytes (bytes): The binary ciphertext input buffer.
        @param
            decryptattributesInOut (FileCipherDecryptAttributes): Object
                             to provide and return detailed information.
        
        @return
            The plaintext output buffer.  The decryptattributesInOut
            paramater will also be modified.
        """
        # inputs
        cCipherTextBytes = _private.CMarshalUtil.bytesToC(ciphertextbytes)
        cFileDecryptAttrs = FileCipherDecryptAttributes._marshalToC(decryptattributesInOut)
        
        # outputs
        cPlainTextBytes = _private.OWNED_POINTER(_private.CBytes)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_decrypt_bytesA(
                self._cCipher,
                cCipherTextBytes,
                _private.byref(cPlainTextBytes),
                cFileDecryptAttrs)
        except Exception as e:
            # Must update the attribute object in case there is Access Denied Page data
            decryptattributesInOut._updateFromC(cFileDecryptAttrs)
            _private.raiseExceptionWithServerResponse(cFileDecryptAttrs.contents.pServerResponseOut, e)
        
        # marshal C outputs to Python
        decryptattributesInOut._updateFromC(cFileDecryptAttrs)

        return _private.CMarshalUtil.bytesFromC(cPlainTextBytes.contents)

    def encryptinplace(self, filepath, attributes = None, metadata = None, mutableAttributes = None):
        """!Encrypts a file in-place.

        This function performs in-place file encryption, which means
        that the file specified by the filepath parameter will be
        overwritten with the resulting encrypted ciphertext.  If
        decryption fails, it is guaranteed that the original ciphertext
        file will not be modified in any way.
        
        You must have write access to the file specified by the filepath
        parameter.  If you do not have write access, the most likely
        error code that you will receive is FILECRYPTO_RENAMEFILE.

        @param
            filepath (string): The file to be encrypted in place.
        @param
            attributes (keyAttributesDict, optional): The
                        attributes to use when creating a key to protect data.
        @param
            metadata (metadataDict, optional): The metadata
                        properties to send along with the HTTP request.
        @param
            mutableAttributes (keyAttributesDict): The key mutable attributes
                        to associate with data chunk protection key.

        @return
            None
        """
        # inputs
        cFilePath = _private.CMarshalUtil.stringToC(filepath)
        cAttributes = KeyAttributesDict._marshalToC(attributes)
        cMutableAttributes = KeyAttributesDict._marshalToC(mutableAttributes)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_encrypt_inplace4(
                self._cCipher,
                cFilePath,
                cAttributes,
                cMutableAttributes,
                cMetadata,
                None, # key id out
                None, # family out
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

    def encryptinplace2(self, filepath, encryptattributesInOut):
        """!Encrypts a file in-place.
        
        This function performs in-place file encryption, which means
        that the file specified by the filepath parameter will be
        overwritten with the resulting encrypted ciphertext.  If
        decryption fails, it is guaranteed that the original ciphertext
        file will not be modified in any way.
        
        You must have write access to the file specified by the filepath
        parameter.  If you do not have write access, the most likely
        error code that you will receive is FILECRYPTO_RENAMEFILE.
        
        @param
            filepath (string): The file to be encrypted in place.
        @param
            encryptattributesInOut (FileCipherEncryptAttributes): Object
                to provide and return detailed information.
        
        @return
            None
        """
        # inputs
        cFilePath = _private.CMarshalUtil.stringToC(filepath)
        cFileEncryptAttrs = FileCipherEncryptAttributes._marshalToC(encryptattributesInOut)
            
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_encrypt_inplaceA(self._cCipher,
                                                            cFilePath,
                                                            cFileEncryptAttrs)
        except Exception as e:
            _private.raiseExceptionWithServerResponse(cFileEncryptAttrs.contents.pServerResponseOut, e)
    
        # marshal C outputs to Python
        encryptattributesInOut._updateFromC(cFileEncryptAttrs)

    def decryptinplace(self, filepath, metadata = None):
        """!Decrypts a file in-place.

        This function performs in-place file decryption, which means
        that the file specified by the filepath parameter will be
        overwritten with the resulting decrypted plaintext.  If 
        decryption fails, it is guaranteed that the original ciphertext
        file will not be modified in any way.
        
        You must have write access to the file specified by the
        filepath parameter.  If you do not have write access, the most
        likely error code that you will receive is
        FILECRYPTO_RENAMEFILE.

        @param
            filepath (string): The file to be decrypted in place.
        @param
            metadata (metadataDict, optional): The metadata
                         properties to send along with the HTTP request.

        @return
            None
        """
        # inputs
        cFilePath = _private.CMarshalUtil.stringToC(filepath)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_decrypt_inplace2(
                self._cCipher,
                cFilePath,
                cMetadata,
                None, # key attributes out
                None, # key id out
                None, # family out
                None, # vesion out
                None, # access denied page out
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
    
    def decryptinplace2(self, filepath, decryptattributesInOut):
        """!Decrypts a file in-place.
        
        This function performs in-place file decryption, which means
        that the file specified by the filepath parameter will be
        overwritten with the resulting decrypted plaintext.  If
        decryption fails, it is guaranteed that the original ciphertext
        file will not be modified in any way.
        
        You must have write access to the file specified by the
        filepath parameter.  If you do not have write access, the most
        likely error code that you will receive is
        FILECRYPTO_RENAMEFILE.
        
        @param
            filepath (string): The file to be decrypted in place.
        @param
            decryptattributesInOut (FileCipherDecryptAttributes): Object
                to provide and return detailed information.
        
        @return
            None
        """
        # inputs
        cFilePath = _private.CMarshalUtil.stringToC(filepath)
        cFileDecryptAttrs = FileCipherDecryptAttributes._marshalToC(decryptattributesInOut)
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_decrypt_inplaceA(self._cCipher,
                                                            cFilePath,
                                                            cFileDecryptAttrs)
        except Exception as e:
            # Must update the attribute object in case there is Access Denied Page data
            decryptattributesInOut._updateFromC(cFileDecryptAttrs)
            _private.raiseExceptionWithServerResponse(cFileDecryptAttrs.contents.pServerResponseOut, e)

        # marshal C outputs to Python
        decryptattributesInOut._updateFromC(cFileDecryptAttrs)

    def encrypt(self, sourcepath, destpath, attributes = None, metadata = None, mutableAttributes = None):
        """!Encrypts an input file into an output file.

        This function performs file encryption using the method implied
        by the class name (e.g. FileCipherOpenXml).
        
        If the source and destination paths point to the same physical
        file, then in-place encryption will be performed automatically.
        However, it is recommended to perform in-place encryption using
        the function dedicated for that purpose (encryptinplace).

        @param
            sourcepath (string): The input file path.
        @param
            destpath (string): The output file path.
        @param
            attributes (keyAttributesDict, optional): The
                    attributes to use when creating a key to protect data.
        @param
            metadata (metadataDict, optional): The metadata
                    properties to send along with the HTTP request.
        @param
            mutableAttributes (keyAttributesDict): The key mutable attributes
                    to associate with data chunk protection key.

        @return
            None
        """
        # inputs
        cSourcePath = _private.CMarshalUtil.stringToC(sourcepath)
        cDestPath = _private.CMarshalUtil.stringToC(destpath)
        cAttributes = KeyAttributesDict._marshalToC(attributes)
        cMutableAttributes = KeyAttributesDict._marshalToC(mutableAttributes)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_encrypt4(
                self._cCipher,
                cSourcePath,
                cDestPath,
                cAttributes,
                cMutableAttributes,
                cMetadata,
                None, # key id out
                None, # family out
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
    
    def encrypt2(self, sourcepath, destpath, encryptattributesInOut):
        """!Encrypts an input file into an output file.
        
        This function performs file encryption using the method implied
        by the class name (e.g. FileCipherOpenXml).
        
        If the source and destination paths point to the same physical
        file, then in-place encryption will be performed automatically.
        However, it is recommended to perform in-place encryption using
        the function dedicated for that purpose (encryptinplace).
        
        @param
            sourcepath (string): The input file path.
        @param
            destpath (string): The output file path.
        @param
            encryptattributesInOut (FileCipherEncryptAttributes): Object
                to provide and return detailed information.

        @return
            None
        """
        # inputs
        cSourcePath = _private.CMarshalUtil.stringToC(sourcepath)
        cDestPath = _private.CMarshalUtil.stringToC(destpath)
        cFileEncryptAttrs = FileCipherEncryptAttributes._marshalToC(encryptattributesInOut)
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_encryptA(self._cCipher,
                                                    cSourcePath,
                                                    cDestPath,
                                                    cFileEncryptAttrs)
        except Exception as e:
            _private.raiseExceptionWithServerResponse(cFileEncryptAttrs.contents.pServerResponseOut, e)

        # marshal C outputs to Python
        encryptattributesInOut._updateFromC(cFileEncryptAttrs)
    
    def decrypt(self, sourcepath, destpath, metadata = None):
        """!Decrypts an input file into an output output file.

        This function performs file decryption using the method implied
        by the class name (e.g. FileCipherOpenXml).
        
        If the source and destination paths point to the same physical
        file, then in-place decryption will be performed automatically.
        However, it is recommended to perform in-place decryption using
        the function dedicated for that purpose (decryptinplace)).

        @param
            sourcepath (string): The input file path.
        @param
            destpath (string): The output file path.
        @param
            metadata (metadataDict, optional): The metadata
                         properties to send along with the HTTP request.

        @return
            None
        """
        # inputs
        cSourcePath = _private.CMarshalUtil.stringToC(sourcepath)
        cDestPath = _private.CMarshalUtil.stringToC(destpath)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_decrypt2(
                self._cCipher,
                cSourcePath,
                cDestPath,
                cMetadata,
                None, # key attributes out
                None, # key id out
                None, # family out
                None, # vesion out
                None, # access denied page out
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

    def decrypt2(self, sourcepath, destpath, decryptattributesInOut):
        """!Decrypts an input file into an output output file.
        
        This function performs file decryption using the method implied
        by the class name (e.g. FileCipherOpenXml).
        
        If the source and destination paths point to the same physical
        file, then in-place decryption will be performed automatically.
        However, it is recommended to perform in-place decryption using
        the function dedicated for that purpose (decryptinplace)).
        
        @param
            sourcepath (string): The input file path.
        @param
            destpath (string): The output file path.
        @param
            decryptattributesInOut (FileCipherDecryptAttributes): Object
                to provide and return detailed information.
        
        @return
            None
        """
        # inputs
        cSourcePath = _private.CMarshalUtil.stringToC(sourcepath)
        cDestPath = _private.CMarshalUtil.stringToC(destpath)
        cFileDecryptAttrs = FileCipherDecryptAttributes._marshalToC(decryptattributesInOut)
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_filecipher_decryptA(self._cCipher,
                                                    cSourcePath,
                                                    cDestPath,
                                                    cFileDecryptAttrs)
        except Exception as e:
            # Must update the attribute object in case there is Access Denied Page data
            decryptattributesInOut._updateFromC(cFileDecryptAttrs)
            _private.raiseExceptionWithServerResponse(cFileDecryptAttrs.contents.pServerResponseOut, e)

        # marshal C outputs to Python
        decryptattributesInOut._updateFromC(cFileDecryptAttrs)

    def getinfobytes(self, inputbytes):
        """!Determines if a file is Ionic protected and various pieces of information about the file.
        
        @param
        inputbytes (bytes): The data input.
        
        @return
        The FileInfo output object.
        """
        cFileInfo = _private.OWNED_POINTER(_private.CFileInfo)()
        _private.cLib.ionic_filecipher_getinfo_cipher_bytes(self._cCipher,
                                                            _private.CMarshalUtil.bytesToC(inputbytes),
                                                            _private.byref(cFileInfo))
        return FileInfo._marshalFromC(cFileInfo.contents)

    def getinfo(self, filepath):
        """!Determines if a file is Ionic protected and various pieces of information about the file.
        
        @param
        filepath (string): The input file path.
        
        @return
        The FileInfo output object.
        """
        cFileInfo = _private.OWNED_POINTER(_private.CFileInfo)()
        _private.cLib.ionic_filecipher_getinfo_cipher(self._cCipher,
                                                _private.CMarshalUtil.stringToC(filepath),
                                               _private.byref(cFileInfo))
        return FileInfo._marshalFromC(cFileInfo.contents)


class FileCipherAuto(FileCipherBase):
    """!Cipher that automatically chooses the correct cipher to use for
    file encryption / decryption.

    Important Limitations
    The automatic file cipher cannot and does not detect CSV or CMS file
    types automatically for encryption. Only decryption of these file
    types are supported automatically.

    CSV files do not follow any standard or documented format, can
    contain any type of delimiter, may not contain any delimiters at
    all, etc. For this reason, the automatic file cipher will encrypt
    CSV files using the generic file cipher (FileCipherGeneric) as
    opposed to the specialized CSV file cipher (FileCipherCsv). When the
    CSV file cipher is desired, it must be used directly instead of
    relying on the automatic cipher.

    Similarly, the CMS cipher will encrypt any input as the payload
    (typically a MIME encoded file attachment). Only the resultant
    encrypted CMS message follows a documented format. Therefore, when
    the CMS file cipher is desired for encryption, it must be used
    directly instead of relying on the automatic cipher.
    """

    ##(FileCipherFamily) File Cipher Family enumeration for this class
    FAMILY = FileCipherFamily.AUTO
    ##(string) File Cipher Family label for this class
    FAMILY_STRING = FileCipherFamily.tostring(FAMILY)
    def __init__(self, agentkeyservice, coverpageservice = None):
        """!Constructs an auto file cipher from key services and optional coverpage services.

        @param
            agentkeyservice (class instance) The key service used to retrieve and create keys.
        @param
            coverpageservice (class instance) The coverpage service used to 
                retrieve cover pages and access denied pages.
        """
        super(FileCipherAuto, self).__init__()
        if isinstance(agentkeyservice, Agent):
            if coverpageservice is None:
                self._cCipher = _private.cLib.ionic_filecipher_create_auto(agentkeyservice._cAgent)
            else:
                self._cCipher = _private.cLib.ionic_filecipher_create_auto_coverpage(agentkeyservice._cAgent, coverpageservice._cCoverPageService)
        elif isinstance(agentkeyservice,AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            if coverpageservice is None:
                self._cCipher = _private.cLib.ionic_filecipher_create_auto_services(self._servicesStruct)
            else:
                self._cCipher = _private.cLib.ionic_filecipher_create_auto_services_coverpage(self._servicesStruct, coverpageservice._cCoverPageService)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice

class FileCipherGeneric(FileCipherBase):
    """!Cipher that supports generic file encryption / decryption.
    """
    ##(FileCipherFamily) File Cipher Family enumeration for this class
    FAMILY = FileCipherFamily.GENERIC
    ##(string) File Cipher Family label for this class
    FAMILY_STRING = FileCipherFamily.tostring(FAMILY)
    def __init__(self, agentkeyservice):
        """!Constructs a generic file cipher from key services.

        @param
            agentkeyservice (class instance) The agent or key service used to retrieve and create keys.
        """
        super(FileCipherGeneric, self).__init__()
        if isinstance(agentkeyservice, Agent):
            self._cCipher = _private.cLib.ionic_filecipher_create_generic(agentkeyservice._cAgent)
        elif isinstance(agentkeyservice,AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            self._cCipher = _private.cLib.ionic_filecipher_create_generic_services(self._servicesStruct)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice

class FileCipherOpenXml(FileCipherBase):
    """!Cipher that supports OpenXML file encryption / decryption.
    """
    ##(FileCipherFamily) File Cipher Family enumeration for this class
    FAMILY = FileCipherFamily.OPENXML
    ##(string) File Cipher Family label for this class
    FAMILY_STRING = FileCipherFamily.tostring(FAMILY)
    def __init__(self, agentkeyservice, coverpageservice = None):
        """!Constructs an OpenXml file cipher from key services and optional coverpage services.

        @param
            agentkeyservice (class instance) The agent or key service used to retrieve and create keys.
        @param
            coverpageservice (class instance) The coverpage service used to 
                retrieve cover pages and access denied pages.
        """
        super(FileCipherOpenXml, self).__init__()
        if isinstance(agentkeyservice, Agent):
            if coverpageservice is None:
                self._cCipher = _private.cLib.ionic_filecipher_create_openxml(agentkeyservice._cAgent)
            else:
                self._cCipher = _private.cLib.ionic_filecipher_create_openxml_coverpage(agentkeyservice._cAgent, coverpageservice._cCoverPageService)
        elif isinstance(agentkeyservice,AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            if coverpageservice is None:
                self._cCipher = _private.cLib.ionic_filecipher_create_openxml_services(self._servicesStruct)
            else:
                self._cCipher = _private.cLib.ionic_filecipher_create_openxml_services_coverpage(self._servicesStruct, coverpageservice._cCoverPageService)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice

class FileCipherPdf(FileCipherBase):
    """!Cipher that supports PDF file encryption / decryption.
    """
    ##(FileCipherFamily) File Cipher Family enumeration for this class
    FAMILY = FileCipherFamily.PDF
    ##(string) File Cipher Family label for this class
    FAMILY_STRING = FileCipherFamily.tostring(FAMILY)
    def __init__(self, agentkeyservice, coverpageservice = None):
        """!Constructs a pdf file cipher from key services and optional coverpage services.

        @param
            agentkeyservice (class instance) The agent or key service used to retrieve and create keys.
        @param
            coverpageservice (class instance) The optional coverpage service used to 
                retrieve cover pages and access denied pages.
        """
        super(FileCipherPdf, self).__init__()
        if isinstance(agentkeyservice, Agent):
            if coverpageservice is None:
                self._cCipher = _private.cLib.ionic_filecipher_create_pdf(agentkeyservice._cAgent)
            else:
                self._cCipher = _private.cLib.ionic_filecipher_create_pdf_coverpage(agentkeyservice._cAgent, coverpageservice._cCoverPageService)
        elif isinstance(agentkeyservice,AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            if coverpageservice is None:
                self._cCipher = _private.cLib.ionic_filecipher_create_pdf_services(self._servicesStruct)
            else:
                self._cCipher = _private.cLib.ionic_filecipher_create_pdf_services_coverpage(self._servicesStruct, coverpageservice._cCoverPageService)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice

class FileCipherCsv(FileCipherBase):
    """!Cipher that supports CSV (Comma Separated Values) file encryption / decryption.
    """
    ##(FileCipherFamily) File Cipher Family enumeration for this class
    FAMILY = FileCipherFamily.CSV
    ##(string) File Cipher Family label for this class
    FAMILY_STRING = FileCipherFamily.tostring(FAMILY)
    def __init__(self, agentkeyservice, coverpageservice = None):
        """!Constructs a CSV file cipher from key services and optional coverpage services.

        @param
            agentkeyservice (class instance) The agent or key service used to retrieve and create keys.
        @param
            coverpageservice (class instance) The optional coverpage service used to 
                retrieve cover pages and access denied pages.
        """
        super(FileCipherCsv, self).__init__()
        if isinstance(agentkeyservice, Agent):
            if coverpageservice is None:
                self._cCipher = _private.cLib.ionic_filecipher_create_csv(agentkeyservice._cAgent)
            else:
                self._cCipher = _private.cLib.ionic_filecipher_create_csv_coverpage(agentkeyservice._cAgent, coverpageservice._cCoverPageService)
        elif isinstance(agentkeyservice,AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            if coverpageservice is None:
                self._cCipher = _private.cLib.ionic_filecipher_create_csv_services(self._servicesStruct)
            else:
                self._cCipher = _private.cLib.ionic_filecipher_create_csv_services_coverpage(self._servicesStruct, coverpageservice._cCoverPageService)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice

class FileCipherCms(FileCipherBase):
    """!Cipher that supports CMS (Cryptographic Message Syntax) encryption / decryption.
    """
    ##(FileCipherFamily) File Cipher Family enumeration for this class
    FAMILY = FileCipherFamily.CMS
    ##(string) File Cipher Family label for this class
    FAMILY_STRING = FileCipherFamily.tostring(FAMILY)
    def __init__(self, agentkeyservice):
        """!Constructs a CMS file cipher from key services and optional coverpage services.

        @param
            agentkeyservice (class instance) The agent or key service used to retrieve and create keys.
        """
        super(FileCipherCms, self).__init__()
        if isinstance(agentkeyservice, Agent):
            self._cCipher = _private.cLib.ionic_filecipher_create_cms(agentkeyservice._cAgent)
        elif isinstance(agentkeyservice, AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            self._cCipher = _private.cLib.ionic_filecipher_create_cms_services(self._servicesStruct)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice

