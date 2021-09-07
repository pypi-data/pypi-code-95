"""!The client-side library for all key vault services
"""

import ionicsdk._private as _private
from ionicsdk.common import *
from ionicsdk.exceptions import *
from ionicsdk.errors import *
from collections import defaultdict
import sys

def KeyVaultGetCurrentServerTimeUtcSeconds():
    """!Retrieve the current server time in seconds
    
    @return
        (int) Server time in seconds
    """
    return _private.cLib.ionic_keyvault_getcurrent_server_time_utc_seconds()

class KeyVaultKeyRecord(object):
    """!@details
        Class pass key information in and out of the Key Vaults.
    """
    ##(int) Key Vault Record State Enumeration - invalid
    ISKR_INVALID = 0
    ##(int) Key Vault Record State Enumeration - recently added, not yet stored
    ISKR_ADDED = 1
    ##(int) Key Vault Record State Enumeration - recently removed, not yet remove from the store
    ISKR_REMOVED = 2
    ##(int) Key Vault Record State Enumeration - recently updated, changes not yet stored
    ISKR_UPDATED = 3
    ##(int) Key Vault Record State Enumeration - no changes since last stored in the vault
    ISKR_STORED = 4

    def __init__(self, keyid, keyBytes, attributes, mutableAttributes, obligations, issuedServerTimeUtcSeconds, expirationServerTimeUtcSeconds, state):
        """!Constructs key vault record from passed in arguments.
            
        @param
            keyid (string) The Key ID or identifying tag
        @param
            keyBytes (bytearray) The Key data
        @param
            attributes (dict of lists) - Protection key attributes.
        @param
            mutableAttributes (dict of lists) - mutable protection key attributes.
        @param
            obligations (dict of lists) - Used to store protection key policy obligations.
        @param
            issuedServerTimeUtcSeconds (int) The time at which this key was issued, measured in UTC seconds according to server time.
        @param
            expirationServerTimeUtcSeconds (int) nExpirationServerTimeUtcSeconds The time at which this key expires,
                                                measured in UTC seconds according to server time.
        @param
            state (Enum) This is ONLY set on KeyVaultCustom callbacks and is otherwise unused.  See KeyVaultCustom class for details. 
        """

        ##(string) The Key ID or identifying tag
        self.keyid = keyid
        ##(bytearray) The Key data
        self.keyBytes = keyBytes
        ##(dict of lists) - Protection key attributes.  For example, when creating key(s), key attributes
        ##      (both immutable and mutable) can be provided for the keys being created. The attributes used (if any)
        ##      when creating key(s) will also be given back when retrieving the keys.
        self.attributes = attributes
        ##(dict of lists) - mutable protection key attributes.  For example, when creating key(s),
        ##      key attributes (both immutable and mutable) can be provided for the keys being created. The attributes
        ##      used (if any) when creating key(s) will also be given back when retrieving the keys.
        self.mutableAttributes = mutableAttributes
        ##(dict of lists) - Used to store protection key policy obligations.  For example, when retrieving
        ##      a key with GetKey(), policy obligations associated with the retrieved key will be represented here.
        self.obligations = obligations
        ##(int) The time at which this key was issued, measured in UTC seconds according to server time.
        self.issuedServerTimeUtcSeconds = issuedServerTimeUtcSeconds
        ##(int) nExpirationServerTimeUtcSeconds The time at which this key expires,
        ##      measured in UTC seconds according to server time.
        self.expirationServerTimeUtcSeconds = expirationServerTimeUtcSeconds
        ##(Enum) This is ONLY set on KeyVaultCustom callbacks and is otherwise unused.  See KeyVaultCustom class for details.
        self.state = state

    @staticmethod
    def _marshalFromC(cKeyVaultKeyRecord):
        if cKeyVaultKeyRecord is None:
            return None

        pyResult = KeyVaultKeyRecord(
            _private.CMarshalUtil.stringFromC(cKeyVaultKeyRecord.pszKeyId),
            _private.CMarshalUtil.bytesFromC(cKeyVaultKeyRecord.keyBytes),
            KeyAttributesDict._marshalFromC(cKeyVaultKeyRecord.pAttributesMap),
            KeyAttributesDict._marshalFromC(cKeyVaultKeyRecord.pMutableAttributesMap),
            KeyObligationsDict._marshalFromC(cKeyVaultKeyRecord.pObligationsMap),
            cKeyVaultKeyRecord.lIssuedServerTimeUtcSeconds,
            cKeyVaultKeyRecord.lExpirationServerTimeUtcSeconds,
            cKeyVaultKeyRecord.eState)

        return pyResult

    @staticmethod
    def _marshalToC(pyKeyVaultKey):
        if pyKeyVaultKey is None:
            return None
        
        cKey = _private.CGetKeyVaultRecord(_private.CMarshalUtil.stringToC(pyKeyVaultKey.keyid),
                                 _private.CMarshalUtil.bytesToC(pyKeyVaultKey.keyBytes),
                                 KeyAttributesDict._marshalToC(pyKeyVaultKey.attributes, False),
                                 KeyAttributesDict._marshalToC(pyKeyVaultKey.mutableAttributes, False),
                                 KeyObligationsDict._marshalToC(pyKeyVaultKey.obligations, False),
                                 pyKeyVaultKey.issuedServerTimeUtcSeconds,
                                 pyKeyVaultKey.expirationServerTimeUtcSeconds,
                                 pyKeyVaultKey.state)
        return cKey

    def __repr__(self):
        return '<KeyVaultKeyRecord for "{0}">'.format(self.keyid)

class KeyVaultKeyRecordList(list):
    """!List of KeyVaultKeyRecord with convenience functions for
        searching by key ID.
    """

    def __repr__(self):
        return '<KeyVaultKeyRecordList ' + super(KeyVaultKeyRecordList,self).__repr__() + '>'

    def findkeyid(self, keyid):
        """!Find a key in this list by keyid.
            
        @param
            keyid (string) The key id to search for
        @return
            The key or None if it was not found in the list.
        """
        for result in self:
            if result.keyid == keyid:
                return result
        return None

    @staticmethod
    def _marshalFromC(cKeyVaultKeyRecordList):
        if cKeyVaultKeyRecordList is None:
            return None

        pyKeyVaultKeyRecordList = KeyVaultKeyRecordList()
        for i in range(cKeyVaultKeyRecordList.nSize):
            pyKeyVaultKeyRecordList.append(KeyVaultKeyRecord._marshalFromC(cKeyVaultKeyRecordList.ppKeyArray[i].contents))
        return pyKeyVaultKeyRecordList

    @staticmethod
    def _marshalToC(pyKeyVaultKeyRecordList):
        if pyKeyVaultKeyRecordList is None:
            return None
                
        cKeyVaultKeyRecordList = _private.CGetKeyVaultRecordList((_private.POINTER(_private.CGetKeyVaultRecord) *len(pyKeyVaultKeyRecordList))(), len(pyKeyVaultKeyRecordList))
            
        for i in range(len(pyKeyVaultKeyRecordList)):
            cKeyVaultKeyRecordList.ppKeyArray[i] = _private.pointer(KeyVaultKeyRecord._marshalToC(pyKeyVaultKeyRecordList[i]))
                
        return cKeyVaultKeyRecordList


class KeyVault(object):
    """!KeyVault service object.  This serves as the base class for the Mac, iOS, Windows and Custom version.
        All the basic functionality of managing keys is here.
        
    Error Codes:    
    - ISKEYVAULT_OK - Success code.
    - ISKEYVAULT_ERROR_BASE - error code range base.
    - ISKEYVAULT_ERROR - A general error occurred, but its specific problem is not represented with its own code.
    - ISKEYVAULT_UNKNOWN - An unknown and unexpected error occurred.
    - ISKEYVAULT_NOMEMORY - A memory allocation failed. This can happen if there is not a sufficient amount of
            memory available to perform an operation.
    - ISKEYVAULT_MISSINGVALUE - An expected and required value was not found. This is typically emitted from
            functions that are responsible for parsing / deserializing data.
    - ISKEYVAULT_INVALIDVALUE - A value was found that is invalid. For example, a string value was expected, but
            it was actually an integer.  This is typically emitted from functions that are responsible for parsing
            deserializing data.
    - ISKEYVAULT_KEY_NOT_FOUND - A key was not found. This happens when attempting to access a key that does not
            exist, for example when trying to retrieve via GetKey(..) or update a key via SetKey(..).
    - ISKEYVAULT_KEY_UPDATE_IGNORED - A key update request was ignored. This happens when attempting to update a
            key via SetKey(), and the provided key is not newer than the key which already exists in the vault.
            This is not an error, per se, but it is informing the caller that the requested update is not needed, 
            and as such is ignored. The determination is made by comparing key issuance UTC time
            (KeyVaultKeyRecord.issuedServerTimeUtcSeconds).
    - ISKEYVAULT_OPENFILE - A file failed to open. This normally happens because the file path provided does not
            exist or it is not accessible due to lack of permission.
    - ISKEYVAULT_EOF - The end of a file was found before it was expected. This normally happens if the file has
            been truncated or is zero length.
    - ISKEYVAULT_NOHEADER - A file header could not be found where it was expected. This normally happens when
            trying to decrypt a file that is not encrypted, or the encrypted file has been corrupted.
    - ISKEYVAULT_PARSEFAILED - The parsing of some serialized data failed. This typically happens if a file or
            block of data is corrupted or of an unexpected format.
    - ISKEYVAULT_HEADER_MISMATCH - A key vault file header has values which were not expected. This typically
            happens when a key vault attempts to open a file that was saved by a different key vault type.  For
            example, if a Windows DPAPI key vault object attempts to open a file that was saved by a different
            key vault type (e.g. Apple Keychain key vault).
    - ISKEYVAULT_LOAD_NOT_NEEDED - A key vault load operation was skipped because it was not needed. This happens
            when a load operation is requested on a key vault, but the vault skipped the operation because it
            determined that the underlying storage data has not changed since the previous load operation.  A 
            key vault may do this in order to optimize execution time by avoiding costly loads from disk when
            possible.
    - ISKEYVAULT_CREATE_PATH - A key vault save operation could not create the required file path. This happens
            when a save operation is requested on a key vault, but the vault is unable to create the necessary
            folder path to store the file. For example, if the destination file path is /a/b/c/vault.dat, and
            the folder /a/b/c does not exist (or some part of it), then the key vault attempts to create the path.
            If the path cannot be created, then ISKEYVAULT_CREATE_PATH is returned.
    - ISKEYVAULT_INVALID_KEY - A key is invalid in some way (key ID, key bytes, etc). This may happen if a key
            was found to be invalid. For example, if the key is the wrong size (any size other than 32 bytes),
            the key ID string is empty or contains invalid characters, etc.
    - ISKEYVAULT_RESOURCE_NOT_FOUND - A resource was not found. This happens when attempting to access a resource
            that does not exist.
    - ISKEYVAULT_FILE_VERSION - A key vault file load operation failed due to unsupported file version. This
            happens when a key vault attempts to load a file from disk, but the version of that file is not
            supported. This may happen when an older version of the SDK is used to load a file that was saved by
            a newer version of the SDK.
    """
    ## Key Vault Error Codes - Success code
    ISKEYVAULT_OK = 0
    ## Key Vault Error Codes - error code range base
    ISKEYVAULT_ERROR_BASE = 16000
    ## Key Vault Error Codes - A general error occurred, but its specific problem is not represented with its own code.
    ISKEYVAULT_ERROR = 16001
    ## Key Vault Error Codes - An unknown and unexpected error occurred.
    ISKEYVAULT_UNKNOWN = 16002
    ## Key Vault Error Codes - A memory allocation failed.
    ##      This can happen if there is not a sufficient amount of memory available to perform an operation.
    ISKEYVAULT_NOMEMORY = 16003
    ## Key Vault Error Codes - An expected and required value was not found.
    ##      This is typically emitted from functions that are responsible for parsing / deserializing data.
    ISKEYVAULT_MISSINGVALUE = 16004
    ## Key Vault Error Codes - A value was found that is invalid.
    #       For example, a string value was expected, but it was actually an integer.
    ##      This is typically emitted from functions that are responsible for parsing deserializing data.
    ISKEYVAULT_INVALIDVALUE = 16005
    ## Key Vault Error Codes - A key was not found.
    ##      This happens when attempting to access a key that does not
    ##          exist, for example when trying to retrieve via GetKey(..) or update a key via SetKey(..).
    ISKEYVAULT_KEY_NOT_FOUND = 16006
    ## Key Vault Error Codes - A key update request was ignored.
    ##      This happens when attempting to update a key via SetKey(), and the provided key is not newer than the key
    ##      which already exists in the vault. This is not an error, per se, but it is informing the caller that the
    ##      requested update is not needed, and as such is ignored. The determination is made by comparing key issuance
    ##      UTC time (KeyVaultKeyRecord.issuedServerTimeUtcSeconds).
    ISKEYVAULT_KEY_UPDATE_IGNORED = 16007
    ## Key Vault Error Codes - A file failed to open.
    ##      This normally happens because the file path provided does not exist or it is not accessible due to lack
    ##          of permission.
    ISKEYVAULT_OPENFILE = 16008
    ## Key Vault Error Codes - The end of a file was found before it was expected.
    ##      This normally happens if the file has been truncated or is zero length.
    ISKEYVAULT_EOF = 16009
    ## Key Vault Error Codes - A file header could not be found where it was expected.
    ##      This normally happens when trying to decrypt a file that is not encrypted, or the encrypted file has been corrupted.
    ISKEYVAULT_NOHEADER = 16010
    ## Key Vault Error Codes - The parsing of some serialized data failed.
    ##      This typically happens if a file or block of data is corrupted or of an unexpected format.
    ISKEYVAULT_PARSEFAILED = 16011
    ## Key Vault Error Codes - A key vault file header has values which were not expected.
    ##      This typically happens when a key vault attempts to open a file that was saved by a different key vault type.
    ##      For example, if a Windows DPAPI key vault object attempts to open a file that was saved by a different
    ##          key vault type (e.g. Apple Keychain key vault).
    ISKEYVAULT_HEADER_MISMATCH = 16012
    ## Key Vault Error Codes - A key vault load operation was skipped because it was not needed.
    ##      This happens when a load operation is requested on a key vault, but the vault skipped the operation because it
    ##      determined that the underlying storage data has not changed since the previous load operation.  A
    ##      key vault may do this in order to optimize execution time by avoiding costly loads from disk when possible.
    ISKEYVAULT_LOAD_NOT_NEEDED = 16013
    ## Key Vault Error Codes - A key vault save operation could not create the required file path.
    ##      This happens when a save operation is requested on a key vault, but the vault is unable to create the necessary
    ##      folder path to store the file. For example, if the destination file path is /a/b/c/vault.dat, and
    ##      the folder /a/b/c does not exist (or some part of it), then the key vault attempts to create the path.
    ##      If the path cannot be created, then ISKEYVAULT_CREATE_PATH is returned.
    ISKEYVAULT_CREATE_PATH = 16014
    ## Key Vault Error Codes - A key is invalid in some way (key ID, key bytes, etc).
    ##      This may happen if a key was found to be invalid. For example, if the key is the wrong size (any size other
    ##          than 32 bytes), the key ID string is empty or contains invalid characters, etc.
    ISKEYVAULT_INVALID_KEY = 16015
    ## Key Vault Error Codes - A resource was not found.
    ##      This happens when attempting to access a resource that does not exist.
    ISKEYVAULT_RESOURCE_NOT_FOUND = 16016
    ## Key Vault Error Codes - A key vault file load operation failed due to unsupported file version.
    ##      This happens when a key vault attempts to load a file from disk, but the version of that file is not
    ##      supported. This may happen when an older version of the SDK is used to load a file that was saved by
    ##      a newer version of the SDK.
    ISKEYVAULT_FILE_VERSION = 16017
    
    def __init__(self):
        """!Constructs a default key vault.
        """
        self._cAgentHandle = None

    def SetKey(self, keyVaultKeyRecord, addIfNotFound):
        """!@details
            Add or update a key into the key vault.

            Attempts to update the provided key into the key vault and returns ISKEYVAULT_OK on success.

            If the key does not exist and addIfNotFound is set to true, then the key will be added to the vault.

            If the key does not exist and addIfNotFound is set to false, then ISKEYVAULT_KEY_NOT_FOUND will be returned.

            If the key is found, but its 'issued' time (KeyVaultKeyRecord.issuedServerTimeUtcSeconds) is 
            unchanged, then the key will NOT be updated and ISKEYVAULT_KEY_UPDATE_IGNORED will be returned.

            If some aspect of the key itself is invalid, such as the key ID being empty, the key data not being 
            32 bytes in size, etc. then ISKEYVAULT_INVALID_KEY will be returned.

        @param
            keyVaultKeyRecord - The data protection key.
        @param
            addIfNotFound - Determines if the key should be added in the case that it is not found.
            
        @return
            Returns one of the return codes listed above.
        """
        cKeyVaultKey = KeyVaultKeyRecord._marshalToC(keyVaultKeyRecord)
        return _private.cLib.ionic_keyvault_setkey(self._cAgentHandle, cKeyVaultKey, addIfNotFound)

    def GetKey(self, keyid):
        """!Get a single key from the key vault. Searches for a key identified by keyId.  On success, key
            will be returned. If the key is not found, then None will be returned.

        @param
            keyid - The data protection key ID (also known as the key tag).
            
        @return
            keyVaultKeyRecord - Output key object that is populated with the retrieved key or None.
        """
        cKeyid = _private.CMarshalUtil.stringToC(keyid)
        cKeyRec = _private.OWNED_POINTER(_private.CGetKeyVaultRecord)()
        
        ret = _private.cLib.ionic_keyvault_getkey(self._cAgentHandle, cKeyid, cKeyRec)
        if ret == KeyVault.ISKEYVAULT_OK:
            # marshal C output to Python
            return KeyVaultKeyRecord._marshalFromC(cKeyRec.contents)
        
        return None

    def GetKeys(self, keyids):
        """!Get multiple keys from the key vault. Searches for each key identifier in the keyids list.  On
            success, a list of keys found will be returned. If no key is not found, then an empty list will
            be returned.
            
        @param
            keyids -  A list of data protection key ID's (also known as the key tag).

        @return
            (keyVaultKeyRecordList) Output key object list that is populated with the found and retrieved
                keys.  If nothing is found, the list will be empty.
        """
        nKeyCount = len(keyids)
        cKeyids = _private.CMarshalUtil.stringArrayToC(keyids)
        cKeyRecArray = _private.OWNED_POINTER(_private.CGetKeyVaultRecordList)()

        _private.cLib.ionic_keyvault_getkeys(self._cAgentHandle, cKeyids, nKeyCount, cKeyRecArray)

        return KeyVaultKeyRecordList._marshalFromC(cKeyRecArray.contents)

    def GetAllKeyIds(self):
        """!Get the list of all key IDs in the key vault.

        @return
            A list of string keyids which represent all the data protection keys that are contained in the 
                key vault.
        """
        cKeyIdsOut = _private.OWNED_POINTER(POINTER(c_char_p))
        cKeyCountOut = POINTER(c_int)

        _private.cLib.ionic_keyvault_getallkey_ids(self._cAgentHandle, cKeyIdsOut, cKeyCountOut)

        return _private.CMarshalUtil.stringArrayFromC(cKeyIdsOut.contents, cKeyCountOut.contents)

    def GetAllKeys(self):
        """!Get the list of all key objects in the key vault.
            
        @return
            KeyVaultKeyReordList of all the data protection keys in the key vault.
        """
        cKeyRecArray = _private.OWNED_POINTER(_private.CGetKeyVaultRecordList)()

        _private.cLib.ionic_keyvault_getallkeys(self._cAgentHandle, cKeyRecArray)

        return KeyVaultKeyRecordList._marshalFromC(cKeyRecArray.contents)

    def GetKeyCount(self):
        """!Get the number of keys in the key vault.
            
        @return
            The number of keys in the key vault.
        """
        return _private.cLib.ionic_keyvault_getkey_count(self._cAgentHandle)

    def HasKey(self, keyid):
        """!Determine if a key exists in the key vault.
            
        @param
            keyid - (string) The data protection key ID to look for.
            
        @return
            True if a key with the specified ID exists.  Otherwise, returns False.
        """
        cKeyid = _private.CMarshalUtil.stringToC(keyid)

        return _private.cLib.ionic_keyvault_haskey(self._cAgentHandle, cKeyid)

    def RemoveKey(self, keyid):
        """!Remove a single key from the key vault.
            
        @param
            keyid - (string) The key object to remove.
            
        @return
            ISKEYVAULT_OK on success. Otherwise, returns ISKEYVAULT_KEY_NOT_FOUND if the specified 
                key was not found.
        """
        cKeyid = _private.CMarshalUtil.stringToC(keyid)

        return _private.cLib.ionic_keyvault_removekey_by_id(self._cAgentHandle, cKeyid)

    def RemoveKeys(self, keyids):
        """!Remove one or more keys from the key vault.
            
        @param
            keyids - (list of strings) The set of data protection key IDs to remove.
            
        @return
            A list of the string ids that were not found.  Can be None.
        """
        nKeyCount = len(keyids)
        cKeyids = _private.CMarshalUtil.stringArrayToC(keyids)

        cKeyIdsOut = _private.OWNED_POINTER(POINTER(c_char_p))
        cKeyCountOut = POINTER(c_int)

        _private.cLib.ionic_keyvault_removekeys(self._cAgentHandle, cKeyids, nKeyCount, cKeyIdsOut, cKeyCountOut)

        return _private.CMarshalUtil.stringArrayFromC(cKeyIdsOut.contents, cKeyCountOut.contents)

    def ClearAllKeys(self):
        """!Remove all keys from the key vault.
            
        @return
            ISKEYVAULT_OK; there is no error condition for this function.
        """
        return _private.cLib.ionic_keyvault_clearallkeys(self._cAgentHandle)

    def ExpireKeys(self):
        """!Remove all keys which have expired.

        @return
            A list of the string ids that were removed.  Can be None.
        """
        cKeyIdsOut = _private.OWNED_POINTER(POINTER(c_char_p))
        cKeyCountOut = POINTER(c_int)
        
        _private.cLib.ionic_keyvault_expirekeys(self._cAgentHandle, cKeyIdsOut, cKeyCountOut)
        
        return _private.CMarshalUtil.stringArrayFromC(cKeyIdsOut.contents, cKeyCountOut.contents)

    def Sync(self):
        """!@details
            Perform synchronization to permanent storage.
            
            This function first loads any detected changes to the key vault from permanent storage, then 
            merges those changes (if any) with the key vault in memory, and finally saves the merged changes
            to permanent storage.

            This synchronization is both process-safe and thread-safe to ensure that no changes are lost, and 
            more importantly that the permanent storage is never corrupted.
            
            See KeyVaultCustom for details on how to customize this process.
            
        @return
            Returns ISKEYVAULT_OK on success.  Otherwise, returns an error code.
        """
        return _private.cLib.ionic_keyvault_sync(self._cAgentHandle)

    def HasChanges(self):
        """!Determine if there are any changes to the key vault in memory that necessitate a sync().
            
        @return
            True if changes have been made to the key vault in memory that have not yet been put into 
            permanent storage via Sync(). For example, if a key is added, update, or removed, then a call
            to Sync() is needed in order to reflect the relevant change(s) to permanent storage.
        """
        return _private.cLib.ionic_keyvault_haschanges(self._cAgentHandle)

    def CleanVaultStore(self):
        """!Deletes any long term storage used by the particular key vault. In the general
            case, this mean deleting a file. Useful when the Key Vault becomes corrupted.
            
            @return
                None
        """
        return _private.cLib.ionic_keyvault_clean_vault_store(self._cAgentHandle)


class KeyVaultCustom(KeyVault):
    """!Key Vault Class that allows for the creation of a completely custom vault.  The user has two options in this 
    regard.  
    
    - 1. Override the SyncKeys method and call 'EnableSyncCallbacks' at some point in the initialization.
        Sync() is called in normal operation of the key vault when changes should be moved into long term storage.
        With KeyVaultCustom, this call generates a call to the Python method, SyncKeys.  SyncKeys is passed a list 
        of the current keys which will have their state property set.  Keys that have state other than STORED, should
        be updated in long term storage.  After which, use UpdateKeyState or DeleteKey method calls to either update
        the state of the key to STORED, or to permanently remove a key which was marked for removal.
        
    - 2. Override the 'SaveAllKeys' and 'LoadAllKeys' methods and call 'EnableFileLoadSaveCallbacks' at some point
        during the initialization.  Sync() is called in normal operation of the key vault when changes should be
        moved into long term storage.  In this case,  The load and save Python methods are called as needed.  On 
        the Python side, simply implement overrides and move the entire set of keys in or out of long term
        storage when called.
        
    Constructor takes an ID (string), Label (string), and Security Level (int) argument
    
    """
    def __init__(self, vaultId, vaultLabel, vaultSecLev):
        """!Constructs the base part of a custom key vault from passed in arguments.
            
        @param
            vaultId (string) The vault unique type ID.
        @param
            vaultLabel (string) The human readable vault label.
        @param
            vaultSecLev (int) - An arbitrary integer security level - comparable against other key vaults.
        """
        
        cVaultId = _private.CMarshalUtil.stringToC(vaultId)
        cVaultLabel = _private.CMarshalUtil.stringToC(vaultLabel)
        self._cAgentHandle = _private.cLib.ionic_keyvault_create_custom_vault(cVaultId, cVaultLabel, vaultSecLev)
        
        # To hold a ref cnt across 'C' callbacks.
        self._loadedKeys = {}
        self._syncCallback = None
        self._loadCallback = None
        self._saveCallback = None
        self._releaseCallback = None

    def EnableSyncCallbacks(self):
        """!Call this to enable callbacks to the SyncKeys method.  If this is called from a class implementation
            without a SyncKeys override, then the base class will raise an exception on the first call to Sync()

        @return
            None
        """
        def cb_sync(_cAgentHandle, cKeyVaultKeyRecordList):
            try:
                keyVaultKeys = KeyVaultKeyRecordList._marshalFromC(cKeyVaultKeyRecordList.contents)
                return self.SyncKeys(keyVaultKeys)
            except AttributeError:
                return KeyVault.ISKEYVAULT_UNKNOWN

            return KeyVault.ISKEYVAULT_OK
        self._syncCallback = _private.KeyVaultCustomCallback_sync(cb_sync)
        _private.cLib.ionic_keyvaultcustom_set_sync_function(self._cAgentHandle, self._syncCallback)
    
    def EnableFileLoadSaveCallbacks(self):
        """!Call this to enable callbacks to the SaveAllKeys and LoadAllKeys methods.  If this is called from a class
            implementation without both methods overrided, then the base class will raise an exception on the first
            call to Sync()

        @return
            None
        """
        def cb_save(_cAgentHandle, cKeyVaultKeyRecordList):
            try:
                keyVaultKeys = KeyVaultKeyRecordList._marshalFromC(cKeyVaultKeyRecordList.contents)
                return self.SaveAllKeys(keyVaultKeys)
            except AttributeError:
                return KeyVault.ISKEYVAULT_UNKNOWN

            return KeyVault.ISKEYVAULT_OK
        
        def cb_load(_cAgentHandle, pcKeyVaultKeyRecordList):
            pyLoadedKeys = self.LoadAllKeys()
            if pyLoadedKeys is None:
                return KeyVault.ISKEYVAULT_RESOURCE_NOT_FOUND
            
            cLoadedKeys = KeyVaultKeyRecordList._marshalToC(pyLoadedKeys)
            pcKeyVaultKeyRecordList[0] = _private.pointer(cLoadedKeys)
                
            # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
            ref = _private.cast(pcKeyVaultKeyRecordList[0],_private.c_void_p)
            self._loadedKeys[ref.value] = [pyLoadedKeys, cLoadedKeys, ref]

            return KeyVault.ISKEYVAULT_OK
        
        def cb_release(cKeyVaultKeyRecordList):
            ref = _private.cast(cKeyVaultKeyRecordList,_private.c_void_p)
            del self._loadedKeys[ref.value]

        self._saveCallback = _private.KeyVaultCustomCallback_save(cb_save)
        self._loadCallback = _private.KeyVaultCustomCallback_load(cb_load)
        self._releaseCallback = _private.KeyVaultCustomCallback_release(cb_release)

        _private.cLib.ionic_keyvaultcustom_set_file_functions(self._cAgentHandle, self._saveCallback, self._loadCallback, self._releaseCallback)
    
    def GetKeyState(self, keyid):
        """!Outside of the context of a SyncKeys() callback, the Python copy of the vault keys will not have valid
            state values.  Use this function to retrieve the current state.  See class KeyVaultKeyRecord for 
            valid values.
        @param
            keyid (string) The Key ID or identifying tag
        @return
            (KeyVaultKeyRecord enum) Current key state
        """
        cKeyid = _private.CMarshalUtil.stringToC(keyid)
        return _private.cLib.ionic_keyvaultcustom_getkeystate(self._cAgentHandle, cKeyid)
    
    def UpdateKeyState(self, keyid, newState):
        """!Inside the context of a SyncKeys() callback, the code should either update the states ISKR_UPDATED and ISKR_ADDED to ISKR_STORED, or delete keys with the status of ISKR_REMOVED.  This function updates the
            state.  It is insufficient to simply change the state on the Python object as it is a local cop of the 
            actual key data stored in the native code.
        @param
            keyid (string) The Key ID or identifying tag
        @param
            newState (string) The new state to set on the key
        @return
            (int) ISKEYVAULT_OK on success or ISKEYVAULT_INVALIDVALUE if this instance is corrupt somehow
        """
        cKeyid = _private.CMarshalUtil.stringToC(keyid)
        return _private.cLib.ionic_keyvaultcustom_updatekeystate(self._cAgentHandle, cKeyid, newState)
    
    def DeleteKey(self, keyid):
        """!Inside the context of a SyncKeys() callback, the code should either update the states ISKR_UPDATED and ISKR_ADDED to ISKR_STORED, or delete keys with the status of ISKR_REMOVED.  This function permanently
            deletes a key from the native code storage.
        @param
            keyid (string) The Key ID or identifying tag
        @return
            (int) ISKEYVAULT_OK on success or ISKEYVAULT_INVALIDVALUE if this instance is corrupt somehow
        """
        cKeyid = _private.CMarshalUtil.stringToC(keyid)
        return _private.cLib.ionic_keyvaultcustom_deletekey(self._cAgentHandle, cKeyid)
  
    def SyncKeys(self, keyVaultKeys):
        """!@details
            Callback enabled by EnableSyncCallbacks().  You must sub class and override this method to use this.
        @param
            keyVaultKeys - (KeyVaultKeyRecordList)  A list of KeyVaultKeyRecords with valid state.  Use the state
            to determine new or updated keys and keys marked for removal.  This function should move the key vault
            data into long term storage and then update keys to the stored state or permanently remove them if so
            marked.

        @return
            (int) ISKEYVAULT_OK on success or some other meaningful error code
        """
        raise Exception("If SyncEnabled, you must sub-class and implement this method!")

    def SaveAllKeys(self, keyVaultKeys):
        """!Callback enabled by EnableFileLoadSaveCallbacks().  You must sub class and override this method to use
            this.
        @param
            keyVaultKeys - (KeyVaultKeyRecordList)  A list of KeyVaultKeyRecords with valid state.
            
            Function should move the key data to long term storage.  The native implementation of Sync() will update
            the key vault key state in this case.
            
        @return
            (int) ISKEYVAULT_OK on success or some other meaningful error code
        """
        raise Exception("If FileEnabled, you must sub-class and implement this method!")

    def LoadAllKeys(self):
        """!Callback enabled by EnableFileLoadSaveCallbacks().  You must sub class and override this method to use
            this.
            
            Function should retrieve the key data from long term storage and return the list of keys as a
            KeyVaultKeyRecordList.  The native implementation of Sync() will update the key vault key state
            in this case.

        @return
            (KeyVaultKeyRecordList) A list of the keys loaded
        """
        raise Exception("If FileEnabled, you must sub-class and implement this method!")

    def CleanVaultStore(self):
        """!Optional function used to clean up a corrupt key storage file. There is no
            need to implement this via any callback as it is not at present called directly
            by the wrapped SDK code anyway. It should be implemented so that a potentially
            corrupt key storage can be repaired at the application level.
            
            @return
                None
        """
        raise Exception("If FileEnabled, you should sub-class and implement this method!")


class KeyVaultAppleKeyChain(KeyVault):
    """!@details
        Constructor takes protection key and protection auth data as parms.  You may pass 
        None to these and set them with the setters later.  However, the vault is not functional
        without at least these two parms.  Everything else will work with defaults.
        """
    
    def __init__(self, protectionKeybytes, protectionAuthbytes):
        """!Constructs the an Apple style key vault from passed in arguments.
            
        @param
            protectionKeybytes (bytes) The AES GCM key to use for protecting the key vault data.
        @param
            protectionAuthbytes (bytes) The AES GCM auth data to use when protecting the key vault data.
        """
        
        cKeybytes = _private.CMarshalUtil.bytesToC(protectionKeybytes)
        cAuthbytes = _private.CMarshalUtil.bytesToC(protectionAuthbytes)
        self._cAgentHandle = _private.cLib.ionic_keyvault_create_apple_keychain_vault(cKeybytes, cAuthbytes)
    
    @staticmethod
    def GetDefaultServiceName():
        """!Getter for the default Apple key chain Service Name

        @return
            (string) Hard coded default service name "com.ionicsecurity.client.sdk.keyvault.applekeychain"
        """
        cServiceName = _private.cLib.ionic_keyvault_apple_keychain_get_default_service_name()
        return _private.CMarshalUtil.stringFromC(cServiceName)
    
    @staticmethod
    def GetDefaultAccountName():
        """!Getter for the default Apple key chain Account Name

        @return
            (string) Hard coded default account name "Ionic Security"
        """
        cAccountName = _private.cLib.ionic_keyvault_apple_keychain_get_default_account_name()
        return _private.CMarshalUtil.stringFromC(cAccountName)

    def GetProtectionKey(self):
        """!Getter for the AES GCM key to use for protecting the key vault data

        @return
            (bytearray) The AES GCM key
        """
        cKeybytes = _private.cLib.ionic_keyvault_apple_keychain_get_protection_key(self._cAgentHandle)
        return _private.CMarshalUtil.bytesFromC(cKeybytes)

    def GetProtectionAuthData(self):
        """!Getter for the AES GCM Additional Authenticated Data (AAD) to use for protecting the key vault data

        @return
            (bytearray) The AES GCM Additional Authenticated Data (AAD)
        """
        cAuthbytes = _private.cLib.ionic_keyvault_apple_keychain_get_protection_authdata(self._cAgentHandle)
        return _private.CMarshalUtil.bytesFromC(cAuthbytes)

    def GetServiceName(self):
        """!Getter for the Apple key chain Service Name

        @return
            (string) The current service name
        """
        cServiceNameOut = _private.cLib.ionic_keyvault_apple_keychain_get_service_name(self._cAgentHandle)
        return _private.CMarshalUtil.stringFromC(cServiceNameOut)
    
    def GetAccountName(self):
        """!Getter for the Apple key chain Account Name

        @return
            (string) The current account name
        """
        cAccountNameOut = _private.cLib.ionic_keyvault_apple_keychain_get_account_name(self._cAgentHandle)
        return _private.CMarshalUtil.stringFromC(cAccountNameOut)

    def GetAccessGroup(self):
        """!Getter for the Apple key chain access group (iOS only)  Can be None.

        @return
            (string) The current access group
        """
        cAccessGroup = _private.cLib.ionic_keyvault_apple_keychain_get_access_group(self._cAgentHandle)
        return _private.CMarshalUtil.stringFromC(cAccessGroup)

    def SetProtectionKey(self, keybytes):
        """!Setter for the AES GCM key to use for protecting the key vault data
        @param
            keybytes (bytearray) The AES GCM key to use for protecting the key vault data
        @return
            None
        """
        cKeybytes = _private.CMarshalUtil.bytesToC(keybytes)
        _private.cLib.ionic_keyvault_apple_keychain_set_protection_key(self._cAgentHandle, cKeybytes)

    def SetProtectionAuthData(self, authbytes):
        """!Setter for the AES GCM Additional Authenticated Data (AAD) to use for protecting the key vault data
        @param
            authbytes (bytearray) The AES GCM AAD to use for protecting the key vault data
        @return
            None
        """
        cAuthbytes = _private.CMarshalUtil.bytesToC(authbytes)
        _private.cLib.ionic_keyvault_apple_keychain_set_protection_authdata(self._cAgentHandle, cAuthbytes)

    def SetServiceName(self, serviceName):
        """!Setter for the Apple key chain Service Name. Defaults to "com.ionicsecurity.client.sdk.keyvault.applekeychain"
        @param
            serviceName (string) The Apple key chain Service Name
        @return
            None
        """
        cServiceName = _private.CMarshalUtil.stringToC(serviceName)
        _private.cLib.ionic_keyvault_apple_keychain_set_service_name(self._cAgentHandle, cServiceName)
    
    def SetAccountName(self, accountName):
        """!Setter for the Apple key chain Account Name. Defaults to "Ionic Security"
        @param
            accountName (string) The Apple key chain Account Name
        @return
            None
        """
        cAccountName = _private.CMarshalUtil.stringToC(accountName)
        _private.cLib.ionic_keyvault_apple_keychain_set_account_name(self._cAgentHandle, cAccountName)

    def SetAccessGroup(self, accessGroup):
        """!Setter for the Apple key chain access group (iOS only).  Defaults to None.
        @param
            accessGroup (string) The Apple key chain access group (iOS only)
        @return
            None
        """
        cAccessGroup = _private.CMarshalUtil.stringToC(accessGroup)
        _private.cLib.ionic_keyvault_apple_keychain_set_access_group(self._cAgentHandle, cAccessGroup)


class KeyVaultMac(KeyVault):
    """!@details
        KeyVault service object for Mac, which uses an encrypted file using the Mac key chain to store keys

        ServiceName - The keychain service name to use for storing the key vault protection key.
            Defaults to "com.ionicsecurity.client.sdk.keyvault.mac"
            
        AccountName - The keychain account name to use for storing the key vault protection key.
            Defaults to "Ionic Security"
            
        FilePath - The file path and file name of the file to use to store the encrypted keys.
        
        Constructor takes a file name (with path).  Key vault is stored encrypted in this file.  You may
            use None for this argument, in which case, the key vault uses a default name, which is
            "<UserHome>/Library/Application Support/IonicSecurity/KeyVaults/KeyVaultMac.dat"
        """
    
    def __init__(self, filePath):
        """!Initializes the key vault with a file path, using defaults for other properties.
            
        @param
            filePath (string) The file path at which to read/write the key vault data.
        """
        
        cFilePathOut = _private.CMarshalUtil.stringToC(filePath)
        self._cAgentHandle = _private.cLib.ionic_keyvault_create_mac_vault(cFilePathOut)
    
    @staticmethod
    def GetDefaultServiceName():
        """!Getter for the default Apple key chain Service Name

        @return
            (string) Hard coded default service name "com.ionicsecurity.client.sdk.keyvault.mac"
        """
        cServiceName = _private.cLib.ionic_keyvault_mac_get_default_service_name()
        return _private.CMarshalUtil.stringFromC(cServiceName)
    
    @staticmethod
    def GetDefaultAccountName():
        """!Getter for the default Apple key chain Account Name

        @return
            (string) Hard coded default account name "Ionic Security"
        """
        cAccountName = _private.cLib.ionic_keyvault_mac_get_default_account_name()
        return _private.CMarshalUtil.stringFromC(cAccountName)

    @staticmethod
    def GetDefaultFilePath():
        """!Getter for the default filename and path used to stored the keys.

        @return
            (string) System user path plus hard coded default file name "KeyVaultMac.dat"
        """
        cFilePathOut = _private.cLib.ionic_keyvault_mac_get_default_file_path()
        return _private.CMarshalUtil.stringFromC(cFilePathOut)
    
    def GetServiceName(self):
        """!Getter for the Apple key chain Service Name

        @return
            (string) The current service name
        """
        cServiceNameOut = _private.cLib.ionic_keyvault_mac_get_service_name(self._cAgentHandle)
        return _private.CMarshalUtil.stringFromC(cServiceNameOut)

    def GetAccountName(self):
        """!Getter for the Apple key chain Account Name

        @return
            (string) The current account name
        """
        cAccountNameOut = _private.cLib.ionic_keyvault_mac_get_account_name(self._cAgentHandle)
        return _private.CMarshalUtil.stringFromC(cAccountNameOut)

    def GetFilePath(self):
        """!Getter for the filename and path used to store the Key Vault.

        @return
            (string) The current file path used to store the Key Vault
        """
        cFilePathOut = _private.cLib.ionic_keyvault_mac_get_file_path(self._cAgentHandle)
        return _private.CMarshalUtil.stringFromC(cFilePathOut)

    def SetServiceName(self, serviceName):
        """!Setter for the Apple key chain Service Name
        @param
            serviceName (string) The Apple key chain Service Name
        @return
            None
        """
        cServiceName = _private.CMarshalUtil.stringToC(serviceName)
        _private.cLib.ionic_keyvault_mac_set_service_name(self._cAgentHandle, cServiceName)

    def SetAccountName(self, accountName):
        """!Setter for the Apple key chain Account Name
        @param
            accountName (string) The Apple key chain Account Name
        @return
            None
        """
        cAccountName = _private.CMarshalUtil.stringToC(accountName)
        _private.cLib.ionic_keyvault_mac_set_account_name(self._cAgentHandle, cAccountName)

    def SetFilePath(self, filePath):
        """!Setter for the filename and path used to store the Key Vault.
        @param
            filePath (string) The filename and path used to store the Key Vault.
        @return
            None
        """
        cFilePath = _private.CMarshalUtil.stringToC(filePath)
        _private.cLib.ionic_keyvault_mac_set_file_path(self._cAgentHandle, cFilePath)


class KeyVaultWindowsDpApi(KeyVault):
    """!KeyVault service object for Windows, which uses an encrypted file using Windows DP (Data Protection) API

    FilePath - The file path and file name of the file to use to store the encrypted keys.

    Constructor takes a file name (with path).  Key vault is stored encrypted in this file.  You may
        use None for this argument, in which case, the key vault uses a default name, which is
        "<UserHome>\AppData\LocalLow\IonicSecurity\KeyVaults\KeyVaultDpapi.dat"
    """

    def __init__(self, filePath=None):
        """!Initializes the key vault with an optional file path, using defaults for other properties.
            
        @param
            filePath (string) The file path at which to read/write the key vault data.
        """
        
        if filePath is None:
            filePath = KeyVaultWindowsDpApi.GetDefaultFilePath()
        
        cFilePathOut = _private.CMarshalUtil.stringToC(filePath)
        self._cAgentHandle = _private.cLib.ionic_keyvault_create_windows_dpapi_vault(cFilePathOut)

    @staticmethod
    def GetDefaultFilePath():
        """!Getter for the default file path used for the key vault storage

        @return
            (string) System application data path plus hard coded default file name "KeyVaultDpapi.dat"
        """
        cFilePathOut = _private.cLib.ionic_keyvault_windows_dpapi_get_default_file_path()
        return _private.CMarshalUtil.stringFromC(cFilePathOut)

    def GetFilePath(self):
        """!Getter for the file path used for the key vault storage, if not previously set, returns the default path

        @return
            (string) The current file path used to store the Key Vault
        """
        cFilePathOut = _private.cLib.ionic_keyvault_windows_dpapi_get_file_path(self._cAgentHandle)
        return _private.CMarshalUtil.stringFromC(cFilePathOut)

    def SetFilePath(self, filePath):
        """!Setter for the file path used for the key vault storage
        @param
            filePath (string) The filename and path used to store the Key Vault.
        @return
            None
        """
        cFilePath = _private.CMarshalUtil.stringToC(filePath)
        _private.cLib.ionic_keyvault_windows_dpapi_set_file_path(self._cAgentHandle, cFilePath)


class KeyVaultLinux(KeyVault):
    """!KeyVault service object for Linux, which uses the Linux file permissions
    FilePath - The file path and file name of the file to use to store the keys.

    Constructor takes a file name (with path).  Key vault is stored in this file.  You may
        use None for this argument, in which case, the key vault uses a default name in your 
        user folder. "<UserHome>/.ionicsecurity/keyvault.dat" 
    """

    def __init__(self, filePath=None):
        """!Initializes the key vault with an optional file path, using defaults for other properties.
            
        @param
            filePath (string) The file path at which to read/write the key vault data.
        """
        
        if filePath is None:
            filePath = KeyVaultLinux.GetDefaultFilePath()
        
        cFilePathOut = _private.CMarshalUtil.stringToC(filePath)
        self._cAgentHandle = _private.cLib.ionic_keyvault_create_linux_vault(cFilePathOut)

    @staticmethod
    def GetDefaultFilePath():
        """!Getter for the default file path used for the key vault storage

        @return
            (string) System user path plus hard coded default filename "keyvault.dat"
        """
        cFilePathOut = _private.cLib.ionic_keyvault_linux_get_default_file_path()
        return _private.CMarshalUtil.stringFromC(cFilePathOut)

    def GetFilePath(self):
        """!Getter for the file path used for the key vault storage, if not previously set, returns the default path

        @return
            (string) The current file path used to store the Key Vault
        """
        cFilePathOut = _private.cLib.ionic_keyvault_linux_get_file_path(self._cAgentHandle)
        return _private.CMarshalUtil.stringFromC(cFilePathOut)

    def SetFilePath(self, filePath):
        """!Setter for the file path used for the key vault storage
        @param
            filePath (string) The filename and path used to store the Key Vault.
        @return
            None
        """
        cFilePath = _private.CMarshalUtil.stringToC(filePath)
        _private.cLib.ionic_keyvault_linux_set_file_path(self._cAgentHandle, cFilePath)
