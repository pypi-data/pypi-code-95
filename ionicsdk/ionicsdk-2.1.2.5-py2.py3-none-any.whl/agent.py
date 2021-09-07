"""!The client-side library for all Ionic.com REST API endpoint
communication.
"""

import ionicsdk._private as _private
from ionicsdk.common import *
from ionicsdk.profilemanager import *
from ionicsdk.services import *
from ionicsdk.exceptions import *
from ionicsdk.errors import *
from collections import defaultdict

class GetKeyQueryResult(object):
    """!Class used to return external key query result object(s)."""
    def __init__(self, externalkeyid, errorcode, errormessage, keyids):
        """!Constructor which assigns all internal variables.
            
        @param
            externalkeyid (string) The external key id
        @param
            errorcode (int) The error code
        @param
            errormessage (string) The error text message
        @param
            keyids (string) The Key IDs
        """

        ##(string) The external key id
        self.externalkeyid = externalkeyid
        ##(int) The error code
        self.errorcode = errorcode
        ##(string) The error text message
        self.errormessage = errormessage
        ##(string) The Key IDs
        self.keyids = keyids

    @staticmethod
    def _marshalFromC(cGetKeyQueryResult):
        if cGetKeyQueryResult is None:
            return None
        
        pyResult = GetKeyQueryResult(
                        _private.CMarshalUtil.stringFromC(cGetKeyQueryResult.pszExternalKeyId),
                        cGetKeyQueryResult.nErrorCode,
                        _private.CMarshalUtil.stringFromC(cGetKeyQueryResult.pszErrorMessage),
                        _private.CMarshalUtil.stringArrayFromC(cGetKeyQueryResult.ppszKeyIds, cGetKeyQueryResult.nKeyIdCount))
        return pyResult

    def __repr__(self):
        return '<GetKeyQueryResult for "{0}">'.format(self.externalkeyid)

class GetKeyQueryList(list):
    """!List of Get Key Query Results with convenience functions for
    searching by external ID.
    """

    def __repr__(self):
        return '<GetKeyQueryList ' + super(GetKeyQueryList,self).__repr__() + '>'
    
    def findexternalkeyid(self, externalkeyid):
        """!Find a query result in this list by external key id.
            
        @param
            externalkeyid (string) The external key id to search for
        @return
            The query result or None if it was not found in the list.
        """
        for result in self:
            if result.externalkeyid == externalkeyid:
                return result
        return None
    
    @staticmethod
    def _marshalFromC(cGetKeyQueryList):
        if cGetKeyQueryList is None:
            return None
    
        pyGetKeyQueryList = GetKeyQueryList()
        for i in range(cGetKeyQueryList.nSize):
            pyGetKeyQueryList.append(GetKeyQueryResult._marshalFromC(cGetKeyQueryList.ppQueryResults[i].contents))
        return pyGetKeyQueryList

class GetKeyError(object):
    """!Class used to return Error object(s) from calls to GetKeys2.
    """
    def __init__(self, keyid, clienterror, servererror, servermessage):
        """!Constructor which assigns all internal variables.
            
        @param
            keyid (string) The key id to search for
        @param
            clienterror (int) The client error code
        @param
            servererror (int) The server error code
        @param
            servermessage (string) The server error message text
        """

        ##(string) The Key ID
        self.keyid = keyid
        ##(int) The client error code
        self.clienterror = clienterror
        ##(int) The server error code
        self.servererror = servererror
        ##(string) The server error message text
        self.servermessage = servermessage

    @staticmethod
    def _marshalFromC(cGetKeyError):
        if cGetKeyError is None:
            return None
        
        pyError = GetKeyQueryResult(
                     _private.CMarshalUtil.stringFromC(cGetKeyError.pszKeyId),
                     cGetKeyError.nClientError,
                     cGetKeyError.nServerError,
                     _private.CMarshalUtil.stringFromC(cGetKeyError.pszServerMessage))
        return pyError

    def __repr__(self):
        return '<GetKeyError for "{0}">'.format(self.keyid)

class GetKeyErrorList(list):
    """!List of Get Key Errors with convenience functions for searching
    by key id.
    """
    
    def __repr__(self):
        return '<GetKeyErrorList ' + super(GetKeyErrorList,self).__repr__() + '>'
    
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
    def _marshalFromC(cGetKeyErrorList):
        if cGetKeyErrorList is None:
            return None
        
        pyGetKeyErrorList = GetKeyErrorList()
        for i in range(cGetKeyErrorList.nSize):
            pyGetKeyQueryList.append(GetKeyError._marshalFromC(cGetKeyErrorList.ppErrors[i].contents))
        return pyGetKeyErrorList

class CreateKeysRequest(object):
    """!Class used to request multiple keys with varying attributes."""
    class KeyRequest(object):
        """!Inner class for CreateKeyRequest to hold groups of counts and attributes"""

        def __init__(self, ref, count, attributes, mutableattributes = None):
            """!Constructor

            @param
                ref (String) A string value that will be included with the created 
                    keys that can be used to match them with the provided attributes
            @param
                count (int) The number of keys with the given attributes to be created
            @param
                attributes (KeyAttributesDict) The attributes to be set for these keys
            @param
                mutableattributes (KeyAttributesDict) The mutable attributes to be set
                    for these keys
            """
            ## ref (String) A string value that will be included with the created keys that can be used to match them with the provided attributes
            self.ref = ref
            ## count (int) The number of keys with the given attributes to be created
            self.count = count
            ## attributes (KeyAttributesDict) The attributes to be set for these keys
            self.attributes = attributes
            ## mutableattributes (KeyAttributesDict) The mutable attributes to be set for these keys
            self.mutableattributes = mutableattributes
    def __init__(self, metadata = None, simulate = False):
        """!Constructor for CreateKeyRequest.
   
        @param
            metadata (MetadataDict) Optional metadata to add to the call
        @param
            simulate (boolean) If true, allows for testing of whether a create 
                call would succeed without creating any keys. The response will
                contain keys that are allowed to be created with empty ID and
                key byte values.
        """

        ##(dict) metadata associated with the request
        self.metadata = metadata
        ##(bool) whether to check if the key is retrievable, or actually retrieve it.
        self.simulate = simulate
        ##(list) list of keys to request
        self.keys = []

    def addkeyrequest(self, ref, count, attributes, mutableattributes = None):
        """!Method for adding a request for a number of keys with given attributes to the multiple key request
        
        @param
            ref (String) A string value that will be included with the created 
                keys that can be used to match them with the provided attributes
        @param
            count (int) The number of keys with the given attributes to be created
        @param
            attributes (KeyAttributesDict) The attributes to be set for these keys
        @param
            mutableattributes (KeyAttributesDict) The mutable attributes to be set
                for these keys
        @return
            None
        """
        self.keys.append(self.KeyRequest(ref, count, attributes, mutableattributes))

    @staticmethod
    def _marshalToC(pyCreateKeysRequest):
        if pyCreateKeysRequest is None:
            return None
        cCreateKeysRequest = _private.cLib.ionic_create_keys_request_create()
        _private.cLib.ionic_create_keys_request_set_simulation(cCreateKeysRequest, pyCreateKeysRequest.simulate == True)
        if not pyCreateKeysRequest.metadata is None:
            _private.cLib.ionic_create_keys_request_set_metadata(cCreateKeysRequest, MetadataDict._marshalToC(pyCreateKeysRequest.metadata))
        for key in pyCreateKeysRequest.keys:
            _private.cLib.ionic_create_keys_request_add(cCreateKeysRequest, 
                _private.CMarshalUtil.stringToC(key.ref),
                KeyAttributesDict._marshalToC(key.attributes),
                KeyAttributesDict._marshalToC(key.mutableattributes),
                key.count
            )
        return cCreateKeysRequest

    @staticmethod
    def _marshalFromC(cCreateKeysRequest):
        if cCreateKeysRequest is None:
            return None
        cMetadata = _private.OWNED_POINTER(_private.CMetadataMap)()
        _private.cLib.ionic_create_keys_request_get_metadata(cCreateKeysRequest, _private.byref(cMetadata))
        cSimulate = c_bool()
        _private.cLib.ionic_create_keys_request_get_simulation(cCreateKeysRequest, _private.byref(cSimulate))
        pyCreateKeysRequest = CreateKeysRequest(MetadataDict._marshalFromC(cMetadata.contents), cSimulate)

        cCount = c_int()
        _private.cLib.ionic_create_keys_request_get_count(cCreateKeysRequest, _private.byref(cCount))
        for i in range(cCount.value):
            cKCount = c_int()
            cRef = _private.POINTER(c_char)()
            cAttribute = _private.OWNED_POINTER(_private.CAttributesMap)()
            cMutable = _private.OWNED_POINTER(_private.CAttributesMap)()
            _private.cLib.ionic_create_keys_request_get(cCreateKeysRequest, i, 
                _private.byref(cRef),
                _private.byref(cAttribute),
                _private.byref(cMutable),
                _private.byref(cKCount)
            )
            pyCreateKeysRequest.addkeyrequest(_private.CMarshalUtil.stringFromC(cRef), cKCount.value,
                KeyAttributesDict._marshalFromC(cAttribute),
                KeyAttributesDict._marshalFromC(cMutable)
            )
        return pyCreateKeysRequest

class ResourceRequest(object):
    """!Class used to request generic resource object(s)."""
    def __init__(self, refid, resourceid, args = None):
        """!Constructor which assigns all internal variables.
            
        @param
            refid (string) The resource ID
        @param
            resourceid (string) The resource ID
        @param
            args (string) The request arguments
        """

        ##(string) The reference ID
        self.refid = refid
        ##(string) The resource ID
        self.resourceid = resourceid
        ##(string) The request arguments
        self.args = args
        
    def __repr__(self):
        return '<ResourceRequest resourceid="{0}" args="{1}">'.format(self.resourceid, self.args)
    
    @staticmethod
    def _marshalToC(pyResourceRequest):
        if pyResourceRequest is None:
            return None

        cRequest = _private.CResourceRequest()
        cRequest.pszRefId = _private.CMarshalUtil.stringToC(pyResourceRequest.refid)
        cRequest.pszResourceId = _private.CMarshalUtil.stringToC(pyResourceRequest.resourceid)
        cRequest.pszArgs = _private.CMarshalUtil.stringToC(pyResourceRequest.args)
        return cRequest

    @staticmethod
    def _marshalToCArray(pyResourceRequestList):
        if pyResourceRequestList is None:
            return None

        cRequestArray = (_private.POINTER(_private.CResourceRequest) *len(pyResourceRequestList))()
        i = 0
        for request in pyResourceRequestList:
            cRequestArray[i] = _private.pointer(ResourceRequest._marshalToC(request))
            i = i + 1
        return cRequestArray

class ResourceResponseList(list):
    """!List of generic resource object(s) with convenience functions for
    searching by refid.
    """
    def __repr__(self):
        return '<ResourceResponseList ' + super(ResourceResponseList,self).__repr__() + '>'
    
    def getrefids(self):
        """!Get the list of reference IDs in this response.
            
        @return
            The list of reference IDs.
        """
        return list(map( lambda response: response.refid, self))
    
    def findrefid(self, refid):
        """!Find a resource response in this list by reference ID.
            
        @param
            refid (string) The reference id to search for
        @return
            The resource response or None if it was not found in the list.
            """
        for resp in self:
            if resp.refid == refid:
                return resp
        return None
    
    @staticmethod
    def _marshalFromC(cRespArray):
        if cRespArray is None:
            return None

        pyResourceResponseList = ResourceResponseList()
        for i in range(cRespArray.nSize):
            pyResourceResponseList.append(ResourceResponse._marshalFromC(
                                                           cRespArray.ppResponseArray[i].contents))
        return pyResourceResponseList

class ResourceResponse(object):
    """!Class used to return generic resource object(s)."""
    def __init__(self, refid, data, error = None):
        """!Constructor which assigns all internal variables.
            
        @param
            refid (string) The reference ID
        @param
            data (string) The resource
        @param
            error (string) The error text, if there was an error
        """

        ##(string) The reference ID
        self.refid = refid
        ##(string) The resource
        self.data = data
        ##(string) The error text, if there was an error
        self.error = error
        
    def __repr__(self):
        return '<ResourceResponse refid="{0.refid}" data="{0.data}" error="{0.error}">'.format(self)
    
    @staticmethod
    def _marshalFromC(cResp):
        if cResp is None:
            return None
        pyResourceResponse = ResourceResponse(
            _private.CMarshalUtil.stringFromC(cResp.pszRefId),
            _private.CMarshalUtil.stringFromC(cResp.pszData),
            _private.CMarshalUtil.stringFromC(cResp.pszError))
        return pyResourceResponse

class KeyspaceResponse(object):
    """!Class used to return keyspace object(s)."""
    def __init__(self, fqdn, tenantId, enrollUrl, apiUrl = None):
        """!Constructor which assigns all internal variables.
            
        @param
            fqdn (string) The fully qualified domain name
        @param
            tenantId (string) The tenant ID
        @param
            enrollUrl (string) The enrollment URL
        @param
            apiUrl (string) The main API URL, if available
        """

        ##(string) The fully qualified domain name
        self.fqdn = fqdn
        ##(string) The tenant ID
        self.tenantId = tenantId
        ##(string) The enrollment URL
        self.enrollUrl = enrollUrl
        ##(string) The main API URL, if available
        self.apiUrl = apiUrl
    
    def __repr__(self):
        return '<KeyspaceResponse fqdn="{0.fqdn}" tenantId="{0.tenantId}" enrollUrl="{0.enrollUrl}">'.format(self)
    
    @staticmethod
    def _marshalFromC(cResp):
        if cResp is None:
            return None
        pyKeyspaceResponse = KeyspaceResponse(
                                _private.CMarshalUtil.stringFromC(cResp.pszFqdn),
                                _private.CMarshalUtil.stringFromC(cResp.pszTenantId),
                                _private.CMarshalUtil.stringFromC(cResp.pszEnrollUrl),
                                _private.CMarshalUtil.stringFromC(cResp.pszApiUrl))
        return pyKeyspaceResponse

class AgentConfig(object):
    """!Configuration object used by Agent.
    """
    def __init__(self, useragent=None, httpimpl=None, httptimeoutsecs=None, maxredirects=None):
        """!Initializes the agent config object with provided inputs.

        @param
            useragent (string, optional): The User-Agent header value to
                                          use for HTTP communication.
        @param
            httpimpl (string, optional): The name of the HTTP
                                        implementation to use.
        @param
            httptimeoutsecs (int, optional): The HTTP timeout in seconds
                                             (default 30).
        @param
            maxredirects (int, optional): The maximum number of HTTP
                                          redirects (default 2).
        """

        ##(string) The User-Agent header value to use for HTTP communication
        self.useragent = (useragent if useragent is not None and useragent != '' else 'Python SDK Client')
        ##(string) The name of the HTTP implementation to use
        self.httpimpl = (httpimpl if httpimpl is not None else '')
        ##(int) The HTTP timeout in seconds (default 30)
        self.httptimeoutsecs = (httptimeoutsecs if httptimeoutsecs is not None else 30)
        ##(int) The maximum number of HTTP redirects (default 2)
        self.maxredirects = (maxredirects if maxredirects is not None else 2)
        
    def __repr__(self):
        return '<AgentConfig useragent="{0.useragent}" httptimeoutsecs="{0.httptimeoutsecs}">'.format(self)

    @staticmethod
    def _marshalFromC(cConfig):
        if cConfig is None:
            return None
        
        pyConfig = AgentConfig(
            _private.CMarshalUtil.stringFromC(cConfig.pszUserAgent),
            _private.CMarshalUtil.stringFromC(cConfig.pszHttpImpl),
            cConfig.nHttpTimeoutSecs,
            cConfig.nMaxRedirects)
        return pyConfig
        
    @staticmethod
    def _marshalToC(pyConfig):
        if pyConfig is None:
            return None
        
        cConfig = _private.CAgentConfig()
        cConfig.pszUserAgent = _private.CMarshalUtil.stringToC(pyConfig.useragent)
        cConfig.pszHttpImpl = _private.CMarshalUtil.stringToC(pyConfig.httpimpl)
        cConfig.nHttpTimeoutSecs = pyConfig.httptimeoutsecs
        cConfig.nMaxRedirects = pyConfig.maxredirects
        return cConfig

class Agent(AgentKeyServicesBase):
    """!Agent class performs all client/server communication with
    Ionic.com.
    """
    def __init__(self, agentconfig = None, profilepersistor = None, loadprofiles = True, cloneagent = None, profilemanager = None):
        """!An Agent object can be initialized with different profile
        persistors and a config object, or defaults

        By default an Agent will load profiles from the platform-specific
        device profile persistor (if one exists for the platform, otherwise
        an AGENT_NO_PROFILE_PERSISTOR IonicException may be thrown if no other
        persistor is specified).  Loading can be disabled, or a 
        ionicsdk.common.DeviceProfilePersistorPlaintextFile,
        ionicsdk.common.DeviceProfilePersistorPasswordFile, or
        ionicsdk.common.DeviceProfilePersistorAesGcmFile can be used to load
        profiles from a file.

        Alternatively, an ionicsdk.profilemanager.ProfileManager can be
        provided as a source from which to copy profiles without the additional
        overhead of loading them from the system each time.

        An AgentConfig object or configuration file can specify network
        communication parameters.

        @param
            agentconfig (AgentConfig, optional): An AgentConfig object
                can specify network configuration parameters.
        @param
            profilepersistor (DeviceProfilePersistorBase, optional): A
                device profile persistor.  If unspecified or None, will
                use platform default which will be shared across all
                ionic-enabled applications.  Subclasses are available to
                load profiles from plaintext, passworded, or encrypted
                files.
        @param
            loadprofiles (bool, optional): Set to false to prevent
                loading of profiles.  Profiles must be added or loaded
                using Agent.*profile[s] methods before using the Agent
                object for network communication.
        @param
            cloneagent (Agent, optional): If present, this overrides the 
            other parameters and an Agent is created by copying the one 
            passed. This is useful in a multithread environment.
        @param
            profilemanager (ProfileManager, optional): If present, this
            will not use the persistor and instead copy profiles and 
            current active profile from the argument into the new Agent.
        """
        self._cAgent = None
        self._cServerResponse = None
        
        if cloneagent:
            self._cAgent = _private.cLib.ionic_agent_clone(cloneagent._cAgent)
        else:
            cAgentConfig = AgentConfig._marshalToC(agentconfig)
            if profilemanager:
                self._cAgent = _private.cLib.ionic_agent_create_with_manager(profilemanager._cProfileManager, cAgentConfig)
            else:
                if loadprofiles:
                    pp = None
                    if profilepersistor:
                        if not isinstance(profilepersistor, DeviceProfilePersistorBase):
                            raise Exception('profilepersistor must be an instance of DeviceProfilePersistorBase')
                        pp = profilepersistor._cPersistor
                    self._cAgent = _private.cLib.ionic_agent_create(pp, cAgentConfig)
                else:
                    self._cAgent = _private.cLib.ionic_agent_create_without_profiles(cAgentConfig)

            if self._cAgent:
                _private.cLib.ionic_agent_set_metadata(self._cAgent, _private.CMarshalUtil.stringToC("ionic-agent"), _private.CMarshalUtil.stringToC("IonicSDK/1 Python/" + _private.IONIC_SDK_VERSION))
        
        if not self._cAgent:
            raise IonicException('Failed to create an Agent object. Check the log to know the reason for this error (common cause is failure to initialize internally).', IonicError.AGENT_ERROR)

    def getLastServerResponse(self):
        """!Return the Server Response object from the last Agent call.
            @return
                A valid ServerResponse object or None if no server calls have been made yet.
        """
        return ServerResponse._marshalFromC(self._cServerResponse)

    def getprofilemanager(self):
        """!Get the ionicsdk.profilemanager.ProfileManager object for this agent.
            @return
                A ProfileManager object that can be modified to change the agents behavior.
        """
        return  ProfileManager(_cProfileManager=_private.cLib.ionic_agent_get_profile_manager(self._cAgent))

    # active profile
    def hasactiveprofile(self):
        """!(DEPRECATED) Determine if any device profile is active. 
        @deprecated This function has moved to ionicsdk.profilemanager.ProfileManager, accessible through
            getprofilemanager().  Time for removal is TBD.
        @return
            True if an active profile is loaded, False otherwise
        """
        return _private.cLib.ionic_agent_has_active_profile(self._cAgent)

    def setactiveprofile(self, deviceid):
        """!(DEPRECATED) Set the current device profile of the agent.
        @deprecated This function has moved to ionicsdk.profilemanager.ProfileManager, accessible through
            getprofilemanager().  Time for removal is TBD.
        @param
            deviceid (str): A string device id of a loaded profile to
                set as the active profile for the agent. If a
                DeviceProfile object is given instead it will use the
                deviceid parameter of the object as the string source.
        @return
            None, raises an exception on errors
        """
        if type(deviceid) is DeviceProfile:
            deviceid = deviceid.deviceid
        
        _private.cLib.ionic_agent_set_active_profile(self._cAgent,
                          _private.CMarshalUtil.stringToC(deviceid))

    def getactiveprofile(self):
        """!(DEPRECATED) Get the current device profile of the agent.
        @deprecated This function has moved to ionicsdk.profilemanager.ProfileManager, accessible through
            getprofilemanager().  Time for removal is TBD.
        @return
            Returns the active device profile object. If no active
            profile is set, then None will be returned. You can also
            call Agent.hasactiveprofile() to determine if there is an
            active profile.
        """
        cProfile = _private.cLib.ionic_agent_get_active_profile(self._cAgent)
        return (DeviceProfile._marshalFromC(cProfile.contents) if cProfile else None)

    # profile management
    def hasanyprofiles(self):
        """!(DEPRECATED) Determine if any device profiles are loaded.
        @deprecated This function has moved to ionicsdk.profilemanager.ProfileManager, accessible through
            getprofilemanager().  Time for removal is TBD.
        @return
            True if an any profile is loaded, False otherwise
        """
        return _private.cLib.ionic_agent_has_any_profiles(self._cAgent)

    def getallprofiles(self):
        """!(DEPRECATED) Get all available device profiles.
        @deprecated This function has moved to ionicsdk.profilemanager.ProfileManager, accessible through
            getprofilemanager().  Time for removal is TBD.
        @return
            Returns a DeviceProfileList (subclass of list) of all device
                profile objects. 
        """
        cNumProfiles = _private.c_size_t(0)
        cProfileArray = _private.cLib.ionic_agent_get_all_profiles(self._cAgent,
                                          _private.byref(cNumProfiles))
        
        return DeviceProfileList._marshalFromC(cProfileArray, cNumProfiles)

    def addprofile(self, deviceprofile, makeactive = False):
        """!(DEPRECATED) Add a device profile to the agent device profile collection.
        @deprecated This function has moved to ionicsdk.profilemanager.ProfileManager, accessible through
            getprofilemanager().  Time for removal is TBD.
        @param
            deviceprofile (DeviceProfile): The device profile object.
        @param
            makeactive (bool, optional): If true, then this profile will
                          be set as the active profile (default: False).
        
        @return
            None, raises an exception on errors
        """
        if type(deviceprofile) is not DeviceProfile:
            raise TypeError('addprofile expected a DeviceProfile.  See createdevice for more information.')
        
        cDeviceProfile = DeviceProfile._marshalToC(deviceprofile)
        _private.cLib.ionic_agent_add_profile(self._cAgent, cDeviceProfile,
                                                     bool(makeactive))

    def removeprofile(self, deviceid):
        """!(DEPRECATED) Remove a device profile from the agent device profile list.
        @deprecated This function has moved to ionicsdk.profilemanager.ProfileManager, accessible through
            getprofilemanager().  Time for removal is TBD.
        @param
            deviceid (string): The device id of the profile to remove.
        @return
            None, raises an exception on errors
        """
        if type(deviceid) is DeviceProfile:
            deviceid = deviceid.deviceid
        _private.cLib.ionic_agent_rmv_profile(self._cAgent,
                                              _private.CMarshalUtil.stringToC(deviceid))

    def updateprofile(self, deviceid=None, knsProviderUrl=None):
        """!Finds the deviceId (or uses the active profile), gets the current KNS information
            for the profile keyspace, and then updates the profile (and active profile if needed).
            The user is encouraged to save the profile afterward.

        @param
            deviceid (string): The device id of the profile to update, optional, uses active
            profile by default.
        @param
            knsProviderUrl (unicode): The KNS provider url, optional, defaults to https://api.ionic.com
        @return
            None, raises an exception on errors
        """
        if type(deviceid) is DeviceProfile:
            deviceid = deviceid.deviceid
        _private.cLib.ionic_agent_update_profile_from_kns(self._cAgent,
                                              _private.CMarshalUtil.stringToC(deviceid),
                                              _private.CMarshalUtil.stringToC(knsProviderUrl))

    def getprofileforkeyid(self, keyid):
        """!(DEPRECATED) Determine which device profile is associated with the
        provided key ID.
        @deprecated This function has moved to ionicsdk.profilemanager.ProfileManager, accessible through
            getprofilemanager().  Time for removal is TBD.
        @param
            keyid (string): The key ID for which to retrieve the
                            associated device profile.

        @return
            The DeviceProfile associated with the provided key ID, or
            None if not found.
        """
        cKeyId = _private.CMarshalUtil.stringToC(keyid)
        cProfile = _private.cLib.ionic_agent_get_profile_for_key_id(self._cAgent, cKeyId)
        return (DeviceProfile._marshalFromC(cProfile.contents) if cProfile else None)

    # agent metadata management
    def getmetadata(self):
        """!Get metadata dictionary that will be included with requests
        from this agent.
        
        @return
            The metadata dictionary as a Python MetadataDict instance
        """
        cMeta = _private.cLib.ionic_agent_get_metadata_all(self._cAgent)
        return MetadataDict._marshalFromC(cMeta)

    def setmetadata(self, metadatadict):
        """!Set metadata dictionary to be included with requests from this agent.

        @param
            metadatadict (MetadataDict, optional): The metadata properties to send
                along with the HTTP request.
        @return
            None, raises an exception on errors
        """
        cMeta = MetadataDict._marshalToC(metadatadict)
        _private.cLib.ionic_agent_set_metadata_all(self._cAgent, cMeta)

    def addmetadata(self, metadatadict):
        """!Add metadata dictionary to any meta data already on the agent.
        A metadata key passed in here with an empty value is removed from the agent.

        @param
            metadatadict (MetadataDict, optional): The metadata properties to send
                along with the HTTP request.
        @return
            None, raises an exception on errors
        """
        cMeta = MetadataDict._marshalToC(metadatadict)
        _private.cLib.ionic_agent_add_metadata(self._cAgent, cMeta)

    # profile persistence
    def loadprofiles(self, persistor):
        """!(DEPRECATED) Load device profiles using the provided profile persistor.
        
        Attempts to load device profiles using the specified profile
        persistor.

        If loading is successful, all existing profiles associated with
        the agent will be discarded in favor of the newly loaded
        profiles.  The active profile provided by the persistor will
        replace the previous active profile (if any).  It is also
        possible that the persistor does not provide an active profile,
        in which case the agent object will be left without an active
        profile.
        
        If loading is not successful, then no changes are made to the
        state of the agent.

        @deprecated This function has moved to ionicsdk.profilemanager.ProfileManager, accessible through
            getprofilemanager().  Time for removal is TBD.
        @param
            persistor (DeviceProfilePersistorBase): The device profile
                                                    persistor.
        @return
            None, raises an exception on errors
        """
        _private.cLib.ionic_agent_load_profiles(self._cAgent, persistor._cPersistor)

    def saveprofiles(self, persistor):
        """!(DEPRECATED) Save device profiles using the specified profile persistor.

        @deprecated This function has moved to ionicsdk.profilemanager.ProfileManager, accessible through
            getprofilemanager().  Time for removal is TBD.
        @param
            persistor (DeviceProfilePersistorBase): The device profile
                                                persistor.
        @return
            None, raises an exception on errors
        """
        _private.cLib.ionic_agent_save_profiles(self._cAgent, persistor._cPersistor)

    # network APIs
    def createdevice(self, server, etag, token, uidauth, rsa_pub_key_base64, profilename = ''):
        """!Creates (registers) a device with Ionic.com.

        This method makes an HTTP call to Ionic.com to register a
        device.
        
        It is the responsibility of the caller to save this new profile
        to a persistent store by calling Agent.saveprofiles() or by
        saving it in another way of their choice.

        @param
            server (string): The server to be used for the device
                             registration call.
        @param
            etag (string): The ETag (enrollment tag.
        @param
            token (string): The token.
        @param
            uidauth (string): The UIDAuth.
        @param
            rsa_pub_key_base64 (string): The Base64 encoded RSA public
                    key belonging to the EI (Enrollment Infrastructure).
        @param
            profilename (string, optional): Device profile name to be
                        used for the device being created (default: '').
                        
        @return
            A device profile
        """
        # inputs
        cServer = _private.CMarshalUtil.stringToC(server)
        cETag = _private.CMarshalUtil.stringToC(etag)
        cToken = _private.CMarshalUtil.stringToC(token)
        cUidAuth = _private.CMarshalUtil.stringToC(uidauth)
        cRsaPubKeyBase64 = _private.CMarshalUtil.stringToC(rsa_pub_key_base64)
        cProfileName = _private.CMarshalUtil.stringToC(profilename)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cProfile = _private.OWNED_POINTER(_private.CDeviceProfile)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_create_device(
                self._cAgent,
                cServer,
                cETag,
                cToken,
                cUidAuth,
                cRsaPubKeyBase64,
                cProfileName,
                _private.byref(cProfile),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

        # marshal C output to Python
        return DeviceProfile._marshalFromC(cProfile.contents)

    def createkey(self, attributes = None, metadata = None, mutableAttributes = None):
        """!Creates a single protection key with attributes through Ionic.com.
        
        This method makes an HTTP call to Ionic.com to create a
        protection key with attributes.
        
        @param
            attributes (KeyAttributesDict, optional): The protection key
                    attributes to use for creating the protection key.
        @param
            metadata (MetadataDict, optional): The metadata properties to send
                    along with the HTTP request.
        @param
            mutableAttributes (KeyAttributesDict, optional): The protection key
                    mutable attributes to use for creating the protection key.
        
        @return
            A KeyData object with the newly created protection key from Ionic.com.
        """
        # inputs
        cAttributes = KeyAttributesDict._marshalToC(attributes)
        cMutableAttributes = KeyAttributesDict._marshalToC(mutableAttributes)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cKeyData = _private.OWNED_POINTER(_private.CKeyData)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_create_key2(
                self._cAgent,
                cAttributes,
                cMutableAttributes,
                cMetadata,
                _private.byref(cKeyData),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
        
        # marshal C output to Python
        return KeyData._marshalFromC(cKeyData.contents)

    def createkeys(self, keycount, attributes = None, metadata = None, mutableAttributes = None):
        """!Creates protection keys through Ionic.com.
        
        This method makes an HTTP call to Ionic.com to create protection
        keys.
        
        NOTE: please limit to 1,000 keys per request, otherwise the server will return an error.
        @param
            keycount (int): The number of keys to create.
        @param
            attributes (KeyAttributesDict, optional): The protection key
                attributes to use for creating the protection keys.
        @param
            metadata (MetadataDict, optional): The metadata properties
                to send along with the HTTP request.
        @param
            mutableAttributes (KeyAttributesDict, optional): The protection key
                mutable attributes to use for creating the protection key.
        
        @return
            The KeyDataList of newly created protection keys from Ionic.com.
        """
        # inputs
        cAttributes = KeyAttributesDict._marshalToC(attributes)
        cMutableAttributes = KeyAttributesDict._marshalToC(mutableAttributes)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cKeyArray = _private.OWNED_POINTER(_private.CKeyDataArray)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_create_keys2(
                self._cAgent,
                cAttributes,
                cMutableAttributes,
                keycount,
                cMetadata,
                _private.byref(cKeyArray),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
        
        # marshal C output to Python
        return KeyDataList._marshalFromC(cKeyArray.contents)

    def createkeys2(self, createkeysrequest):
        """!Creates protection keys with various attribute sets through Ionic.com.
        
        This method makes an HTTP call to Ionic.com to create protection
        keys.
        
        NOTE: please limit to 1,000 keys per request, otherwise the server will return an error.
        @param
            createkeysrequest (CreateKeysRequest) A request object that has had
                all the desired key attribute sets and other data added to it.
        
        @return
            The KeyDataList of newly created protection keys from Ionic.com.
        """
        # inputs
        cReq = CreateKeysRequest._marshalToC(createkeysrequest)
                
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cKeyArray = _private.OWNED_POINTER(_private.CKeyDataArray)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_create_keys3(
                self._cAgent,
                cReq,
                _private.byref(cKeyArray),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
        
        # marshal C output to Python
        return RefKeyDataList._marshalFromC(cKeyArray.contents)

    def getkey(self, keyid, metadata = None):
        """!Gets a single protection key from Ionic.com.

        This method makes an HTTP call to Ionic.com to get a protection
        key.

        @param
            keyid (string): The protection key ID to fetch.
        @param
            metadata (MetadataDict, optional): The metadata properties
                to send along with the HTTP request.

        @return
            A KeyData object containing the requested key.
        """
        # inputs
        cKeyId = _private.CMarshalUtil.stringToC(keyid)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cKeyData = _private.OWNED_POINTER(_private.CKeyData)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_get_key(self._cAgent,
                cKeyId,
                cMetadata,
                _private.byref(cKeyData),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

        # marshal C output to Python
        return KeyData._marshalFromC(cKeyData.contents)

    def getkeys(self, keyids, metadata = None):
        """!Gets protection keys from Ionic.com.

        This method makes an HTTP call to Ionic.com to get protection
        keys.

        NOTE: please limit to 1,000 keys per request, otherwise the server will return an error.
        @param
            keyids (string): The list of protection key IDs to fetch.
        @param
            metadata (MetadataDict, optional): The metadata properties
                                    to send along with the HTTP request.

        @return
            A list of keys that were successfully retrieved.  It is
            important to note that even if the function succeeds, it
            does NOT mean that any or all of the requested keys were
            provided. The caller can iterate through the response object
            and determine which keys were returned by looking at the key
            ID property (KeyData.id).
        """
        # inputs
        nKeyCount = len(keyids)
        cKeyIdArray = _private.CMarshalUtil.stringArrayToC(keyids)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cKeyArray = _private.OWNED_POINTER(_private.CKeyDataArray)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_get_keys(
                self._cAgent,
                cKeyIdArray,
                nKeyCount,
                cMetadata,
                _private.byref(cKeyArray),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
        
        # marshal C output to Python
        return KeyDataList._marshalFromC(cKeyArray.contents)

    def getkeys2(self, keyids, externalkeyids, metadata = None):
        """!Gets protection keys from Ionic.com.
            
        This method makes an HTTP call to Ionic.com to get protection
        keys.
        
        NOTE: please limit to 1,000 keys per request, otherwise the server will return an error.
        @param
            keyids (string): The list of protection key IDs to fetch.
        @param
            externalkeyids (string): Alternate list of external ids of
                keys to fetch.  External ids reference keys with external 
                ids in their AttributeMap.
        @param
            metadata (MetadataDict, optional): The metadata properties
                to send along with the HTTP request.
        
        @return
            A tuple containing:            
            - A list of keys that were successfully retrieved.  It is
                important to note that even if the function succeeds, it
                does NOT mean that any or all of the requested keys were
                provided. The caller can iterate through the response object
                and determine which keys were returned by looking at the key
                ID property (KeyData.id).            
            - A list of Query results. Each Query Result contains the external
                key id and either a list of matching key ids (ionic) or an error
                code and error message. If a key just isn't found, there will
                be no Query result for it.                
            - A list of per Key Errors. (Almost always empty) Each Error result
                is generated when an error is generated from a specific key id
                such as a privilege error. Each Error is a dict containing a
                key id, a client error code, a server error code, and a server 
                message
        """
        # inputs
        nKeyCount = len(keyids)
        cKeyIdArray = _private.CMarshalUtil.stringArrayToC(keyids)
        nExternalKeyCount = len(externalkeyids)
        cExternalKeyIdArray = _private.CMarshalUtil.stringArrayToC(externalkeyids)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cKeyArray = _private.OWNED_POINTER(_private.CKeyDataArray)()
        cGetKeyQueryList = _private.OWNED_POINTER(_private.CGetKeyQueryList)()
        cGetKeyErrorList = _private.OWNED_POINTER(_private.CGetKeyErrorList)()
        
        # call into C library to perform the work
        try:
            res = _private.cLib.ionic_agent_get_keys2(
                                               self._cAgent,
                                               cKeyIdArray,
                                               nKeyCount,
                                               cExternalKeyIdArray,
                                               nExternalKeyCount,
                                               cMetadata,
                                               _private.byref(cKeyArray),
                                               _private.byref(cGetKeyQueryList),
                                               _private.byref(self._cServerResponse),
                                               _private.byref(cGetKeyErrorList))
            if res:
                _private.raiseExceptionWithServerResponse(self._cServerResponse, IonicException("Bad return code", res))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
        
        # marshal C output to Python
        return (KeyDataList._marshalFromC(cKeyArray.contents), GetKeyQueryList._marshalFromC(cGetKeyQueryList.contents), GetKeyErrorList._marshalFromC(cGetKeyErrorList.contents))

    def updatekey(self, updateKeyData, metadata = None):
        """!Updates the mutable portion of the attributes on a protection
            key at Ionic.com.
            
            This method makes an HTTP call to Ionic.com to update protection
            keys.
            
            @param
                updateKeyData (UpdateKeyData): The key to be updated with mutable
                            properties changed
            @param
                metadata (MetadataDict, optional): The metadata properties to send
                            along with the HTTP request.
            
            @return
                A KeyData object containing the updated key.
            """

        cUpdateKeyData = UpdateKeyData._marshalToC(updateKeyData)
        cMetadata = MetadataDict._marshalToC(metadata)

        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cKeyData = _private.OWNED_POINTER(_private.CKeyData)()

        # call into C library to perform the work
        try:
            result = _private.cLib.ionic_agent_update_key(
                self._cAgent,
                cUpdateKeyData,
                cMetadata,
                _private.byref(cKeyData),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

        if result:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, Exception("Bad return code", result))
        
        # marshal C output to Python
        return KeyData._marshalFromC(cKeyData.contents)

    def updatekeys(self, KeyDataArray, metadata = None):
        """!Updates the mutable portion of the attributes on a list of protection
            keys at Ionic.com.
            
            This method makes an HTTP call to Ionic.com to update protection
            keys.
            
            @param
                KeyDataArray (UpdateKeyDataList): The keys to be updated with mutable
                    properties changed
            @param
                metadata (MetadataDict, optional): The metadata properties to send
                    along with the HTTP request.
            
            @return
                A KeyDataList object containing the updated keys.
            """

        cKeyDataArray = UpdateKeyDataList._marshalToC(KeyDataArray)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cKeyDataArrayOut = _private.OWNED_POINTER(_private.CKeyDataArray)()
        
        # call into C library to perform the work
        try:
            result = _private.cLib.ionic_agent_update_keys(
                                                 self._cAgent,
                                                 cKeyDataArray,
                                                 cMetadata,
                                                 _private.byref(cKeyDataArrayOut),
                                                 _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
    
        if result:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, Exception("Bad return code", result))
    
        # marshal C output to Python
        return KeyDataList._marshalFromC(cKeyDataArrayOut.contents)

    def logmessage(self, msgtype, datajson, metadata = None):
        """!Logs a single messages to Ionic.com.

        This method makes an HTTP call to Ionic.com to post a single log
        message.

        @param
            msgtype (string): The message type string.
        @param
            datajson (string): The message data in JSON format.
        @param
            metadata (MetadataDict, optional): The metadata properties
                                    to send along with the HTTP request.
        @return
            None
        """
        # inputs
        cMessageType = _private.CMarshalUtil.stringToC(msgtype)
        cDataJson = _private.CMarshalUtil.stringToC(datajson)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_log_message(
                self._cAgent,
                cMessageType,
                cDataJson,
                cMetadata,
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

    def logmessages(self, msgtypes, datajsons, metadata = None):
        """!Logs one or more messages to Ionic.com.

        This method makes an HTTP call to Ionic.com to post one or more
        log messages.

        @param
            msgtypes (list[string]): The list of message type strings.
        @param
            datajsons (list[string]): The list of message data strings
                                      in JSON format.
        @param
            metadata (MetadataDict, optional): The metadata properties
                                    to send along with the HTTP request.
        @return
            None
        """
        nMsgCount = len(msgtypes)
        nDataCount = len(datajsons)
        
        # ensure the two lists are of the same size
        if nMsgCount != nDataCount:
            raise ValueError('The number of message types does not match the number of json objects')
        elif nMsgCount <= 0:
            raise ValueError('The number of message types must be greater than zero')
        
        # inputs
        cMessageTypeArray = _private.CMarshalUtil.stringArrayToC(msgtypes)
        cDataJsonArray = _private.CMarshalUtil.stringArrayToC(datajsons)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_log_messages(self._cAgent,
                cMessageTypeArray,
                cDataJsonArray,
                nMsgCount,
                cMetadata,
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

    def createidassertion(self, foruri, nonce, metadata = None):
        """!Creates an identity assertion issued by an Ionic Key Server.
        
        This method makes an HTTP call to Ionic.com to request the
        creation of an identity assertion by an Ionic Key Server.  This
        assertion is useful for proving that the machine which requested
        the assertion is in fact a registered device in the Ionic Key
        Server. The Ionic Key Server which creates the assertion is the
        one associated with the currently active profile of this agent
        object (see Agent.getactiveprofile()).

        @param
            foruri (string): The URI for the assertion.
        @param
            nonce (string): The nonce used for this assertion.
        @param
            metadata (MetadataDict, optional): The metadata properties
                                    to send along with the HTTP request.
                                    
        @return
            A string containing the assertion
        """
        # inputs
        cForUri = _private.CMarshalUtil.stringToC(foruri)
        cNonce = _private.CMarshalUtil.stringToC(nonce)
        cMetadata = MetadataDict._marshalToC(metadata)
        
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cAssertion = _private.OWNED_POINTER(_private.c_char)()
        
        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_create_id_assertion(
                self._cAgent,
                cForUri,
                cNonce,
                cMetadata,
                _private.byref(cAssertion),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
        
        # marshal C output to Python
        return _private.CMarshalUtil.stringFromC(cAssertion)

    def validateassertion(self, keyspace, assertionBase64, foruri = None, nonce = None, knsurl = None):
        """!Given a base 64 encoded Ionic assertion, validate it against the keyspace public key.
            This method makes an HTTP call to Ionic.com to get keyspace information including the public key.
            It checks the assertion formating, checks the valid time window, and finally checks the RSA
            signature against the public key for the keyspace.

        @param
            keyspace (string): The keyspace id.
        @param
            assertionBase64 (string): The Ionic formatted base 64 encoded assertion.
        @param
            foruri (string): An optional recipient string. 
            It should match the one passed when creating the assertion.
            If this option is left off, recipient checks are skipped.
        @param
            nonce (string): An optional nonce string. 
            It should match the one passed when creating the assertion.
            If this option is left off, the validation uses a default value.
            If this value is incorrect, validation will fail.
        @param
           knsurl (string): An optional alternate kns provider url, defaults to https://api.ionic.com

        @return
            None, function will throw an exception if it fails to validate.
        """

        cKeyspace = _private.CMarshalUtil.stringToC(keyspace)
        cAssertionBase64 = _private.CMarshalUtil.stringToC(assertionBase64)
        cForUri = _private.CMarshalUtil.stringToC(foruri)
        cNonce = _private.CMarshalUtil.stringToC(nonce)
        cknsurl = _private.CMarshalUtil.stringToC(knsurl)

        _private.cLib.ionic_agent_validate_assertion(self._cAgent, cKeyspace, cAssertionBase64, cForUri, cNonce, cknsurl)

    def validateAssertionViaEnrollment(self, enrollmentUrl, assertionBase64, foruri = None, nonce = None):
        """!Given a base 64 encoded Ionic assertion, validate it against the keyspace public key.
            This method makes an HTTP call to your enrollment server to get the public key.
            It checks the assertion formatting, checks the valid time window, and finally checks the RSA
            signature against the public key for the keyspace.

        @param
            enrollmentUrl (string): The enrollment URL for the given keyspace.
        @param
            assertionBase64 (string): The Ionic formatted base 64 encoded assertion.
        @param
            foruri (string): An optional recipient string. 
            It should match the one passed when creating the assertion.
            If this option is left off, recipient checks are skipped.
        @param
            nonce (string): An optional nonce string. 
            It should match the one passed when creating the assertion.
            If this option is left off, the validation uses a default value.
            If this value is incorrect, validation will fail.

        @return
            None, function will throw an exception if it fails to validate.
        """

        cEnrollmentUrl = _private.CMarshalUtil.stringToC(enrollmentUrl)
        cAssertionBase64 = _private.CMarshalUtil.stringToC(assertionBase64)
        cForUri = _private.CMarshalUtil.stringToC(foruri)
        cNonce = _private.CMarshalUtil.stringToC(nonce)

        _private.cLib.ionic_agent_validate_assertion_via_enrollment(self._cAgent, cEnrollmentUrl, cAssertionBase64, cForUri, cNonce)

    def getresource(self, resourceid, args = None, metadata = None):
        """!Gets a generic resource from Ionic.com.

        This method makes an HTTP call to Ionic.com to request a generic
        resource.

        @param
            resourceid (string): The resource/rpc ID string for this request.
        @param
            args (string, optional): The optional arguments string for this request.
        @param
            metadata (MetadataDict, optional): The metadata properties for this request.

        @return
            A ResourceResponse data object.
        """
        # inputs
        cRequest = _private.CResourceRequest()
        cRequest.pszResourceId = _private.CMarshalUtil.stringToC(resourceid)
        cRequest.pszArgs = _private.CMarshalUtil.stringToC(args)
        cMetadata = MetadataDict._marshalToC(metadata)

        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cResponse = _private.OWNED_POINTER(_private.CResourceResponse)()

        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_get_resource(
                self._cAgent,
                cRequest,
                cMetadata,
                _private.byref(cResponse),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

        # marshal C output to Python
        return ResourceResponse._marshalFromC(cResponse.contents)

    def getresources(self, resourcelist, metadata = None):
        """!Gets one or more generic resource(s) from Ionic.com.

        This method makes an HTTP call to Ionic.com to request generic
        resource(s).

        @param
            resourcelist (list[ResourceRequest]): A list of
                                         ResourceResquest Objects filled
                                         in with resource IDs and args.
        @param
            metadata (MetadataDict, optional): The metadata properties
                                    to send along with the HTTP request.

        @return
            ResourceResponseList containing ResourceResponse data
            objects.
        """
        # inputs
        cRequestArray = ResourceRequest._marshalToCArray(resourcelist)
        cMetadata = MetadataDict._marshalToC(metadata)

        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cResponseArray = _private.OWNED_POINTER(_private.CResourceResponseArray)()

        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_get_resources(
                self._cAgent,
                cRequestArray,
                len(resourcelist),
                cMetadata,
                _private.byref(cResponseArray),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)

        # marshal C output to Python
        return ResourceResponseList._marshalFromC(cResponseArray.contents)

    def getkeyspace(self, keyspace, knsProviderUrl=None):
        """!Gets keyspace information from Ionic.com.
        
        This method makes an HTTP call to Ionic.com to request 
        keyspace information.
        
        @param
        keyspace (unicode): Keyspace string
        
        @param
        knsProviderUrl (unicode): Optional url for an alternate KNS provider, 
        defaults to https://api.ionic.com

        @return
        KeyspaceResponse containing the Fully Qualified Domain Name (fqdn), the tenant ID
        (tenantId), the enrollment url (enrollUrl) and optionally an api url (apiUrl).
        """
            
        # outputs
        self._cServerResponse = _private.OWNED_POINTER(_private.CServerResponse)()
        cResponse = _private.OWNED_POINTER(_private.CKeyspaceResponse)()
                            
        # call into C library to perform the work
        try:
            _private.cLib.ionic_agent_get_keyspace_url(
                self._cAgent,
                _private.CMarshalUtil.stringToC(keyspace),
                _private.CMarshalUtil.stringToC(knsProviderUrl),
                _private.byref(cResponse),
                _private.byref(self._cServerResponse))
        except Exception as e:
            _private.raiseExceptionWithServerResponse(self._cServerResponse, e)
                                            
        # marshal C output to Python
        return KeyspaceResponse._marshalFromC(cResponse.contents)


class AgentMetadataCollectorNetwork(object):
    """!Class used to generate a metadata object containing network identifiers."""

    ##(string) The "hostname" key
    IONIC_AGENT_META_HOSTNAME = _private.IONIC_AGENT_META_HOSTNAME
    ##(string) The "mac_addrs" key
    IONIC_AGENT_META_MAC_ADDRS = _private.IONIC_AGENT_META_MAC_ADDRS
    ##(string) The "iface_addrs" key
    IONIC_AGENT_META_IFACE_ADDRS = _private.IONIC_AGENT_META_IFACE_ADDRS


    def getmetadata(self):
        """!Get the metadata map.

        @return  
            Returns a MetadataMap containing data related to network interfaces.
        """
        cMetadata = _private.cLib.ionic_metadata_collector_network()
        return MetadataDict._marshalFromC(cMetadata)


class AgentMetadataCollectorProcessEnvironment(object):
    """!Class used to generate a metadata object containing environment variables."""
    def __init__(self, listOfEnvironmentKeys):
        """!Constructor

        @param
        listOfEnvironmentKeys (list of string): environment variables to fetch

        """

        ##(list of strings) The list of environment variables to fetch
        self.listOfKeys = listOfEnvironmentKeys

    def getmetadata(self):
        """!Get the metadata map.

        @return  
            Returns a MetadataMap containing environment data.
        """
        nKeyCount = len(self.listOfKeys)
        cKeyArray = _private.CMarshalUtil.stringArrayToC(self.listOfKeys)

        cMetadata = _private.cLib.ionic_metadata_collector_process_environment(cKeyArray, nKeyCount)
        return MetadataDict._marshalFromC(cMetadata)
