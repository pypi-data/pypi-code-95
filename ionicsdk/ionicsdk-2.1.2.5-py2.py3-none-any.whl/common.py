"""!Common data structures used by IonicSDK modules
"""

import ionicsdk._private as _private
from ionicsdk.exceptions import *
from ionicsdk.errors import *
from ionicsdk.secretshare import *
from collections import defaultdict
import os, sys

class KeyData(object):
    """!Defines a data protection key as returned by Ionic.com."""
    def __init__(self, id, bytes, attributes=None, obligations=None, origin=None, mutableAttributes=None, mutableAttributesFromServer=None, attributesSigBase64FromServer=None, mutableAttributesSigBase64FromServer=None):
        """!Initializes the key object with provided inputs.

        @param
            id (string): The key ID (also known as the key tag).
        @param
            bytes (bytes): The raw key bytes.  It must be exactly 32 bytes in length.
        @param
            attributes (dict[string,list[string]], optional): The key attributes.
        @param
            obligations (KeyObligationsDict) The key obligations
        @param
            origin (string) The key origin, usually a URL
        @param
            mutableAttributes (KeyAttributesDict) The key mutable attributes
        @param
            mutableAttributesFromServer (KeyAttributesDict) The key mutable attributes from the server version
        @param
            attributesSigBase64FromServer (string) Base 64 encoded signature of the server's non-mutable attributes
        @param
            mutableAttributesSigBase64FromServer (string) Base 64 encoded signature of the server's mutable attributes
        """
        ##(string) The key ID
        self.id = id
        ##(bytes) The key
        self.bytes = bytes
        ##(KeyAttributesDict) The key non-mutable attributes
        self.attributes = attributes
        ##(KeyAttributesDict) The key mutable attributes
        self.mutableAttributes = mutableAttributes
        ##(KeyObligationsDict) The key obligations
        self.obligations = obligations
        ##(string) The key origin, usually a URL
        self.origin = origin
        ##(KeyAttributesDict) The key mutable attributes from the server version
        self.mutableAttributesFromServer = mutableAttributesFromServer
        ##(string) Base 64 encoded signature of the server's non-mutable attributes
        self.attributesSigBase64FromServer = attributesSigBase64FromServer
        ##(string) Base 64 encoded signature of the server's mutable attributes
        self.mutableAttributesSigBase64FromServer = mutableAttributesSigBase64FromServer

    def __repr__(self):
        return '<KeyData id="{0}">'.format(self.id)
    
    def Debug(self):
        """!Get a debugging string representation of the instance
        @return
            A string describing the instance
        """
        return "KeyData id: " + str(self.id) + "\nattributes: " + str(self.attributes) + "\nobligations: " + str(self.obligations) + "\norigin: " + str(self.origin) + "\nmutableAttributes: " + str(self.mutableAttributes) + "\nmutableAttributesFromServer: " + str(self.mutableAttributesFromServer) + "\nattributesSigBase64FromServer: " + str(self.attributesSigBase64FromServer) + "\nmutableAttributesSigBase64FromServer: " + str(self.mutableAttributesSigBase64FromServer)
    
    @staticmethod
    def _marshalFromC(cKey):
        if cKey is None:
            return None
        
        pyKey = KeyData(
            _private.CMarshalUtil.stringFromC(cKey.pszKeyId),
            _private.CMarshalUtil.bytesFromC(cKey.keyBytes),
            KeyAttributesDict._marshalFromC(cKey.pAttributesMap),
            KeyObligationsDict._marshalFromC(cKey.pObligationsMap),
            _private.CMarshalUtil.stringFromC(cKey.pszOrigin),
            KeyAttributesDict._marshalFromC(cKey.pMutableAttributesMap),
            KeyAttributesDict._marshalFromC(cKey.pMutableAttributesFromServer),
            _private.CMarshalUtil.stringFromC(cKey.pszAttributesSigBase64FromServer),
            _private.CMarshalUtil.stringFromC(cKey.pszMutableAttributesSigBase64FromServer))
        return pyKey

    @staticmethod
    def _marshalToC(pyKey):
        if pyKey is None:
            return None

        cKey = _private.CKeyData(
            _private.CMarshalUtil.stringToC(pyKey.id),
            _private.CMarshalUtil.bytesToC(pyKey.bytes),
            KeyAttributesDict._marshalToC(pyKey.attributes, False),
            KeyObligationsDict._marshalToC(pyKey.obligations, False),
            _private.CMarshalUtil.stringToC(pyKey.origin),
            KeyAttributesDict._marshalToC(pyKey.mutableAttributes, False),
            KeyAttributesDict._marshalToC(pyKey.mutableAttributesFromServer, False),
            _private.CMarshalUtil.stringToC(pyKey.attributesSigBase64FromServer),
            _private.CMarshalUtil.stringToC(pyKey.mutableAttributesSigBase64FromServer))
        
        return cKey

class KeyDataList(list):
    """!List of keys with convenience functions for searching.
    """
    def __repr__(self):
        return '<KeyDataList ' + repr(self.getids()) + '>'
    
    def getids(self):
        """!Gets a list of all the key IDs in this KeyDataList.
        @return
            A list of the key ID's in this list of Keys
        """
        return list(map( lambda key: key.id, self))
    
    def findkey(self, keyid):
        """!Returns the key object with the matching ID, or None if not found.
        @param
            keyid (string): The key id to search for
        @return
            The KeyData if found, or None otherwise
        """
        for key in self:
            if key.id == keyid:
                return key
        return None
    
    @staticmethod
    def _marshalFromC(cKeyArray):
        if cKeyArray is None:
            return None
        
        pyKeyList = KeyDataList()
        for i in range(cKeyArray.nSize):
            key = KeyData._marshalFromC(cKeyArray.ppKeyArray[i].contents)
            pyKeyList.append(key)
        return pyKeyList

    @staticmethod
    def _marshalToC(pyKeyArray):
        
        if pyKeyArray is None:
            return None
    
        cKeyDataArray = _private.cLib.ionic_create_keydata_array(len(pyKeyArray))
        
        for i in range(len(pyKeyArray)):
            try:
                _private.cLib.ionic_set_keydata_in_array_with_ref(cKeyDataArray, i, KeyData._marshalToC(pyKeyArray[i]), pyKeyArray[i].ref)
            except:
                _private.cLib.ionic_set_keydata_in_array(cKeyDataArray, i, KeyData._marshalToC(pyKeyArray[i]))

        return cKeyDataArray

class RefKeyData(KeyData):
    """!Defines a data protection key as returned by Ionic.com."""
    def __init__(self, id, bytes, attributes=None, obligations=None, origin=None, mutableAttributes=None, mutableAttributesFromServer=None, attributesSigBase64FromServer=None, mutableAttributesSigBase64FromServer=None, ref=None):
        """!Initializes the key object with provided inputs.

        @param
            id (string): The key ID (also known as the key tag).
        @param
            bytes (bytes): The raw key bytes.  It must be exactly 32 bytes in length.
        @param
            attributes (dict[string,list[string]], optional): The key attributes.
        @param
            obligations (KeyObligationsDict) The key obligations
        @param
            origin (string) The key origin, usually a URL
        @param
            mutableAttributes (KeyAttributesDict) The key mutable attributes
        @param
            mutableAttributesFromServer (KeyAttributesDict) The key mutable attributes from the server version
        @param
            attributesSigBase64FromServer (string) Base 64 encoded signature of the server's non-mutable attributes
        @param
            mutableAttributesSigBase64FromServer (string) Base 64 encoded signature of the server's mutable attributes
        @param
            ref (string) A reference parameter usually returned by a request for multiple keys with different attributes
        """
        KeyData.__init__(self, id, bytes, attributes, obligations, origin, mutableAttributes, mutableAttributesFromServer, attributesSigBase64FromServer, mutableAttributesSigBase64FromServer)
        ##(string) The key reference
        self.ref = ref


class RefKeyDataList(KeyDataList):
    """!List of keys and associated references with convenience functions for searching.
    """
    def __repr__(self):
        return '<RefKeyDataList ' + repr(self.getids()) + '>'
    
    def findref(self, ref):
        """!Returns the first key object with the matching reference string, or None if not found.
            Further matching ref values can be found by removing used keys from the list or a copy of the list.
        @param
            ref (string): The reference string to search for
        @return
            The KeyData if found, or None otherwise
        """
        for key in self:
            if key.ref == ref:
                return key
        return None
    
    @staticmethod
    def _marshalFromC(cKeyArray):
        if cKeyArray is None:
            return None
        
        pyKeyList = RefKeyDataList()
        for i in range(cKeyArray.nSize):
            key = RefKeyData._marshalFromC(cKeyArray.ppKeyArray[i].contents)
            if cKeyArray.ppszRefs:
                key.ref = _private.CMarshalUtil.stringFromC(cKeyArray.ppszRefs[i])
            pyKeyList.append(key)
        return pyKeyList

    @staticmethod
    def _marshalToC(pyKeyArray):
        
        if pyKeyArray is None:
            return None
    
        cKeyDataArray = _private.cLib.ionic_create_keydata_array(len(pyKeyArray))
        
        for i in range(len(pyKeyArray)):
            try:
                _private.cLib.ionic_set_keydata_in_array_with_ref(cKeyDataArray, i, RefKeyData._marshalToC(pyKeyArray[i]), pyKeyArray[i].ref)
            except:
                _private.cLib.ionic_set_keydata_in_array(cKeyDataArray, i, RefKeyData._marshalToC(pyKeyArray[i]))

        return cKeyDataArray

class UpdateKeyData(KeyData):
    """!Defines a data protection key as returned by Ionic.com."""
    def __init__(self, id, bytes, attributes=None, obligations=None, origin=None, mutableAttributes=None, mutableAttributesFromServer=None, attributesSigBase64FromServer=None, mutableAttributesSigBase64FromServer=None, forceUpdate = False):
        """!Initializes the key object with provided inputs.
            
        @param
            id (string): The key ID (also known as the key tag).
        @param
            bytes (bytes): The raw key bytes.  It must be exactly 32 bytes in length.
        @param
            attributes (dict[string,list[string]], optional): The key attributes.
        @param
            obligations (KeyObligationsDict) The key obligations
        @param
            origin (string) The key origin, usually a URL
        @param
            mutableAttributes (KeyAttributesDict) The key mutable attributes
        @param
            mutableAttributesFromServer (KeyAttributesDict) The key mutable attributes from the server version
        @param
            attributesSigBase64FromServer (string) Base 64 encoded signature of the server's non-mutable attributes
        @param
            mutableAttributesSigBase64FromServer (string) Base 64 encoded signature of the server's mutable attributes
        @param
            forceUpdate (bool): Whether to force update or error when asked to update an out of date key.
        """
        KeyData.__init__(self, id, bytes, attributes, obligations, origin, mutableAttributes, mutableAttributesFromServer, attributesSigBase64FromServer, mutableAttributesSigBase64FromServer)
        ##(bool) The force flag controls whether or not the Ionic key server should update the key forcefully when it is out of date
        self.forceUpdate = forceUpdate
    
    def __repr__(self):
        return '<UpdateKeyData id="{0}">'.format(self.id)
    
    def Debug(self):
        """!Get a debugging string representation of the instance
        @return
            A string describing the instance
        """
        return "UpdateKeyData id: " + str(self.id) + "\nattributes: " + str(self.attributes) + "\nobligations: " + str(self.obligations) + "\norigin: " + str(self.origin) + "\nmutableAttributes: " + str(self.mutableAttributes) + "\nmutableAttributesFromServer: " + str(self.mutableAttributesFromServer) + "\nattributesSigBase64FromServer: " + str(self.attributesSigBase64FromServer) + "\nmutableAttributesSigBase64FromServer: " + str(self.mutableAttributesSigBase64FromServer) + "\nforceUpdate: " + str(self.forceUpdate)
    
    @staticmethod
    def _marshalFromC(cUpdateKey):
        if cUpdateKey is None:
            return None
        
        pyUpdateKey = UpdateKeyData(
                        _private.CMarshalUtil.stringFromC(cUpdateKey.pszKeyId),
                        _private.CMarshalUtil.bytesFromC(cUpdateKey.keyBytes),
                        KeyAttributesDict._marshalFromC(cUpdateKey.pAttributesMap),
                        KeyObligationsDict._marshalFromC(cUpdateKey.pObligationsMap),
                        _private.CMarshalUtil.stringFromC(cUpdateKey.pszOrigin),
                        KeyAttributesDict._marshalFromC(cUpdateKey.pMutableAttributesMap),
                        KeyAttributesDict._marshalFromC(cUpdateKey.pMutableAttributesFromServer),
                        _private.CMarshalUtil.stringFromC(cUpdateKey.pszAttributesSigBase64FromServer),
                        _private.CMarshalUtil.stringFromC(cUpdateKey.pszMutableAttributesSigBase64FromServer),
                        cUpdateKey.bForceUpdate)
        return pyUpdateKey

    @staticmethod
    def FromKeyData(pyKey, forceUpdate = False):
        """!Utlity method for converting from KeyData to UpdateKeyData
        @param
            pyKey (KeyData): Key data to convert
        @param
            forceUpdate (bool): Whether to force update or error when asked to update an out of date key.
        @return
            An UpdateKeyData instance copied from the args
        """
        if pyKey is None:
            return None
        
        return UpdateKeyData(pyKey.id, pyKey.bytes, pyKey.attributes, pyKey.obligations, pyKey.origin, pyKey.mutableAttributes, pyKey.mutableAttributesFromServer, pyKey.attributesSigBase64FromServer, pyKey.mutableAttributesSigBase64FromServer, forceUpdate)

    @staticmethod
    def _marshalToC(pyUpdateKey):
        if pyUpdateKey is None:
            return None
        
        cUpdateKey = _private.CUpdateKeyData(_private.CMarshalUtil.stringToC(pyUpdateKey.id),
                                 _private.CMarshalUtil.bytesToC(pyUpdateKey.bytes),
                                 KeyAttributesDict._marshalToC(pyUpdateKey.attributes, False),
                                 KeyAttributesDict._marshalToC(pyUpdateKey.mutableAttributes, False),
                                 KeyObligationsDict._marshalToC(pyUpdateKey.obligations, False),
                                 _private.CMarshalUtil.stringToC(pyUpdateKey.origin),
                                 KeyAttributesDict._marshalToC(pyUpdateKey.mutableAttributesFromServer, False),
                                 _private.CMarshalUtil.stringToC(pyUpdateKey.attributesSigBase64FromServer),
                                 _private.CMarshalUtil.stringToC(pyUpdateKey.mutableAttributesSigBase64FromServer),
                                 pyUpdateKey.forceUpdate)
                                 
        return cUpdateKey

class UpdateKeyDataList(list):
    """!List of pdate keys with convenience functions for searching."""
    def __repr__(self):
        return '<UpdateKeyDataList ' + repr(self.getids()) + '>'
    
    def getids(self):
        """!Gets a list of all the key IDs in this KeyDataList.
        @return
            A list of the key IDs in this list
        """
        return list(map( lambda key: key.id, self))
    
    def findkey(self, keyid):
        """!Returns the key object with the matching ID, or None if not found.
        @param
            keyid (string): The key id to search for
        @return
            The UpdateKeyData instance if found, otherwise None
        """
        for key in self:
            if key.id == keyid:
                return key
        return None
    
    @staticmethod
    def _marshalFromC(cKeyArray):
        if cKeyArray is None:
            return None
        
        pyKeyList = KeyDataList()
        for i in range(cKeyArray.nSize):
            pyKeyList.append(KeyData._marshalFromC(cKeyArray.ppKeyArray[i].contents))
        return pyKeyList
    
    @staticmethod
    def _marshalToC(pyKeyArray):
        
        if pyKeyArray is None:
            return None

        cKeyDataArray = _private.cLib.ionic_create_updatekeydata_array(len(pyKeyArray))

        for i in range(len(pyKeyArray)):
            _private.cLib.ionic_set_updatekeydata_in_array(cKeyDataArray, i, UpdateKeyData._marshalToC(pyKeyArray[i]))
        
        return cKeyDataArray

    @staticmethod
    def FromKeyDataList(pyKeyList, forceUpdate = False):
        """!Utility method for converting from KeyDataList to UpdateKeyDataList
        @param
            pyKeyList (KeyDataList): Key data list to convert
        @param
            forceUpdate (bool): Whether to force update or error when asked to update an out of date key.
        @return
            An UpdateKeyDataList instance copied from the args
        """
        if pyKeyList is None:
            return None

        pyUpdateKeyList = UpdateKeyDataList()
        for i in range(len(pyKeyList)):
            pyUpdateKeyList.append(UpdateKeyData.FromKeyData(pyKeyList[i], forceUpdate))

        return pyUpdateKeyList

class KeyAttributesDict(defaultdict):
    """!Default Dictionary of string Attribute names with lists of string values.
    """
    def __init__(self):
        """!Constructs an empty attribute container
        """
        super(KeyAttributesDict, self).__init__(list)
    
    @staticmethod
    def _marshalFromC(cAttributesMap):
        # Convert C key attributes map (CAttributesMap) into Python dictionary.
        if cAttributesMap is None:
            return None
        numKeys = _private.c_size_t(0)
        pyAttributesDict = KeyAttributesDict()
        cKeyArray = _private.cLib.ionic_attributesmap_get_keys_array(cAttributesMap,
                                                    _private.byref(numKeys))
        if numKeys.value == 0:
            return None
        if cKeyArray:
            for i in range(numKeys.value):
                pyKey = _private.CMarshalUtil.stringFromC(cKeyArray[i])
                numValues = _private.c_size_t(0)
                cValues = _private.cLib.ionic_attributesmap_get_values_array(cAttributesMap,
                              cKeyArray[i], _private.byref(numValues))
                for j in range(numValues.value):
                    pyAttributesDict[pyKey].append(_private.CMarshalUtil.stringFromC(cValues[j]))
        return pyAttributesDict
        
    @staticmethod
    def _marshalToC(pyAttributes, bOwned=True):
        # Convert Python dictionary into C key attributes map (CAttributesMap).
        # The returned C attributes map will be garbage collected and does NOT 
        # need to be released manually in any way.
        cAttributes = _private.cLib.ionic_attributesmap_create()
        if(bOwned):
            cAttributes = _private.OWNED_POINTER(_private.CAttributesMap)(cAttributes[0])
        
        if pyAttributes is None:
            return cAttributes
        for key,val in pyAttributes.items():
            if isinstance(val, ("".__class__, u"".__class__)):
                _private.cLib.ionic_attributesmap_set(cAttributes,
                                  _private.CMarshalUtil.stringToC(key),
                                  _private.CMarshalUtil.stringToC(val))
            else:
                for one in val:
                    _private.cLib.ionic_attributesmap_set(cAttributes,
                                      _private.CMarshalUtil.stringToC(key),
                                      _private.CMarshalUtil.stringToC(one))
        return cAttributes

class KeyObligationsDict(defaultdict):
    """!Default Dictionary of string Obligation names with lists of string values.
    """
    def __init__(self):
        """!Constructs an empty Obligations container
        """
        super(KeyObligationsDict, self).__init__(list)
    
    @staticmethod
    def _marshalFromC(cObligationsMap):
        # Convert C key obligations map (CObligationsMap) into Python dictionary.
        if cObligationsMap is None:
            return None
        numKeys = _private.c_size_t(0)
        pyObligationsDict = KeyObligationsDict()
        cKeyArray = _private.cLib.ionic_obligationsmap_get_keys_array(cObligationsMap,
                                                    _private.byref(numKeys))
        if cKeyArray:
            for i in range(numKeys.value):
                pyKey = _private.CMarshalUtil.stringFromC(cKeyArray[i])
                numValues = _private.c_size_t(0)
                cValues = _private.cLib.ionic_obligationsmap_get_values_array(cObligationsMap,
                              cKeyArray[i], _private.byref(numValues))
                for j in range(numValues.value):
                    pyObligationsDict[pyKey].append(_private.CMarshalUtil.stringFromC(cValues[j]))
        return pyObligationsDict
        
    @staticmethod
    def _marshalToC(pyObligations, bOwned=True):
        # Convert Python dictionary into C key obligations map (CObligationsMap).
        # The returned C obligations map will be garbage collected and does NOT 
        # need to be released manually in any way.
        cObligations = _private.cLib.ionic_obligationsmap_create()
        if(bOwned):
            cObligations = _private.OWNED_POINTER(_private.CObligationsMap)(cObligations[0])

        if pyObligations is None:
            return cObligations
        for key,val in pyObligations.items():
            if isinstance(val, ("".__class__, u"".__class__)):
                _private.cLib.ionic_obligationsmap_set(cObligations,
                                  _private.CMarshalUtil.stringToC(key),
                                  _private.CMarshalUtil.stringToC(val))
            else:
                for one in val:
                    _private.cLib.ionic_obligationsmap_set(cObligations,
                                      _private.CMarshalUtil.stringToC(key),
                                      _private.CMarshalUtil.stringToC(one))
        return cObligations

class MetadataDict(dict):
    """!Dictionary of string to string."""
    @staticmethod
    def _marshalFromC(cMetadata):
        """Convert C metadata map (CMetadataMap) into Python dictionary"""
        if cMetadata is None:
            return None
        pyMetadataDict = MetadataDict()
        numKeys = _private.c_size_t(0)
        cKeyArray = _private.cLib.ionic_metadatamap_get_keys_array(cMetadata,
                                                                   _private.byref(numKeys))
        if cKeyArray:
            for i in range(numKeys.value):
                cValue = _private.cLib.ionic_metadatamap_get(cMetadata, cKeyArray[i])
                pyKey = _private.CMarshalUtil.stringFromC(cKeyArray[i])
                pyValue = _private.CMarshalUtil.stringFromC(cValue)
                pyMetadataDict[pyKey] = pyValue
        return pyMetadataDict
        
    @staticmethod
    def _marshalToC(pyMetadataDict):
        """Convert Python dictionary into C metadata map (CMetadataMap).
        The returned C metadata map will be garbage collected and does
        NOT need to be released manually in any way."""
        if pyMetadataDict is None:
            return None
        cMeta = _private.cLib.ionic_metadatamap_create()
        for key,val in pyMetadataDict.items():
            _private.cLib.ionic_metadatamap_set(cMeta, _private.CMarshalUtil.stringToC(key),
                                                _private.CMarshalUtil.stringToC(val))
        return cMeta

class DeviceProfile(object):
    """!Data class for storing device profile information (also known as SEP data).

    This class stores device profile information which is the result of
    a successful device registration performed via Agent.createdevice().

    A device profile is also known as a SEP (Secure Enrollment Profile).
    """
    def __init__(self, name, deviceid, keyspace, server,
                 creationtimestampsecs, aesCdIdcProfileKey, aesCdEiProfileKey):
        """!Initializes the agent config object with provided inputs.

        @param
            name (string): The human readable name associated with this profile.
        @param
            deviceid (string): Device ID generated by Ionic.com during registration.
        @param
            keyspace (string): The device profile key space.
        @param
            server (string): The Ionic.com server associated with this device profile.
        @param
            creationtimestampsecs (int): The time at which this profile
                       was created in UTC seconds since January 1, 1970.
        @param
            aesCdIdcProfileKey (bytes): The private AES key shared
                                        between client and Ionic.com.
        @param
            aesCdEiProfileKey (bytes): The private AES key shared
                      between client and EI (Enterprise Infrastructure).
        """
        ##(string) The human readable name associated with this profile
        self.name = name
        ##(string) Device ID generated by Ionic.com during registration
        self.deviceid = deviceid
        ##(string) The device profile key space
        self.keyspace = keyspace
        ##(string): The Ionic.com server associated with this device profile
        self.server = server
        ##(int): The time at which this profile was created in UTC seconds since January 1, 1970
        self.creationtimestampsecs = creationtimestampsecs
        ##(bytes): The private AES key shared between client and Ionic.com
        self.aesCdIdcProfileKey = aesCdIdcProfileKey
        ##(bytes): The private AES key shared between client and EI (Enterprise Infrastructure)
        self.aesCdEiProfileKey = aesCdEiProfileKey
    
    def __repr__(self):
        return '<DeviceProfile name="{0.name}" deviceid="{0.deviceid}" keyspace="{0.keyspace}">'.format(self)

    @staticmethod
    def _marshalFromC(cProfile):
        if cProfile is None:
            return None
        
        pyProfile = DeviceProfile(
            _private.CMarshalUtil.stringFromC(cProfile.pszName),
            _private.CMarshalUtil.stringFromC(cProfile.pszDeviceId),
            _private.CMarshalUtil.stringFromC(cProfile.pszKeySpace),
            _private.CMarshalUtil.stringFromC(cProfile.pszServer),
            cProfile.nCreationTimestampSecs,
            _private.CMarshalUtil.bytesFromC(cProfile.aesCdIdcProfileKey),
            _private.CMarshalUtil.bytesFromC(cProfile.aesCdEiProfileKey))
        return pyProfile
        
    @staticmethod
    def _marshalToC(pyProfile):
        if pyProfile is None:
            return None
        
        cProfile = _private.CDeviceProfile()
        cProfile.pszName = _private.CMarshalUtil.stringToC(pyProfile.name)
        cProfile.pszDeviceId = _private.CMarshalUtil.stringToC(pyProfile.deviceid)
        cProfile.pszKeySpace = _private.CMarshalUtil.stringToC(pyProfile.keyspace)
        cProfile.pszServer = _private.CMarshalUtil.stringToC(pyProfile.server)
        cProfile.nCreationTimestampSecs = pyProfile.creationtimestampsecs
        cProfile.aesCdIdcProfileKey = _private.CMarshalUtil.bytesToC(pyProfile.aesCdIdcProfileKey)
        cProfile.aesCdEiProfileKey = _private.CMarshalUtil.bytesToC(pyProfile.aesCdEiProfileKey)
        return cProfile

# Helper class for DeviceProfile lists
class DeviceProfileList(list):
    """!List of DeviceProfiles."""
    
    def __init__(self):
        """!Contsructs an empty list
        """

        ##(string) Device ID of the active profile
        self.activeDeviceId = u""
        super(DeviceProfileList, self).__init__()
    
    def __repr__(self):
        return '<DeviceProfileList ' + repr(self.getdeviceids()) + '>'
    
    def getdeviceids(self):
        """!Find DeviceProfile with a matching deviceid.
        @return
            The DeviceProfile instance or None if not found
        """
        return list(map( lambda profile: profile.deviceid, self))
    
    @staticmethod
    def LoadAllProfiles(devicePersistor):
        """!Loads all profiles, generally from an encrypted json file
        @param
            devicePersistor (DeviceProfilePersistorBase) instance used to load and save device profiles
        @return
            A DeviceProfileList instance
        """
        cNumProfiles = _private.c_size_t(0)
        cProfileArray= _private.OWNED_POINTER(_private.POINTER(_private.CDeviceProfile))()
        cActiveDeviceId = _private.OWNED_POINTER(_private.c_char)()
        try:
            _private.cLib.ionic_load_all_device_profiles(devicePersistor._cPersistor, _private.byref(cProfileArray), _private.byref(cNumProfiles), _private.byref(cActiveDeviceId))

        except Exception as e:
            raise IonicException("Could not load profiles: " + str(e), IonicError.AGENT_LOAD_PROFILES_FAILED)
    
        profiles = DeviceProfileList._marshalFromC(cProfileArray, cNumProfiles)
        profiles.activeDeviceId = _private.CMarshalUtil.stringFromC(cActiveDeviceId)
            
        return profiles
    
    def SaveAllProfiles(self, devicePersistor):
        """!Saves all profiles, generally into an encrypted json file
        @param
            devicePersistor (DeviceProfilePersistorBase) instance used to load and save device profiles
        @return
            None, raises an exception on errors
        """
        cProfileArray, cNumProfiles = DeviceProfileList._marshalToC(self)
        cActiveDeviceId = _private.CMarshalUtil.stringToC(self.activeDeviceId)
        
        _private.cLib.ionic_save_all_device_profiles(devicePersistor._cPersistor, cProfileArray, cNumProfiles, cActiveDeviceId)
    
    @staticmethod
    def _marshalFromC(cProfileArray, profileCount):
        if cProfileArray is None:
            return None
        
        pyProfileList = DeviceProfileList()
        for i in range(0, profileCount.value):
            pyProfileList.append(DeviceProfile._marshalFromC(cProfileArray[i].contents))
        return pyProfileList

    @staticmethod
    def _marshalToC(pyProfileArray):
        if pyProfileArray is None:
            return None, None
        count = len(pyProfileArray)
        cProfileArray = (_private.POINTER(_private.CDeviceProfile) * count)()

        for i in range(count):
            cProfile = DeviceProfile._marshalToC(pyProfileArray[i])
            cProfileArray[i] = _private.pointer(cProfile)
        
        return cProfileArray, _private.c_size_t(count)


class DeviceProfilePersistorBase(object):
    """!Abstract class used to load and save device profiles.

    This class provides the interface required for all device profile
    persistor implementations (e.g. DeviceProfilePersistorDefault,
    DeviceProfilePersistorAesGcm).  A device profile persistor is
    responsible for loading and saving device profile objects
    (DeviceProfile).

    The default implementation (DeviceProfilePersistorDefault) is
    typically sufficient for most desktop application environments.
    Another commonly used secure implementation is
    DeviceProfilePersistorAesGcmFile.
    """
    def __new__(cls, *args, **kwargs): # The base class should not be used directly
        if cls is DeviceProfilePersistorBase:
            raise NotImplementedError()
        return super(DeviceProfilePersistorBase, cls).__new__(cls)
    
    def __init__(self):
        """!Constructs a persistor with default values
        """
        self._cPersistor = None

    def getversion(self):
        """!Gets the profile persistor verion to use, or an empty value if a default will be used.
        @return
            A string value for the version to use, or an empty string for a default value.
        """
        cVersion = _private.cLib.ionic_profile_persistor_get_version(self._cPersistor)
        return _private.CMarshalUtil.stringFromC(cVersion)

    def setversion(self, version):
        """!Sets the profile persistor verion to use. An empty value will have a default be used.
        @param
            version (string) value to use to pick the version, or empty for a default version.
        @return
            None, raises an exception on errors
        """
        cVersion = _private.CMarshalUtil.stringToC(version)
        _private.cLib.ionic_profile_persistor_set_version(self._cPersistor, cVersion)

# Implementations
class DeviceProfilePersistorDefault(DeviceProfilePersistorBase):
    """!Default device profile persistor implementation.
    
    This class provides the default device persistor implementation for
    the environment / operating system that the program runs.
    """
    def __init__(self):
        """!Constructs a persistor with default values
        """       
        super(DeviceProfilePersistorDefault,self).__init__()
        self._cPersistor = _private.cLib.ionic_profile_persistor_create_default()

class DeviceProfilePersistorPasswordFile(DeviceProfilePersistorBase):
    """!Password protected device profile persistor implementation.
    
    This class provides a file-based device persistor that is password 
    protected.  The minimum password length is six characters; use of a password of
    insufficient length will cause an
    \ref ionicsdk.errors.IonicError.AGENT_INVALIDVALUE "AGENT_INVALIDVALUE"
    \ref ionicsdk.exceptions.IonicException "IonicException".
    """
    def __init__(self, filepath, password):
        """!Constructs a persistor with the provided values

        @param
            filepath (string): The file name and path
        @param
            password (string): A user password as a string
        """
        super(DeviceProfilePersistorPasswordFile,self).__init__()
        ##(unicode) File name and path where the encrypted JSON file will be located
        self.filepath = filepath
        self._cPersistor = _private.cLib.ionic_profile_persistor_create_pw_file(
            _private.CMarshalUtil.stringToC(filepath),
            _private.CMarshalUtil.stringToC(password))

class DeviceProfilePersistorAesGcmFile(DeviceProfilePersistorBase):
    """!AES/GCM protected device profile persistor implementation.
    
    This class provides a file-based device persistor that is protected
    by an encryption key.

    The Additional Authenticated Data (AAD) provided in authdata must not be empty.
    """
    def __init__(self, filepath, keydata, authdata):
        """!Constructs a persistor with the provided values

        @param
            filepath (string): The file name and path
        @param
            keydata (bytes): The raw key bytes.  It must be exactly 32 bytes in length.
        @param
            authdata (bytes): The raw auth data. If None or empty, no AAD will be used.
        """
        super(DeviceProfilePersistorAesGcmFile,self).__init__()
        ##(unicode) File name and path where the encrypted JSON file will be located
        self.filepath = filepath
        self._cPersistor = _private.cLib.ionic_profile_persistor_create_aesgcm_file(
            _private.CMarshalUtil.stringToC(filepath),
            _private.CMarshalUtil.bytesToC(keydata),
            _private.CMarshalUtil.bytesToC(authdata))

if os.name == 'posix':
    if sys.platform == 'mac' or sys.platform == 'darwin':
        class DeviceProfilePersistorMac(DeviceProfilePersistorBase):
            """!Mac keychain protected device profile persistor implementation.
            
            This class provides a file-based device persistor that is protected
            by an encryption key stored in the Mac keychain.
            """
            def __init__(self, filepath=None, keychainAccessDescription=None):
                """!Constructs a persistor with the provided values

                @param
                    filepath (string): Optional, the file name and path
                @param
                    keychainAccessDescription (string): Optional, the description to show if 
                    the OS keychain needs to prompt for permission.
                """
                super(DeviceProfilePersistorMac,self).__init__()
                ##(unicode) File name and path where the encrypted JSON file will be located
                self.filepath = filepath
                self._cPersistor = _private.cLib.ionic_profile_persistor_create_mac(
                    _private.CMarshalUtil.stringToC(filepath),
                    _private.CMarshalUtil.stringToC(keychainAccessDescription))
    else:
        class DeviceProfilePersistorLinux(DeviceProfilePersistorBase):
            """!Linux file permission protected device profile persistor implementation.
            
            This class provides a file-based device persistor that is protected
            by Linux file permissions, but is not encrypted.
            """
            def __init__(self, filepath=None):
                """!Constructs a persistor with the provided values

                @param
                    filepath (string): Optional, the file name and path
                """
                super(DeviceProfilePersistorLinux,self).__init__()
                ##(unicode) File name and path where the JSON file will be located
                self.filepath = filepath
                self._cPersistor = _private.cLib.ionic_profile_persistor_create_linux(
                    _private.CMarshalUtil.stringToC(filepath))
else:
    class DeviceProfilePersistorWindows(DeviceProfilePersistorBase):
        """!Windows DPAPI protected device profile persistor implementation.
        
        This class provides a file-based device persistor that is protected
        by an encryption using DPAPI.
        """
        def __init__(self, filepath=None):
            """!Constructs a persistor with the provided values

            @param
                filepath (string): Optional, the file name and path
            """
            super(DeviceProfilePersistorWindows,self).__init__()
            ##(unicode) File name and path where the encrypted JSON file will be located
            self.filepath = filepath
            self._cPersistor = _private.cLib.ionic_profile_persistor_create_windows(
                _private.CMarshalUtil.stringToC(filepath))

class DeviceProfilePersistorPlaintextFile(DeviceProfilePersistorBase):
    """!Plaintext device profile persistor implementation.
    
    This class provides a file-based device persistor that is not
    protected.
    """
    def __init__(self, filepath):
        """!Constructs a persistor with the provided values

        @param
            filepath (string): The file name and path
        """
        super(DeviceProfilePersistorPlaintextFile,self).__init__()
        ##(unicode) File name and path where the JSON file will be located
        self.filepath = filepath
        self._cPersistor = _private.cLib.ionic_profile_persistor_create_plaintext_file(
            _private.CMarshalUtil.stringToC(filepath))

class SecretShareProfilePersistor(DeviceProfilePersistorBase):
    """!Secret Share device profile persistor implementation.
        @details
        This class uses a SecretShareData object to populate data. (See SecretShareData)
        
        DO NOT use the provided SecretShareData class alone.  You must subclass the provided
        class and add a GetData() and GetBuckets() method.
        
        This class provides a file-based device persistor that is uses
        a seperate Secret Share Persistor to store the encryption keys.
        
        It needs two file paths, one for the secret share persistor and
        the other for the encrypted device profiles.
        
        NOTE: The secret share persistor will query the SecretShareData each time a key
        is requested.  It does not cache anything other than the file paths.
    """
    def __init__(self, secretsharedata, filePath = None, secretshareFilePath = None):
        """!Constructs a persistor with the provided values

        @param
            secretsharedata (SecretShareData) data object used by secret share to encrypt
        @param
            filePath (string): The device profile file path to use
        @param
            secretshareFilePath (string): The secret share persistor file path to use
        """
        super(SecretShareProfilePersistor,self).__init__()
        
        if not issubclass(type(secretsharedata), SecretShareData):
            raise TypeError()
    
        self._cSecretShareProfilePersistor = _private.cLib.ionic_secret_share_profile_persistor_create(secretsharedata._cSecretShareData, _private.CMarshalUtil.stringToC(filePath), _private.CMarshalUtil.stringToC(secretshareFilePath))
        
        if not self._cSecretShareProfilePersistor:
            raise IonicException('Failed to create a SecretShareProfilePersistor object. Check the log to know the reason for this error (common cause is failure to initialize internally).', IonicError.AGENT_ERROR)

        self._cPersistor = _private.cLib.ionic_secret_share_profile_to_device_profile(self._cSecretShareProfilePersistor)
    
    def SetFilePath(self, filePath):
        """!Sets the encrypted device profile file path
            
        @param
            filePath (string): The device profile file path to use
        @return
            None
        """
        _private.cLib.ionic_secret_share_profile_persistor_set_filepath(self._cSecretShareProfilePersistor, _private.CMarshalUtil.stringToC(filePath))
    
    def SetSecretShareFilePath(self, filePath):
        """!Sets the secret share persistor file path
            
        @param
            filePath (string): The secret share persistor file path to use
        @return
            None
        """
        _private.cLib.ionic_secret_share_profile_persistor_set_secret_share_filepath(self._cSecretShareProfilePersistor, _private.CMarshalUtil.stringToC(filePath))



