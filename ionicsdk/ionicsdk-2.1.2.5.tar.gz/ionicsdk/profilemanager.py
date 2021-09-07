"""!Management interface for profiles"""

import ionicsdk._private as _private
from ionicsdk.common import *
from ionicsdk.exceptions import *
from ionicsdk.errors import *


class ProfileManager():
    """!ProfileManager handles management of profiles, including
    interfacing with persistors to save and load, and loading json
    profile data, as well as active profiles.
    """
    def __init__(self, profilelist = None, json = None, _cProfileManager = None):
        """!A ProfileManager can be initialized with an array of existing
        profiles, or a json string of profile data

        @param
            profilelist (DeviceProfileList, optional): A device profile
                list to initialize the manager with. If unspecified or 
                None, will start with an empty list and profiles must be
                added later.
        @param
            json (string, optional): A string containing profile
            data in json format.  Can be read from a SEP file or 
            downloaded from a server.

        @param
            _cProfileManager (CProfileManager, optional): Parameter for internal use to create
            a ProfileManager from a C profile manager struct.
        """
        self._cProfileManager = _cProfileManager
        if self._cProfileManager:
            return # exit out here
        if profilelist:
            if not isinstance(profilelist, DeviceProfileList):
                raise Exception('profilelist must be an instance of DeviceProfileList')
            self._cProfileManager = _private.cLib.ionic_profile_manager_create()
            cProfListAndLenTuple = DeviceProfileList._marshalToC(profilelist)
            _private.cLib.ionic_profile_manager_set_all_profiles(self._cProfileManager, *cProfListAndLenTuple)
        elif json:
            self._cProfileManager = _private.cLib.ionic_profile_manager_create_from_json(_private.CMarshalUtil.stringToC(json))
        else:
            self._cProfileManager = _private.cLib.ionic_profile_manager_create()
      
        if not self._cProfileManager:
            raise IonicException('Failed to create a profile manager object. Check the log to know the reason for this error.', IonicError.AGENT_ERROR)

    # active profile
    def hasactiveprofile(self):
        """!Determine if any device profile is active. 
        @return
            True if an active profile is loaded, False otherwise
        """
        return _private.cLib.ionic_profile_manager_has_active_profile(self._cProfileManager)

    def setactiveprofile(self, deviceid):
        """!Set the current device profile of the agent.

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
        
        _private.cLib.ionic_profile_manager_set_active_profile(self._cProfileManager,
                          _private.CMarshalUtil.stringToC(deviceid))

    def getactiveprofile(self):
        """!Get the current device profile of the agent.

        @return
            Returns the active device profile object. If no active
            profile is set, then None will be returned. You can also
            call Agent.hasactiveprofile() to determine if there is an
            active profile.
        """
        cProfile = _private.cLib.ionic_profile_manager_get_active_profile(self._cProfileManager)
        return (DeviceProfile._marshalFromC(cProfile.contents) if cProfile else None)

    # profile management
    def hasanyprofiles(self):
        """!Determine if any device profiles are loaded.
        @return
            True if an any profile is loaded, False otherwise
        """
        return _private.cLib.ionic_profile_manager_has_any_profiles(self._cProfileManager)

    def getallprofiles(self):
        """!Get all available device profiles.

        @return
            Returns a DeviceProfileList (subclass of list) of all device
                profile objects. 
        """
        cNumProfiles = _private.c_size_t(0)
        cProfileArray = _private.cLib.ionic_profile_manager_get_all_profiles(self._cProfileManager,
                                          _private.byref(cNumProfiles))
        
        return DeviceProfileList._marshalFromC(cProfileArray, cNumProfiles)

    def addprofile(self, deviceprofile, makeactive = False):
        """!Add a device profile to the agent device profile collection.

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
        _private.cLib.ionic_profile_manager_add_profile(self._cProfileManager, cDeviceProfile,
                                                     bool(makeactive))

    def removeprofile(self, deviceid):
        """!Remove a device profile from the agent device profile list.

        @param
            deviceid (string): The device id of the profile to remove.
        @return
            None, raises an exception on errors
        """
        if type(deviceid) is DeviceProfile:
            deviceid = deviceid.deviceid
        _private.cLib.ionic_profile_manager_rmv_profile(self._cProfileManager,
                                              _private.CMarshalUtil.stringToC(deviceid))

    def getprofileforkeyid(self, keyid):
        """!Determine which device profile is associated with the
        provided key ID.

        @param
            keyid (string): The key ID for which to retrieve the
                            associated device profile.

        @return
            The DeviceProfile associated with the provided key ID, or
            None if not found.
        """
        cKeyId = _private.CMarshalUtil.stringToC(keyid)
        cProfile = _private.cLib.ionic_profile_manager_get_profile_for_key_id(self._cProfileManager, cKeyId)
        return (DeviceProfile._marshalFromC(cProfile.contents) if cProfile else None)

    # profile persistence
    def loadprofiles(self, persistor):
        """!Load device profiles using the provided profile persistor.
        
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

        @param
            persistor (DeviceProfilePersistorBase): The device profile
                                                    persistor.
        @return
            None, raises an exception on errors
        """
        _private.cLib.ionic_profile_manager_load_profiles(self._cProfileManager, persistor._cPersistor)

    def saveprofiles(self, persistor):
        """!Save device profiles using the specified profile persistor.

        @param
            persistor (DeviceProfilePersistorBase): The device profile
                                                persistor.
        @return
            None, raises an exception on errors
        """
        _private.cLib.ionic_profile_manager_save_profiles(self._cProfileManager, persistor._cPersistor)

    def loadfromjson(self, jsonstring):
        """!Loads all profiles from json data.

        @param
            jsonstring (string): A string containing json profile data.

        @return
            None, raises an exception on errors
        """
        _private.cLib.ionic_profile_manager_load_from_json(self._cProfileManager, _private.CMarshalUtil.stringToC(jsonstring))

    def savetojson(self):
        """!Saves all profiles into an unencrypted string.

        @return
            Returns the json string representation of the profile data.
        """
        cstr = _private.cLib.ionic_profile_manager_save_to_json(self._cProfileManager)
        return _private.CMarshalUtil.stringFromC(cstr)