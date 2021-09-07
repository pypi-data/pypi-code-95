"""!Supports protection of small-medium sized text strings and binary
arrays.\n
"""

import ionicsdk._private as _private
from ionicsdk.exceptions import *
from ionicsdk.agent import *
from ionicsdk.services import _ServicesInternal

class ChunkInfo(object):
    """!Data class used to describe attributes of a data chunk.
    """
    def __init__(self, isencrypted=False, keyid=None, cipherid=None):
        """!Constructor which assigns all internal variables.
            
        @param
            isencrypted (bool) Determines whether the chunk is encrypted.
        @param
            keyid (string) The key ID that was used to encrypt the data chunk
        @param
            cipherid (string) The cipher ID of the data chunk
        """

        ##(bool) Determines whether the chunk is encrypted.
        self.isencrypted = isencrypted
        ##(string) The key ID that was used to encrypt the data chunk
        self.keyid = keyid
        ##(string) The cipher ID of the data chunk
        self.cipherid = cipherid
        
    @staticmethod
    def _marshalFromC(cChunkInfo):
        info = ChunkInfo()
        info.isencrypted = bool(cChunkInfo.bIsEncrypted)
        info.keyid = _private.CMarshalUtil.stringFromC(cChunkInfo.pszKeyId)
        info.cipherid = _private.CMarshalUtil.stringFromC(cChunkInfo.pszCipherId)
        return info

class ChunkCipherEncryptAttributes(object):
    """!Allows for extended input and output options during data chunk
    encryption.
    """
    def __init__(self, attributes=None, metadata=None, mutableAttributes=None):
        """!Constructor for decrypt attributes, can pass in attributes, and then assign any other member variables.
            
        @param
            attributes (KeyAttributesDict) The key attributes to associate with data chunk protection key
        @param
            metadata (MetadataDict) The metadata properties to send along with the HTTP request
        @param
            mutableAttributes (KeyAttributesDict) The key mutable attributes to associate with data chunk protection key
        """

        ##(string) The key ID (also known as the key tag)
        self.keyidOut = None
        ##(KeyData) The full key information as returned from the server
        self.keydataOut = None
        ##(string) The data chunk cipher ID that the data was encrypted with
        self.cipheridOut = None
        ##(\link ionicsdk.common.KeyAttributesDict KeyAttributesDict \endlink) The key attributes to associate with data chunk protection key
        self.attributes = attributes
        ##(\link ionicsdk.common.KeyAttributesDict KeyAttributesDict \endlink) The key mutable attributes to associate with data chunk protection key
        self.mutableAttributes = mutableAttributes
        ##(\link ionicsdk.common.MetadataDict MetadataDict \endlink) The metadata properties to send along with the HTTP request
        self.metadata = metadata

class ChunkCipherDecryptAttributes(object):
    """!Allows for extended output options during data chunk decryption.
    """
    def __init__(self, metadata=None):
        """!Constructor for decrypt attributes, can pass in metadata, and then assign any other member variables.
            
        @param
            metadata (MetadataDict) The metadata properties to send along with the HTTP request
        """

        ##(string) The key ID (also known as the key tag)
        self.keyidOut = None
        ##(KeyData) The full key information as returned from the server
        self.keydataOut = None
        ##(string) The data chunk cipher ID that the data was decrypted with
        self.cipheridOut = None
        ##(\link ionicsdk.common.KeyAttributesDict KeyAttributesDict \endlink) The key attributes that are associated with the key used to decrypt the data
        self.attributesOut = None
        ##(\link ionicsdk.common.KeyAttributesDict KeyAttributesDict \endlink) The mutable key attributes that are associated with the key used to decrypt the data
        self.mutableAttributesOut = None
        ##(\link ionicsdk.common.MetadataDict MetadataDict \endlink) The metadata properties to send along with the HTTP request
        self.metadata = metadata

class ChunkCrypto(object):
    """!Utility functions to retrieve ChunkInfo from protected data.
    """
    @staticmethod
    def getinfo(inputdata):
        """!Determines if a data chunk is Ionic protected and various
        pieces of information about the data chunk.

        @param
            inputdata (bytes or string): The data input.

        @return
            A ChunkInfo instance
        """
        cChunkInfo = _private.OWNED_POINTER(_private.CChunkInfo)()
         
        if isinstance(inputdata, ("".__class__, u"".__class__)):
            _private.cLib.ionic_chunkcipher_getinfo_str(_private.CMarshalUtil.stringToC(inputdata)
                                                        ,_private.byref(cChunkInfo))
        else:
            _private.cLib.ionic_chunkcipher_getinfo_bytes(_private.CMarshalUtil.bytesToC(inputdata)
                                                          ,_private.byref(cChunkInfo))

        return ChunkInfo._marshalFromC(cChunkInfo.contents)

class ChunkCipherBase(object):
    """!Base class for all data chunk encryption / decryption ciphers.

    Not to be used directly.  Use one of the appropriate subclasses:\n
    - ChunkCipherAuto - Cipher that automatically chooses the correct
                   cipher to use for data chunk encryption / decryption.\n
    - ChunkCipherV1 - Cipher that supports version 1 data chunk
                        encryption / decryption.\n
    - ChunkCipherV2 - Cipher that supports version 2 data chunk
                        encryption / decryption.\n
    - ChunkCipherV3 - Cipher that supports version 3 data chunk
                        encryption / decryption.\n
    - ChunkCipherV4 - Cipher that supports version 4 data chunk
                        encryption / decryption.\n
    """
    def __new__(cls, *args, **kwargs): # The base class should not be used directly
        if cls is ChunkCipherBase:
            raise NotImplementedError()
        return super(ChunkCipherBase, cls).__new__(cls)
    
    def __init__(self, ):
        """!Constructor for base class.
        """

        self._cCipher = None
        self._cServerResponse = None
    
    @property
    def id(self):
        """!Gets the hard-coded cipher ID of this instance
        @return
            The ID string
        """
        return self.__class__.ID
    
    @property
    def label(self):
        """!Gets the hard-coded cipher label of this instance
        @return
            The label string
        """
        return self.__class__.LABEL

    def getLastServerResponse(self):
        """!Return the Server Response object from the last Agent call.
            @return
            A valid ServerResponse object or None if no server calls have been made yet.
        """
        return ServerResponse._marshalFromC(self._cServerResponse)
    
    def encryptstr(self, plaintext, attributes = None, metadata = None, mutableAttributes = None):
        """!Encrypts an input string into an output string.
        
        This function performs data chunk encryption using the method
        implied by the class name (e.g. ISChunkCryptoV1).

        @param
            plaintext (string): The plaintext input string.
        @param
            attributes (KeyAttributesDict, optional): The
                    attributes to use when creating a key to protect data.
        @param
            metadata (MetadataDict, optional): The metadata
                    properties to send along with the HTTP request.
        @param
            mutableAttributes (KeyAttributesDict, optional): The protection key
                    mutable attributes to use for creating the protection key.
        @return
            The ciphertext output string.
        """
        return self.encryptstr2(plaintext, ChunkCipherEncryptAttributes(attributes, metadata, mutableAttributes))

    def encryptstr2(self, plaintext, encryptattributesInOut):
        """!Encrypts an input string into an output string.
        
        This function performs data chunk encryption using the method
        implied by the class name (e.g. ISChunkCryptoV1).

        @param
            plaintext (string): The plaintext input string.
        @param
            encryptattributesInOut (ChunkCipherEncryptAttributes):
                      Object to provide and return detailed information.
        @return
            The ciphertext output string.  The encryptattributesInOut
            paramater will also be modified.
        """
        # inputs
        cPlainText = _private.CMarshalUtil.stringToC(plaintext)
        cAttributes = KeyAttributesDict._marshalToC(encryptattributesInOut.attributes)
        cMutableAttributes = KeyAttributesDict._marshalToC(encryptattributesInOut.mutableAttributes)
        cMetadata = MetadataDict._marshalToC(encryptattributesInOut.metadata)

        # outputs
        cKeyData = _private.OWNED_POINTER(_private.CKeyData)()
        cCipherId = _private.OWNED_POINTER(_private.c_char)()
        cCipherText = _private.OWNED_POINTER(_private.c_char)()
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_chunkcipher_encrypt_str4(
                self._cCipher,
                cPlainText,
                cAttributes,
                cMutableAttributes,
                cMetadata,
                _private.byref(cCipherText),
                _private.byref(cKeyData),
                _private.byref(cCipherId),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

        # marshal C outputs to Python
        encryptattributesInOut.keydataOut = KeyData._marshalFromC(cKeyData.contents)
        encryptattributesInOut.keyidOut = encryptattributesInOut.keydataOut.id
        encryptattributesInOut.cipheridOut = _private.CMarshalUtil.stringFromC(cCipherId)
        return _private.CMarshalUtil.stringFromC(cCipherText)

    def encryptbytes(self, plaintextbytes, attributes = None, metadata = None, mutableAttributes = None):
        """!Encrypts an input bytes buffer into an output string.
        
        This function performs data chunk encryption using the method
        implied by the class name (e.g. ISChunkCryptoV1).

        @param
            plaintextbytes (bytes): The binary plaintext input buffer.
        @param
            attributes (KeyAttributesDict, optional): The
                    attributes to use when creating a key to protect data.
        @param
            metadata (MetadataDict, optional): The metadata
                    properties to send along with the HTTP request.
        @param
            mutableAttributes (KeyAttributesDict, optional): The protection key
                    mutable attributes to use for creating the protection key.

        @return
            The ciphertext output string.
        """
        return self.encryptbytes2(plaintextbytes, ChunkCipherEncryptAttributes(attributes,metadata, mutableAttributes))

    def encryptbytes2(self, plaintextbytes, encryptattributesInOut):
        """!Encrypts an input bytes buffer into an output string.
        
        This function performs data chunk encryption using the method
        implied by the class name (e.g. ISChunkCryptoV1).

        @param
            plaintextbytes (bytes): The binary plaintext input buffer.
        @param
            encryptattributesInOut (ChunkCipherEncryptAttributes):
                      Object to provide and return detailed information.

        @return
            The ciphertext output string.  The encryptattributesInOut
            paramater will also be modified.
        """
        # inputs
        cPlainTextBytes = _private.CMarshalUtil.bytesToC(plaintextbytes)
        cAttributes = KeyAttributesDict._marshalToC(encryptattributesInOut.attributes)
        cMutableAttributes = KeyAttributesDict._marshalToC(encryptattributesInOut.mutableAttributes)
        cMetadata = MetadataDict._marshalToC(encryptattributesInOut.metadata)
        
        # outputs
        cKeyData = _private.OWNED_POINTER(_private.CKeyData)()
        cCipherId = _private.OWNED_POINTER(_private.c_char)()
        cCipherText = _private.OWNED_POINTER(_private.c_char)()
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_chunkcipher_encrypt_bytes4(
                self._cCipher,
                cPlainTextBytes,
                cAttributes,
                cMutableAttributes,
                cMetadata,
                _private.byref(cCipherText),
                _private.byref(cKeyData),
                _private.byref(cCipherId),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
        
        # marshal C outputs to Python
        encryptattributesInOut.keydataOut = KeyData._marshalFromC(cKeyData.contents)
        encryptattributesInOut.keyidOut = encryptattributesInOut.keydataOut.id
        encryptattributesInOut.cipheridOut = _private.CMarshalUtil.stringFromC(cCipherId)
        return _private.CMarshalUtil.stringFromC(cCipherText)

    def decryptstr(self, ciphertext, metadata = None):
        """!Decrypts an input string into an output string.

        This function performs data chunk decryption using the method
        implied by the class name (e.g. ISChunkCryptoV1).

        @param
            ciphertext (string): The ciphertext input string.
        @param
            metadata (MetadataDict, optional): The metadata
                         properties to send along with the HTTP request.

        @return
            The plaintext output string.
        """
        return self.decryptstr2(ciphertext, ChunkCipherDecryptAttributes(metadata))

    def decryptstr2(self, ciphertext, decryptattributesInOut):
        """!Decrypts an input string into an output string.

        This function performs data chunk decryption using the method
        implied by the class name (e.g. ISChunkCryptoV1).

        @param
            ciphertext (string): The ciphertext input string.
        @param
            decryptattributesInOut (ChunkCipherDecryptAttributes):
                      Object to provide and return detailed information.
        @return
            The plaintext output string. The decryptattributesInOut
            paramater will also be modified.
        """
        # inputs
        cCipherText = _private.CMarshalUtil.stringToC(ciphertext)
        cMetadata = MetadataDict._marshalToC(decryptattributesInOut.metadata)
        
        # outputs
        cKeyData = _private.OWNED_POINTER(_private.CKeyData)()
        cCipherId = _private.OWNED_POINTER(_private.c_char)()
        cPlainText = _private.OWNED_POINTER(_private.c_char)()
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_chunkcipher_decrypt_str3(
                self._cCipher,
                cCipherText,
                cMetadata,
                _private.byref(cPlainText),
                _private.byref(cKeyData),
                _private.byref(cCipherId),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

        # marshal C outputs to Python
        decryptattributesInOut.keydataOut = KeyData._marshalFromC(cKeyData.contents)
        decryptattributesInOut.attributesOut = decryptattributesInOut.keydataOut.attributes
        decryptattributesInOut.mutableAttributesOut = decryptattributesInOut.keydataOut.mutableAttributes
        decryptattributesInOut.keyidOut = decryptattributesInOut.keydataOut.id
        decryptattributesInOut.cipheridOut = _private.CMarshalUtil.stringFromC(cCipherId)            
        return _private.CMarshalUtil.stringFromC(cPlainText)

    def decryptbytes(self, ciphertext, metadata = None):
        """!Decrypts an input string into an output byte buffer.

        This function performs data chunk decryption using the method
        implied by the class name (e.g. ISChunkCryptoV1).

        @param
            ciphertext (string): The ciphertext input string.
        @param
            metadata (MetadataDict, optional): The metadata
                         properties to send along with the HTTP request.

        @return
            The plaintext output byte buffer.
        """
        return self.decryptbytes2(ciphertext, ChunkCipherDecryptAttributes(metadata))

    def decryptbytes2(self, ciphertext, decryptattributesInOut):
        """!Decrypts an input string into an output bytes buffer.

        This function performs data chunk decryption using the method
        implied by the class name (e.g. ISChunkCryptoV1).

        @param
            ciphertext (string): The ciphertext input string.
        @param
            decryptattributesInOut (ChunkCipherDecryptAttributes):
                      Object to provide and return detailed information.
        @return
            The plaintext output bytes buffer. The 
            decryptattributesInOut paramater will also be modified.
        """
        # inputs
        cCipherText = _private.CMarshalUtil.stringToC(ciphertext)
        cMetadata = MetadataDict._marshalToC(decryptattributesInOut.metadata)
        
        # outputs
        cKeyData = _private.OWNED_POINTER(_private.CKeyData)()
        cCipherId = _private.OWNED_POINTER(_private.c_char)()
        cPlainTextBytes = _private.OWNED_POINTER(_private.CBytes)()
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_chunkcipher_decrypt_bytes3(
                self._cCipher,
                cCipherText,
                cMetadata,
                _private.byref(cPlainTextBytes),
                _private.byref(cKeyData),
                _private.byref(cCipherId),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

        # marshal C outputs to Python
        decryptattributesInOut.keydataOut = KeyData._marshalFromC(cKeyData.contents)
        decryptattributesInOut.attributesOut = decryptattributesInOut.keydataOut.attributes
        decryptattributesInOut.mutableAttributesOut = decryptattributesInOut.keydataOut.mutableAttributes
        decryptattributesInOut.keyidOut = decryptattributesInOut.keydataOut.id
        decryptattributesInOut.cipheridOut = _private.CMarshalUtil.stringFromC(cCipherId)
        return _private.CMarshalUtil.bytesFromC(cPlainTextBytes)

class ChunkCipherAuto(ChunkCipherBase):
    """!Cipher that automatically chooses the correct cipher to use for
    data chunk encryption / decryption.

    By default, when encrypting using ChunkCipherAuto, the result is encoded using the ChunkCipherV2
    format.  When decrypting using ChunkCipherAuto, the appropriate ChunkCipher is used.
    """

    ##ChunkAuto Chunk Cipher ID
    ID = "ChunkAuto"
    ##ChunkAuto Chunk Cipher text label
    LABEL = "Chunk Cipher Auto"
    def __init__(self, agentkeyservice):
        """!Constructor which takes an key service refernce
            
        @param
            agentkeyservice (class instance) An Agent or key service used to retrieve and create keys
        """

        super(ChunkCipherAuto, self).__init__()
        if isinstance(agentkeyservice, Agent):
            self._cCipher = _private.cLib.ionic_chunkcipher_create_auto(agentkeyservice._cAgent)
        elif isinstance(agentkeyservice, AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            self._cCipher = _private.cLib.ionic_chunkcipher_create_auto_services(self._servicesStruct)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice

class ChunkCipherV1(ChunkCipherBase):
    """!Cipher that supports version 1 data chunk encryption /
    decryption.
    """
    ##ChunkV1 Chunk Cipher ID
    ID = "ChunkV1"
    ##ChunkV1 Chunk Cipher text label
    LABEL = "Chunk Cipher V1"
    def __init__(self, agentkeyservice):
        """!Constructor which takes an key service refernce
            
        @param
            agentkeyservice (class instance) An Agent or key service used to retrieve and create keys
        """

        super(ChunkCipherV1, self).__init__()
        if isinstance(agentkeyservice, Agent):
            self._cCipher = _private.cLib.ionic_chunkcipher_create_v1(agentkeyservice._cAgent)
        elif isinstance(agentkeyservice, AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            self._cCipher = _private.cLib.ionic_chunkcipher_create_v1_services(self._servicesStruct)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice

class ChunkCipherV2(ChunkCipherBase):
    """!Cipher that supports version 2 data chunk encryption /
    decryption.
    """
    ##ChunkV2 Chunk Cipher ID
    ID = "ChunkV2"
    ##ChunkV2 Chunk Cipher text label
    LABEL = "Chunk Cipher V2"
    def __init__(self, agentkeyservice):
        """!Constructor which takes an key service refernce
            
        @param
            agentkeyservice (class instance) An Agent or key service used to retrieve and create keys
        """

        super(ChunkCipherV2, self).__init__()
        if isinstance(agentkeyservice, Agent):
            self._cCipher = _private.cLib.ionic_chunkcipher_create_v2(agentkeyservice._cAgent)
        elif isinstance(agentkeyservice, AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            self._cCipher = _private.cLib.ionic_chunkcipher_create_v2_services(self._servicesStruct)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice

class ChunkCipherV3(ChunkCipherBase):
    """!Cipher that supports version 3 data chunk encryption /
    decryption.
    """
    ##ChunkV3 Chunk Cipher ID
    ID = "ChunkV3"
    ##ChunkV3 Chunk Cipher text label
    LABEL = "Chunk Cipher V3"
    def __init__(self, agentkeyservice):
        """!Constructor which takes an key service refernce
            
        @param
            agentkeyservice (class instance) An Agent or key service used to retrieve and create keys
        """

        super(ChunkCipherV3, self).__init__()
        if isinstance(agentkeyservice, Agent):
            self._cCipher = _private.cLib.ionic_chunkcipher_create_v3(agentkeyservice._cAgent)
        elif isinstance(agentkeyservice, AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            self._cCipher = _private.cLib.ionic_chunkcipher_create_v3_services(self._servicesStruct)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice

class ChunkCipherV4(ChunkCipherBase):
    """!Cipher that supports version 4 data chunk encryption /
    decryption.
    """
    ##ChunkV4 Chunk Cipher ID
    ID = "ChunkV4"
    ##ChunkV4 Chunk Cipher text label
    LABEL = "Chunk Cipher V4"
    def __init__(self, agentkeyservice):
        """!Constructor which takes an key service refernce
            
        @param
            agentkeyservice (class instance) An Agent or key service used to retrieve and create keys
        """

        super(ChunkCipherV4, self).__init__()
        if isinstance(agentkeyservice, Agent):
            self._cCipher = _private.cLib.ionic_chunkcipher_create_v4(agentkeyservice._cAgent)
        elif isinstance(agentkeyservice, AgentKeyServicesBase):
            self._servicesInternal = _ServicesInternal(agentkeyservice)
            self._servicesStruct = self._servicesInternal.getServices()
            self._cCipher = _private.cLib.ionic_chunkcipher_create_v4_services(self._servicesStruct)
        else:
            raise Exception("Please supply an Agent or extend AgentKeyServices.  Exceptions generated by the supplied class will not transfer through the native library and may be difficult to understand")
        self._cAgent = agentkeyservice
