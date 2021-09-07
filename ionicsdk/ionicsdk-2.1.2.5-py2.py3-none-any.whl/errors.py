"""!Error codes used by ionicsdk."""

import ionicsdk._private as _private
import numbers

class IonicError(object):
    """!Defines error codes produced by the SDK and a method to retrieve a description of the error.
    Most errors and their string values will be added in the IonicMessage message body.
@details


AGENT_OK                        0
Success code.

AGENT_ERROR                     40001
A general error occurred, but its specific problem is not represented with its own code.

AGENT_UNKNOWN                   40002
An unknown and unexpected error occurred.

AGENT_NOMEMORY                  40003
A memory allocation failed.
This can happen if there is not a sufficient amount of memory available to perform an operation.

AGENT_MISSINGVALUE              40004
An expected and required value was not found.
This is typically emitted from functions that are responsible for parsing / deserializing data.

AGENT_INVALIDVALUE              40005
A value was found that is invalid.
For example, a string value was expected, but it was actually an integer.  This is typically
         emitted from functions that are responsible for parsing / deserializing data.

AGENT_NOINIT                    40006
The agent was used before being initialized.
Not applicable in this context as the Agent is initialized at creation.

AGENT_DOUBLEINIT                40007
Agent initialization was performed twice.
Not applicable in this context as the Agent is initialized at creation.

AGENT_CREATEFINGERPRINT         40008
Fingerprint creation failed.

AGENT_REQUESTFAILED             40009
A network request failed.
A request failed due to connection failure, unknown server, unresponsive server, or other network problem.

AGENT_PARSEFAILED               40010
The parsing of some serialized data failed.
This typically happens if a file or block of data is corrupted or of an unexpected format.

AGENT_UNEXPECTEDRESPONSE        40011
A server replied with a response that the agent was not expecting.
This can happen if the server rejects a request, it doesn't support the API version used by the agent, etc.

AGENT_BADCONFIG                 40012
The agent configuration is invalid.
This could be because the HTTP implementation is not recognized, the server hostname/IP is empty, etc.

AGENT_OPENFILE                  40013
A file failed to open.
This normally happens because the file path provided does not exist or it is
         not accessible due to lack of permission.

AGENT_BADREQUEST                40014
The request object is invalid.
The request object failed validation in the agent code.  This can happen if
         any of the request data is not acceptable (e.g. empty key ID, required properties missing).

AGENT_BADRESPONSE               40015
The response object is invalid.
The response object failed validation in the agent code.  This means that the
         server responseded with an invalid / unacceptable response.

AGENT_BADREDIRECT               40016
The server redirected the agent to an invalid location (e.g. an empty URL)
This is typically indicative that there is a problem on the server side.

AGENT_TOOMANYREDIRECTS          40017
The maximum amount of allowed server redirects has been hit.
The server redirected us too many times.  The maximum number of allowed redirects can be set during
         Agent creation via AgentConfig.maxredirects.

AGENT_NOTIMPLEMENTED            40018
The function (or a function it depends on) is not implemented.

AGENT_NOTALLOWED                40019
The function (or a function it depends on) is not allowed to be called
This typically happens if the function would knowingly cause a problem if it were to be run.

AGENT_TIMEOUT                   40020
An operation has timed out.
This happens when a blocking function has been used with a maximum wait time, and that time has expired.

AGENT_NULL_INPUT                40021
A value of None was passed to a function that does not accept None.

AGENT_NO_DEVICE_PROFILE         40022
An active device profile has not been set.
This happens when a function is called that requires an active device profile, but there is no profile set yet (e.g. Agent.createkeys()).

AGENT_RESOURCE_NOT_FOUND        40023
A resource was not found.
This happens when attempting to access a resource that does not exist.

AGENT_KEY_DENIED                40024
A request to create or fetch a key was denied by the server.

AGENT_FPHASH_DENIED             40025
A request was denied because there was a fingerprint hash mismatch.

AGENT_FPFULL_DENIED             40026
A request was denied because the full fingerprint was denied.

AGENT_CID_TIMESTAMP_DENIED      40027
A request was denied because the conversation ID (CID) timestamp was denied.

AGENT_NO_PROFILE_PERSISTOR      40028
No default profile persistor is available for the current platform. A profile persistor must be specified.

AGENT_LOAD_PROFILES_FAILED      40029
Failed to load device profiles. 
This may happen if an incorrect password was provided, the storage file is corrupt, or some other problem occurred.

AGENT_INVALID_KEY               40030
A key is invalid in some way (key ID, key bytes, etc).
This may happen if a key was found to be invalid. For example, if the key is the wrong size
         (any size other than 32 bytes), the key ID string is empty or contains invalid characters,
         etc.
         
AGENT_STALE_KEY_ATTRIBUTES      40031
Key updated failed because key attribute data is stale.
This happens when a key update request is performed via Agent.updatekeys() or Agent.updatekey()
        and the key server denies the request because it detected that the client has a stale version
        of the key. A stale key is one which has been updated by another client without the knowledge
        of the client who requested a separate update.

This may happen, for example, if two or more different clients attempt to update the same key at a very
        similar time. In this case, there is a race condition, and the first client request to be
        processed works successfully, but the other clients will have their requests denied.

To remedy this error, the client must retrieve the key again from the key server (via Agent.getkey()
        or variants), apply the desired changes to it and perform another update request via 
        Agent.updatekeys() or Agent.updatekey().

AGENT_DUPLICATE_KEY             40032
A keys update request contains two or more entries with the same key id.
This is a user error.

AGENT_HEADER_NOT_FOUND          40033
A header was not found in the specified data.
This may happen if the data version is older and special handling for this error may be necessary to
        support previous SDK versions existing on the system.
        
AGENT_NO_SECURE_CONNECTION      40034
An HTTPS secure connection was not achieved.
This commonly happens when the device OS is either setup without TLS 1.x, or is intentionally
         set to use a weaker security standard. Ionic servers require at least TLS 1.0.

CRYPTO_OK                       0
Success code.

CRYPTO_ERROR                    50001
A general error occurred, but its specific problem is not represented with its own code.

CRYPTO_UNKNOWN                  50002
An unknown and unexpected error occurred.

CRYPTO_NULL_INPUT               50003
A value of None was passed to one of the crypto functions.

CRYPTO_BAD_INPUT                50004
An invalid input value was encountered.
An input value was found that is invalid.  For example, a buffer length
         input was equal to zero.

CRYPTO_NO_INIT                  50005
CryptoAbstract module has not been initialized.
The crypto module was used before being initialized.

CRYPTO_NOMEMORY                 50006
Memory allocation error.
This can happen if there is not a sufficient amount of memory available
         to perform an operation.

CRYPTO_KEY_VALIDATION           50007
Key validation error.
A key was loaded or generated that did not pass validation.
         For example, this may happen when loading or generating an RSA private key.

CRYPTO_BAD_SIGNATURE            50008
Message signature verification error.
A message signature verification failed.  This can be returned by RSA signature
         verification functions.

CRYPTO_SEED_OVERFLOW            50009
A seed overflow occurred during RSA private key generation.
During RSA private key generation, it is possible for the random seed to overflow
         (although extremely unlikely).  In that situation, RSA key generation is aborted and the
         CRYPTO_RSA_SEED_OVERFLOW error code is returned.
         When this error is encountered, it is recommended to simply try again.

CRYPTO_FATAL                    50100
Fatal error.
A fatal error has occurred and the module will no longer be usable.
         This will happen if any POST test, healthcheck test, or any other operational
         test fails at any time.  such failure of any test indicates the possibility of
         the module being compromised, and so it becomes disabled.

FILECRYPTO_OK                   0
Success code.

FILECRYPTO_ERROR                80001
A general error occurred, but its specific problem is not represented with its own code.

FILECRYPTO_UNKNOWN              80002
An unknown and unexpected error occurred.

FILECRYPTO_NOMEMORY             80003
A memory allocation failed.
This can happen if there is not a sufficient amount of memory available to perform an operation.

FILECRYPTO_MISSINGVALUE         80004
An expected and required value was not found.
This is typically emitted from functions that are responsible for parsing / deserializing data.

FILECRYPTO_INVALIDVALUE         80005
A value was found that is invalid.
For example, a string value was expected, but it was actually an integer.  This is typically
         emitted from functions that are responsible for parsing / deserializing data.

FILECRYPTO_NULL_INPUT           80006
A value of None was passed to a function that does not accept None.

FILECRYPTO_BAD_INPUT            80007
An invalid input value was encountered.
An input value was found that is invalid.  For example, a buffer length
         input was equal to zero.

FILECRYPTO_OPENFILE             80008
A file failed to open.
This normally happens because the file path provided does not exist or it is
         not accessible due to lack of permission.

FILECRYPTO_EOF                  80009
The end of a file was found before it was expected.
This normally happens if the file has been truncated or is zero length.

FILECRYPTO_NOHEADER             80010
A file header could not be found where it was expected.
This normally happens when trying to decrypt a file that is not encrypted, or the encrypted file has been corrupted.

FILECRYPTO_PARSEFAILED          80011
The parsing of some serialized data failed.
This typically happens if a file or block of data is corrupted or of an unexpected format.

FILECRYPTO_VERSION_UNSUPPORTED  80012
The file version is unsupported or unrecognized.

FILECRYPTO_HASH_VERIFICATION    80013
A hash digest verification failed.
The computed digest did not match the expected digest.

FILECRYPTO_STREAM_WRITE         80014
A failure occurred while writing to a stream.
An error flag of some sort was set on the stream when it was being written to.

FILECRYPTO_RESOURCE_NOT_FOUND   80015
A resource was not found.
This happens when attempting to access a resource that does not exist.

FILECRYPTO_BAD_ZIP              80016
A zip file failed to open because it was not formatted correctly.
This normally happens because the zip file is corrupted in some way (for example, truncated).

FILECRYPTO_UNRECOGNIZED         80017
A file is not supported for Ionic protection.

FILECRYPTO_ALREADY_ENCRYPTED    80018
A file was requested to be encrypted, but it is already encrypted.

FILECRYPTO_NOT_ENCRYPTED        80019
A file was requested to be decrypted, but it is not encrypted.

FILECRYPTO_RENAMEFILE           80020
A file failed to be renamed.
This normally happens because a temporary file was attempted to be renamed in order
         to overwrite an input file during in-place encryption or decryption, but the rename attempt failed
         (see FileCipherBase.encryptinplace()).
         A system level error code is emitted to the logger in this case.
         \n\n
         The file may be open by another process or by another thread in the current process, you may
         not have permissions to write to the file, or some other error occurred.

FILECRYPTO_NOEMBED              80021
A file did not contain an Ionic embed stream.

FILECRYPTO_NO_COVERPAGE         80022
A file type was specified that does not have a cover page.

FILECRYPTO_IOSTREAM_ERROR		80023
An error occurred in the Streams lib.

CHUNKCRYPTO_OK                  0
Success code.

CHUNKCRYPTO_ERROR               20001
A general error occurred, but its specific problem is not represented with its own code.

CHUNKCRYPTO_UNKNOWN             20002
An unknown and unexpected error occurred.

CHUNKCRYPTO_NOMEMORY            20003
A memory allocation failed.
This can happen if there is not a sufficient amount of memory available to perform an operation.

CHUNKCRYPTO_MISSINGVALUE        20004
An expected and required value was not found.
This is typically emitted from functions that are responsible for parsing / deserializing data.

CHUNKCRYPTO_INVALIDVALUE        20005
A value was found that is invalid.
For example, a string value was expected, but it was actually an integer.  This is typically
         emitted from functions that are responsible for parsing / deserializing data.

CHUNKCRYPTO_NULL_INPUT          20006
A value of None pointer was passed to a function that does not accept None.

CHUNKCRYPTO_BAD_INPUT           20007
An invalid input value was encountered.
An input value was found that is invalid.  For example, a buffer length
         input was equal to zero.

CHUNKCRYPTO_EOF                 20009
The end of a data chunk was found before it was expected.
This normally happens if the data chunk has been truncated or is zero length.

CHUNKCRYPTO_PARSEFAILED         20011
The parsing of some serialized data failed.
This typically happens if a file or block of data is corrupted or of an unexpected format.

CHUNKCRYPTO_HASH_VERIFICATION   20013
A hash digest verification failed.
The computed digest did not match the expected digest.

CHUNKCRYPTO_STREAM_WRITE        20014
A failure occurred while writing to a stream.
An error flag of some sort was set on the stream when it was being written to.

CHUNKCRYPTO_RESOURCE_NOT_FOUND  20015
A resource was not found.
This happens when attempting to access a resource that does not exist.

CHUNKCRYPTO_UNRECOGNIZED        20017
A data chunk is not supported for Ionic protection.

CHUNKCRYPTO_ALREADY_ENCRYPTED   20018
A data chunk was requested to be encrypted, but it is already encrypted.

CHUNKCRYPTO_NOT_ENCRYPTED       20019
A data chunk was requested to be decrypted, but it is not encrypted.



HTTP_OK                         0
Success code.

HTTP_ERROR                      13001
A general error occurred, but its specific problem is not represented with its own code.

HTTP_UNKNOWN                    13002
An unknown and unexpected error occurred.

HTTP_NOMEMORY                   13003
A memory allocation failed.
This can happen if there is not a sufficient amount of memory available to perform an operation.

HTTP_MISSINGVALUE               13004
An expected and required value was not found.
This is typically emitted from functions that are responsible for parsing / deserializing data.

HTTP_INVALIDVALUE               13005
A value was found that is invalid.
For example, a string value was expected, but it was actually an integer.  This is typically
         emitted from functions that are responsible for parsing / deserializing data.

HTTP_NULL_INPUT                 13006
A value of None pointer was passed to a function that does not accept None.

HTTP_BAD_INPUT                  13007
An invalid input value was encountered.
An input value was found that is invalid.  For example, a buffer length
         input was equal to zero.

HTTP_TIMEOUT                    13008
An HTTP operation has timed out.
This happens when a blocking HTTP function has been used with a maximum wait time, and that time has expired.

HTTP_PARSEFAILED                13009
The parsing of some serialized data failed.
This typically happens if an HTTP message is malformed, truncated, or otherwise unable to be parsed.

HTTP_OPENFILE                   13010
A file failed to open.
This normally happens because the file path provided does not exist or it is
         not accessible due to lack of permission.

HTTP_METHOD_UNKNOWN             13011
An HTTP method was found that is not recognized.
This happens when parsing an HTTP request and discovering an unknown / unsupported
         HTTP method.  The supported HTTP methods are GET, POST, PUT, HEAD, and DELETE.


The following errors may be generated by the C layer library

ISC_OK                          0
Success code.

ISC_ERROR_BASE                  10000
The base range for C library error codes

ISC_ERROR                       10001
A general error occurred, but its specific problem is not represented with its own code.

ISC_BAD_INPUT                   10003
Invalid input was provided to a function.
This is commonly caused by zero length input to any encrypt or decrypt function.

ISC_NULL_INPUT                  10004
A NULL pointer was provided as an input that is not optional.
Python strings that are empty will generate this error as well.

ISC_BAD_POINTER                 10005
A pointer was given to the ionic_release() function that is not recognized.
A pointer was attempted to be released via ionic_release(), but the pointer 
is unknown to the SDK.  This means that the SDK did not originally allocate
the data, or possibly the data has previously been released and so is no 
longer tracked by the SDK.

ISC_DUPLICATE_POINTER           10006
Internally used error code that indicates a pointer was double-registered.
This error code should never be emitted from any public-facing SDK function.
The code is strictly used internally.

ISC_NOT_FOUND                   10007
An item was not found during a search.
This error code can be returned by functions which search for an item but
cannot find it.  For example, ionic_attributesmap_rmv_value() can return this
code if the specified attribute key or value does not exist.

    """
    def __init__(self):
        """!This is a static class, do not create instances.
        """
        raise NotImplementedError()
    
    @staticmethod
    def tostring(errorcode):
        """!Gets a human-readable string description for any SDK error
        code emitted by any Ionic SDK module.

        @param
            errorcode (int): The error code.

        @return
            String description of the error code.
        """
        if errorcode is None or not isinstance(errorcode, numbers.Integral):
            raise TypeError('errorcode must be numeric')
        cErrorText = _private.cLib.ionic_get_error_str(errorcode)
        return _private.CMarshalUtil.stringFromC(cErrorText)
    ##(int) Error Codes: Success code
    AGENT_OK                         = 0
    ##(int) Error Codes: A general error occurred, but its specific problem is not represented with its own code.
    AGENT_ERROR                      = 40001
    ##(int) Error Codes: An unknown and unexpected error occurred.
    AGENT_UNKNOWN                    = 40002
    ##(int) Error Codes: A memory allocation failed.
    ##      This can happen if there is not a sufficient amount of memory available to perform an operation.
    AGENT_NOMEMORY                   = 40003
    ##(int) Error Codes: An expected and required value was not found.
    ##      This is typically emitted from functions that are responsible for parsing / deserializing data.
    AGENT_MISSINGVALUE               = 40004
    ##(int) Error Codes: A value was found that is invalid.
    ##      For example, a string value was expected, but it was actually an integer.  This is typically
    ##          emitted from functions that are responsible for parsing / deserializing data.
    AGENT_INVALIDVALUE               = 40005
    ##(int) Error Codes: The agent was used before being initialized.
    ##      Not applicable in this context as the Agent is initialized at creation.
    AGENT_NOINIT                     = 40006
    ##(int) Error Codes: Agent initialization was performed twice.
    ##      Not applicable in this context as the Agent is initialized at creation.
    AGENT_DOUBLEINIT                 = 40007
    ##(int) Error Codes: Fingerprint creation failed.
    AGENT_CREATEFINGERPRINT          = 40008
    ##(int) Error Codes: A network request failed.
    ##      A request failed due to connection failure, unknown server, unresponsive server, or other network problem.
    AGENT_REQUESTFAILED              = 40009
    ##(int) Error Codes: The parsing of some serialized data failed.
    ##      This typically happens if a file or block of data is corrupted or of an unexpected format.
    AGENT_PARSEFAILED                = 40010
    ##(int) Error Codes: A server replied with a response that the agent was not expecting.
    ##      This can happen if the server rejects a request, it doesn't support the API version used by the agent, etc.
    AGENT_UNEXPECTEDRESPONSE         = 40011
    ##(int) Error Codes: The agent configuration is invalid.
    ##      This could be because the HTTP implementation is not recognized, the server hostname/IP is empty, etc.
    AGENT_BADCONFIG                  = 40012
    ##(int) Error Codes: A file failed to open.
    ##      This normally happens because the file path provided does not exist or it is
    ##          not accessible due to lack of permission.
    AGENT_OPENFILE                   = 40013
    ##(int) Error Codes: The request object is invalid.
    ##      The request object failed validation in the agent code.  This can happen if
    ##          any of the request data is not acceptable (e.g. empty key ID, required properties missing).
    AGENT_BADREQUEST                 = 40014
    ##(int) Error Codes: The response object is invalid.
    ##      The response object failed validation in the agent code.  This means that the
    ##          server responseded with an invalid / unacceptable response.
    AGENT_BADRESPONSE                = 40015
    ##(int) Error Codes: The server redirected the agent to an invalid location (e.g. an empty URL)
    ##      This is typically indicative that there is a problem on the server side.
    AGENT_BADREDIRECT                = 40016
    ##(int) Error Codes: The maximum amount of allowed server redirects has been hit.
    ##      The server redirected us too many times.  The maximum number of allowed redirects can be set during
    ##          Agent creation via AgentConfig.maxredirects.
    AGENT_TOOMANYREDIRECTS           = 40017
    ##(int) Error Codes: The function (or a function it depends on) is not implemented.
    AGENT_NOTIMPLEMENTED             = 40018
    ##(int) Error Codes: The function (or a function it depends on) is not allowed to be called
    ##      This typically happens if the function would knowingly cause a problem if it were to be run.
    AGENT_NOTALLOWED                 = 40019
    ##(int) Error Codes: An operation has timed out.
    ##      This happens when a blocking function has been used with a maximum wait time, and that time has expired.
    AGENT_TIMEOUT                    = 40020
    ##(int) Error Codes: A value of None was passed to a function that does not accept None.
    AGENT_NULL_INPUT                 = 40021
    ##(int) Error Codes: An active device profile has not been set.
    ##      This happens when a function is called that requires an active device profile, but there is no profile set yet
    ##          (e.g. Agent.createkeys()).
    AGENT_NO_DEVICE_PROFILE          = 40022
    ##(int) Error Codes: A resource was not found.
    ##      This happens when attempting to access a resource that does not exist.
    AGENT_RESOURCE_NOT_FOUND         = 40023
    ##(int) Error Codes: A request to create or fetch a key was denied by the server.
    AGENT_KEY_DENIED                 = 40024
    ##(int) Error Codes: A request was denied because there was a fingerprint hash mismatch.
    AGENT_FPHASH_DENIED              = 40025
    ##(int) Error Codes: A request was denied because the full fingerprint was denied.
    AGENT_FPFULL_DENIED              = 40026
    ##(int) Error Codes: A request was denied because the conversation ID (CID) timestamp was denied.
    AGENT_CID_TIMESTAMP_DENIED       = 40027
    ##(int) Error Codes: No default profile persistor is available for the current platform. A profile persistor must be specified.
    AGENT_NO_PROFILE_PERSISTOR       = 40028
    ##(int) Error Codes: Failed to load device profiles.
    ##      This may happen if an incorrect password was provided, the storage file is corrupt, or some other problem occurred.
    AGENT_LOAD_PROFILES_FAILED       = 40029
    ##(int) Error Codes: A key is invalid in some way (key ID, key bytes, etc).
    ##      This may happen if a key was found to be invalid. For example, if the key is the wrong size
    ##      (any size other than 32 bytes), the key ID string is empty or contains invalid characters, etc.
    AGENT_INVALID_KEY                = 40030

    ##(int) Key updated failed because key attribute data is stale.
    ##      This happens when a key update request is performed via \link ionicsdk.agent.Agent.updatekeys() Agent.updatekeys() \endlink or
    ##      \link ionicsdk.agent.Agent.updatekey() Agent.updatekey() \endlink and the key server denies the request because it detected that the client
    ##      has a stale version of the key. A stale key is one which has been updated by another client
    ##      without the knowledge of the client who requested a separate update.
    ##
    ##      This may happen, for example, if two or more different clients attempt to update the same key
    ##      at a very similar time. In this case, there is a race condition, and the first client request
    ##      to be processed works successfully, but the other clients will have their requests denied.
    ##
    ##      To remedy this error, the client must retrieve the key again from the key server (via
    ##      \link ionicsdk.agent.Agent.getkey() Agent.getkey() \endlink or variants), apply the desired changes to it and perform another
    ##      update request via \link ionicsdk.agent.Agent.updatekeys() Agent.updatekeys() \endlink or \link ionicsdk.agent.Agent.updatekey() Agent.updatekey() \endlink.
    AGENT_STALE_KEY_ATTRIBUTES      = 40031

    ## A keys update request contains two or more entries with the same key id.
    ##      This is a user error.
    AGENT_DUPLICATE_KEY             = 40032

    ## A header was not found in the specified data.
    ##      This may happen if the data version is older and special handling for this error may be
    ##      necessary to support previous SDK versions existing on the system.
    AGENT_HEADER_NOT_FOUND          = 40033

    ## An HTTPS secure connection was not achieved.
    ##      This commonly happens when the device OS is either setup without TLS 1.x, or is intentionally
    ##      set to use a weaker security standard. Ionic servers require at least TLS 1.0.
    AGENT_NO_SECURE_CONNECTION      = 40034
    

    ##(int) Error Codes: Success code.
    CRYPTO_OK                        = 0
    ##(int) Error Codes: A general error occurred, but its specific problem is not represented with its own code.
    CRYPTO_ERROR                     = 50001
    ##(int) Error Codes: An unknown and unexpected error occurred.
    CRYPTO_UNKNOWN                   = 50002
    ##(int) Error Codes: A value of None was passed to one of the crypto functions.
    CRYPTO_NULL_INPUT                = 50003
    ##(int) Error Codes: An invalid input value was encountered.
    ##      An input value was found that is invalid.  For example, a buffer length input was equal to zero.
    CRYPTO_BAD_INPUT                 = 50004
    ##(int) Error Codes: CryptoAbstract module has not been initialized.
    ##      The crypto module was used before being initialized.
    CRYPTO_NO_INIT                   = 50005
    #(int) Error Codes: Memory allocation error.
    ##      This can happen if there is not a sufficient amount of memory available to perform an operation.
    CRYPTO_NOMEMORY                  = 50006
    ##(int) Error Codes: Key validation error.
    ##      A key was loaded or generated that did not pass validation.
    ##          For example, this may happen when loading or generating an RSA private key.
    CRYPTO_KEY_VALIDATION            = 50007
    ##(int) Error Codes: Message signature verification error.
    ##      A message signature verification failed.  This can be returned by RSA signature verification functions.
    CRYPTO_BAD_SIGNATURE             = 50008
    ##(int) Error Codes: A seed overflow occurred during RSA private key generation.
    ##      During RSA private key generation, it is possible for the random seed to overflow (although extremely unlikely).
    ##          In that situation, RSA key generation is aborted and the CRYPTO_RSA_SEED_OVERFLOW error code is returned.
    ##          When this error is encountered, it is recommended to simply try again.
    CRYPTO_SEED_OVERFLOW             = 50009
    ##(int) Error Codes: Fatal error.
    ##      A fatal error has occurred and the module will no longer be usable. This will happen if any POST test, healthcheck
    ##          test, or any other operational test fails at any time.  such failure of any test indicates the possibility of
    ##          the module being compromised, and so it becomes disabled.
    CRYPTO_FATAL                     = 50100

    ##(int) Error Codes: Success code.
    FILECRYPTO_OK                    = 0
    ##(int) Error Codes: A general error occurred, but its specific problem is not represented with its own code.
    FILECRYPTO_ERROR                 = 80001
    ##(int) Error Codes: An unknown and unexpected error occurred.
    FILECRYPTO_UNKNOWN               = 80002
    #(int) Error Codes: Memory allocation error.
    ##      This can happen if there is not a sufficient amount of memory available to perform an operation.
    FILECRYPTO_NOMEMORY              = 80003
    ##(int) Error Codes: An expected and required value was not found.
    ##      This is typically emitted from functions that are responsible for parsing / deserializing data.
    FILECRYPTO_MISSINGVALUE          = 80004
    ##(int) Error Codes: A value was found that is invalid.
    ##      For example, a string value was expected, but it was actually an integer.  This is typically
    ##          emitted from functions that are responsible for parsing / deserializing data.
    FILECRYPTO_INVALIDVALUE          = 80005
    ##(int) Error Codes: A value of None was passed to one of the crypto functions.
    FILECRYPTO_NULL_INPUT            = 80006
    ##(int) Error Codes: An invalid input value was encountered.
    ##      An input value was found that is invalid.  For example, a buffer length input was equal to zero.
    FILECRYPTO_BAD_INPUT             = 80007
    ##(int) Error Codes: A file failed to open.
    ##      This normally happens because the file path provided does not exist or it is not accessible due to lack of permission.
    FILECRYPTO_OPENFILE              = 80008
    ##(int) Error Codes: The end of a file was found before it was expected.
    ##      This normally happens if the file has been truncated or is zero length.
    FILECRYPTO_EOF                   = 80009
    ##(int) Error Codes: A file header could not be found where it was expected.
    ##      This normally happens when trying to decrypt a file that is not encrypted, or the encrypted file has been corrupted.
    FILECRYPTO_NOHEADER              = 80010
    ##(int) Error Codes: The parsing of some serialized data failed.
    ##      This typically happens if a file or block of data is corrupted or of an unexpected format.
    FILECRYPTO_PARSEFAILED           = 80011
    ##(int) Error Codes: The file version is unsupported or unrecognized.
    FILECRYPTO_VERSION_UNSUPPORTED   = 80012
    ##(int) Error Codes: A hash digest verification failed.
    ##      The computed digest did not match the expected digest.
    FILECRYPTO_HASH_VERIFICATION     = 80013
    ##(int) Error Codes: A failure occurred while writing to a stream.
    ##      An error flag of some sort was set on the stream when it was being written to.
    FILECRYPTO_STREAM_WRITE          = 80014
    ##(int) Error Codes: A resource was not found.
    ##      This happens when attempting to access a resource that does not exist.
    FILECRYPTO_RESOURCE_NOT_FOUND    = 80015
    ##(int) Error Codes: A zip file failed to open because it was not formatted correctly.
    ##      This normally happens because the zip file is corrupted in some way (for example, truncated).
    FILECRYPTO_BAD_ZIP               = 80016
    ##(int) Error Codes: A file is not supported for Ionic protection.
    FILECRYPTO_UNRECOGNIZED          = 80017
    ##(int) Error Codes: A file was requested to be encrypted, but it is already encrypted.
    FILECRYPTO_ALREADY_ENCRYPTED     = 80018
    ##(int) Error Codes: A file was requested to be decrypted, but it is not encrypted.
    FILECRYPTO_NOT_ENCRYPTED         = 80019
    ##(int) Error Codes: A file failed to be renamed.
    ##      This normally happens because a temporary file was attempted to be renamed in order to overwrite an input
    ##          file during in-place encryption or decryption, but the rename attempt failed
    ##          (see FileCipherBase.encryptinplace()). A system level error code is emitted to the logger in this case.
    ##          \n\n
    ##          The file may be open by another process or by another thread in the current process, you may
    ##          not have permissions to write to the file, or some other error occurred.
    FILECRYPTO_RENAMEFILE            = 80020
    ##(int) Error Codes: A file did not contain an Ionic embed stream.
    FILECRYPTO_NOEMBED               = 80021
    ##(int) A file type was specified that does not have a cover page.
    FILECRYPTO_NO_COVERPAGE          = 80022
    ##(int) An error occurred in the Streams lib.
    FILECRYPTO_IOSTREAM_ERROR		 = 80023


    ##(int) Error Codes: Success code.
    CHUNKCRYPTO_OK                   = 0
    ##(int) Error Codes: A general error occurred, but its specific problem is not represented with its own code.
    CHUNKCRYPTO_ERROR                = 20001
    ##(int) Error Codes: An unknown and unexpected error occurred.
    CHUNKCRYPTO_UNKNOWN              = 20002
    #(int) Error Codes: Memory allocation error.
    ##      This can happen if there is not a sufficient amount of memory available to perform an operation.
    CHUNKCRYPTO_NOMEMORY             = 20003
    ##(int) Error Codes: An expected and required value was not found.
    ##      This is typically emitted from functions that are responsible for parsing / deserializing data.
    CHUNKCRYPTO_MISSINGVALUE         = 20004
    ##(int) Error Codes: A value was found that is invalid.
    ##      For example, a string value was expected, but it was actually an integer.  This is typically emitted from
    ##      functions that are responsible for parsing / deserializing data.
    CHUNKCRYPTO_INVALIDVALUE         = 20005
    ##(int) Error Codes: A value of None was passed to one of the crypto functions.
    CHUNKCRYPTO_NULL_INPUT           = 20006
    ##(int) Error Codes: An invalid input value was encountered.
    ##      An input value was found that is invalid.  For example, a buffer length input was equal to zero.
    CHUNKCRYPTO_BAD_INPUT            = 20007
    ##(int) Error Codes: The end of a data chunk was found before it was expected.
    ##      This normally happens if the data chunk has been truncated or is zero length.
    CHUNKCRYPTO_EOF                  = 20009
    ##(int) Error Codes: The parsing of some serialized data failed.
    ##      This typically happens if a file or block of data is corrupted or of an unexpected format.
    CHUNKCRYPTO_PARSEFAILED          = 20011
    ##(int) Error Codes: A hash digest verification failed.
    ##      The computed digest did not match the expected digest.
    CHUNKCRYPTO_HASH_VERIFICATION    = 20013
    ##(int) Error Codes: A failure occurred while writing to a stream.
    ##      An error flag of some sort was set on the stream when it was being written to.
    CHUNKCRYPTO_STREAM_WRITE         = 20014
    ##(int) Error Codes: A resource was not found.
    ##      This happens when attempting to access a resource that does not exist.
    CHUNKCRYPTO_RESOURCE_NOT_FOUND   = 20015
    ##(int) Error Codes: A data chunk is not supported for Ionic protection.
    CHUNKCRYPTO_UNRECOGNIZED         = 20017
    ##(int) Error Codes: A data chunk was requested to be encrypted, but it is already encrypted.
    CHUNKCRYPTO_ALREADY_ENCRYPTED    = 20018
    ##(int) Error Codes: A data chunk was requested to be decrypted, but it is not encrypted.
    CHUNKCRYPTO_NOT_ENCRYPTED        = 20019
    
    ##(int) Error Codes: Success code.
    HTTP_OK                          = 0
    ##(int) Error Codes: A general error occurred, but its specific problem is not represented with its own code.
    HTTP_ERROR                       = 13001
    ##(int) Error Codes: An unknown and unexpected error occurred.
    HTTP_UNKNOWN                     = 13002
    ##(int) Error Codes: A memory allocation failed.
    ##      This can happen if there is not a sufficient amount of memory available to perform an operation.
    HTTP_NOMEMORY                    = 13003
    ##(int) Error Codes: An expected and required value was not found.
    ##      This is typically emitted from functions that are responsible for parsing / deserializing data.
    HTTP_MISSINGVALUE                = 13004
    ##(int) Error Codes: A value was found that is invalid.
    ##      For example, a string value was expected, but it was actually an integer.  This is typically
    ##      emitted from functions that are responsible for parsing / deserializing data.
    HTTP_INVALIDVALUE                = 13005
    ##(int) Error Codes: A value of None pointer was passed to a function that does not accept None.
    HTTP_NULL_INPUT                  = 13006
    ##(int) Error Codes: An invalid input value was encountered.
    ##      An input value was found that is invalid.  For example, a buffer length input was equal to zero.
    HTTP_BAD_INPUT                   = 13007
    ##(int) Error Codes: An HTTP operation has timed out.
    ##      This happens when a blocking HTTP function has been used with a maximum wait time, and that time has expired.
    HTTP_TIMEOUT                     = 13008
    ##(int) Error Codes: The parsing of some serialized data failed.
    ##      This typically happens if an HTTP message is malformed, truncated, or otherwise unable to be parsed.
    HTTP_PARSEFAILED                 = 13009
    ##(int) Error Codes: A file failed to open.
    ##      This normally happens because the file path provided does not exist or it is not accessible due to lack of permission.
    HTTP_OPENFILE                    = 13010
    ##(int) Error Codes: An HTTP method was found that is not recognized.
    ##      This happens when parsing an HTTP request and discovering an unknown / unsupported HTTP method.
    ##      The supported HTTP methods are GET, POST, PUT, HEAD, and DELETE.
    HTTP_METHOD_UNKNOWN              = 13011

