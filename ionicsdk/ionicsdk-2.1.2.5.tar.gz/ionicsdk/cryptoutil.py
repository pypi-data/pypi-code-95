"""Various cryptographics functions.
"""
import ionicsdk._private as _private

def sha256(inbytes):
    """!Generate a SHA256 hash code
        
    @param
        inbytes (bytes): The data to hash
        
    @return
        (bytes) The 256 bit hash as a byte array
    """
    # inputs
    cInputData = _private.CMarshalUtil.bytesToC(inbytes)

    # outputs
    cOutputLen = 32
    cOutputData = _private.POINTER(_private.ARRAY(_private.c_ubyte, cOutputLen))()
    cOutputData.contents = (_private.c_ubyte * cOutputLen)()

    
    # call into C library to perform the work
    _private.cLib.ionic_crypto_sha256(
          cInputData,
          _private.cast(cOutputData, _private.POINTER(_private.c_ubyte)),
          cOutputLen)

    # marshal C outputs to Python
    return _private.string_at(cOutputData, cOutputLen)

def hmac_sha256(inbytes, keybytes):
    """!Generate a HMAC_SHA256 hash code
        
    @param
        inbytes (bytes): The data to hash
    @param 
        keybytes (bytes): The key bytes
        
    @return
        (bytes) The 256 bit hash as a byte array
    """

    # inputs
    cInputData = _private.CMarshalUtil.bytesToC(inbytes)
    cKeyBytes = _private.CMarshalUtil.bytesToC(keybytes)

    # outputs
    cOutputLen = 32
    cOutputData = _private.POINTER(_private.ARRAY(_private.c_ubyte, cOutputLen))()
    cOutputData.contents = (_private.c_ubyte * cOutputLen)()

    
    # call into C library to perform the work
    _private.cLib.ionic_crypto_hmac_sha256(
        cInputData,
        cKeyBytes,
        _private.cast(cOutputData, _private.POINTER(_private.c_ubyte)),
        cOutputLen)

    # marshal C outputs to Python
    return _private.string_at(cOutputData, cOutputLen)
    
def sha512(inbytes):
    """!Generate a SHA512 hash code
        
    @param
        inbytes (bytes): The data to hash
        
    @return
        (bytes) The 256 bit hash as a byte array
    """

    # inputs
    cInputData = _private.CMarshalUtil.bytesToC(inbytes)

    # outputs
    cOutputLen = 64
    cOutputData = _private.POINTER(_private.ARRAY(_private.c_ubyte, cOutputLen))()
    cOutputData.contents = (_private.c_ubyte * cOutputLen)()

    
    # call into C library to perform the work
    _private.cLib.ionic_crypto_sha512(
        cInputData,
        _private.cast(cOutputData, _private.POINTER(_private.c_ubyte)),
        cOutputLen)

    # marshal C outputs to Python
    return _private.string_at(cOutputData, cOutputLen)

def hmac_sha512(inbytes, keybytes):
    """!Generate a HMAC_SHA512 hash code
        
    @param
        inbytes (bytes): The data to hash
    @param
        keybytes (bytes): The key bytes
        
    @return
        (bytes) The 256 bit hash as a byte array
    """

    # inputs
    cInputData = _private.CMarshalUtil.bytesToC(inbytes)
    cKeyBytes = _private.CMarshalUtil.bytesToC(keybytes)

    # outputs
    cOutputLen = 64
    cOutputData = _private.POINTER(_private.ARRAY(_private.c_ubyte, cOutputLen))()
    cOutputData.contents = (_private.c_ubyte * cOutputLen)()

    
    # call into C library to perform the work
    _private.cLib.ionic_crypto_hmac_sha512(
        cInputData,
        cKeyBytes,
        _private.cast(cOutputData, _private.POINTER(_private.c_ubyte)),
        cOutputLen)

    # marshal C outputs to Python
    return _private.string_at(cOutputData, cOutputLen)
    
def pbkdf2(inbytes, saltbytes, iterations, hashlen):
    """!Performs the PBKDF2 key derivation algorithm on provided input bytes and optional salt
    
    @param
        inbytes (bytes): The data to hash
    @param
        saltbytes (bytes): The salt bytes
    @param
        iterations (int): The number of iterations (must be greater than zero)
    @param
        hashlen (int): The length of the desired output hash length, which must be greater than
            zero. The computed hash will be this length.
    
    @return
        (bytes) The output bytes
    """

    # inputs
    cInputData = _private.CMarshalUtil.bytesToC(inbytes)
    cSaltBytes = _private.CMarshalUtil.bytesToC(saltbytes)
    cIterations = iterations
    
    # outputs
    cOutputLen = hashlen
    cOutputData = _private.POINTER(_private.ARRAY(_private.c_ubyte, cOutputLen))()
    cOutputData.contents = (_private.c_ubyte * cOutputLen)()

    
    # call into C library to perform the work
    _private.cLib.ionic_crypto_pbkdf2(
        cInputData,
        cSaltBytes,
        cIterations,
        _private.cast(cOutputData, _private.POINTER(_private.c_ubyte)),
        cOutputLen,
        cOutputLen)

    # marshal C outputs to Python
    return _private.string_at(cOutputData, cOutputLen)
    

def initialize():
    """!Initialize the crypto library.
        This function must be called before any function from any part of the cryptography
        library may be called.  Applications typically call this function during startup before
        doing any work.
        \n\n
        NOTE: crypto functions will call this function as needed, so the only reason the user 
        might want to call it themselves is to check for a bad result or to force the crypto 
        module to load at a convenient earlier time.
        \n\n
        This function may be called redundantly, and when called this way, it throws the exception
        from the initial call, if any error occurred at that time.
    @return
        None
    """
    _private.cLib.ionic_crypto_initialize()

def shutdown():
    """!Shutdown the crypto library.
        This function should be called before the application terminates or when the crypto library is no longer
        needed.  This gives the crypto library a chance to release any resources that were allocated by
        initialization or during operation. This function calls the crypto module shutdown internally 
        and then unloads the crypto module.
        \n\n
        A user might use this to unload a crypto module in preparation for loading some other alternate module.
        Users should do this with great care as any memory allocated by the old module will have undefined
        behavior with the new module - for example, an RSA key generated or loaded using the crypto API. This
        data will likely contain entirely different formats internally.
    @return
        None
    """
    _private.cLib.ionic_crypto_shutdown()

def setCryptoSharedLibraryFipsMode(isFips):
    """!Sets whether on the Windows, Mac, or Linux platform, ISCRYPTO will load a FIPS approved 
        crypto module or not. The FIPS approved module will be older code, in general, and on
        Linux, may block waiting for entropy.

    @param
        [in] isFips (bool) true for FIPS module, false for the alternate
    @return
        None
    """
    _private.cLib.ionic_crypto_set_crypto_shared_library_fips_mode(isFips)

def setCryptoSharedLibraryCustomDirectory(sharedDirectory):
    """!Allows the user to set a custom folder for Ionic to check for the Crypto module.
        As an example, the SDK, by default, checks for the crypto module in the same directory
        as the currently running executable. However, an installation may place these in a central
        location.
    @param
        [in] sharedDirectory (unicode) directory to find the crypto module.
    @return
        None
    """
    cSharedDirectory = _private.CMarshalUtil.stringToC(sharedDirectory)
    _private.cLib.ionic_crypto_set_crypto_shared_library_custom_directory(cSharedDirectory)

def setCryptoSharedLibraryCustomPath(sharedLibPath):
    """!Allows the user to use a custom crypto module. The module must contain specific Ionic API.
        This overrides any other settings regarding which crypto module to load.

    @param
        [in] sharedLibPath (unicode) full path name of a custom crypto shared library.
    @return
        None
    """
    cSharedLibPath = _private.CMarshalUtil.stringToC(sharedLibPath)
    _private.cLib.ionic_crypto_set_crypto_shared_library_custom_path(cSharedLibPath)

def getCryptoSharedLibraryLoadedFilename():
    """!Gets the full path filename of the crypto module loaded or an empty string otherwise.
        Allows the user to check if the crypto module has loaded and if it is the correct module.

    @return
        Full path filename of the crypto module loaded or an empty string otherwise.
    """
    cFilename = _private.cLib.ionic_crypto_get_crypto_shared_library_loaded_filename()
    return _private.CMarshalUtil.stringFromC(cFilename)
