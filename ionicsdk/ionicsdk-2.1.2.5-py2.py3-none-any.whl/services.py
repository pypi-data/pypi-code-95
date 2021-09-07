"""!The AgentKeyServicesBase class used as a base class for custom key services code.
"""
import ionicsdk._private as _private
from ionicsdk.common import *
from ionicsdk.agent import *
from ionicsdk.exceptions import *
from ionicsdk.errors import *
import ionicsdk.log
import traceback
from inspect import currentframe, getframeinfo

class AgentKeyServicesBase(object):
    """!AgentKeyServicesBase class performs all key related services (create and get) for higher level objects
        like chunk cipher and file cryto. A user may sub class this base class to create their own local key
        storage services, or the user could use \ref agent.Agent, which uses the Ionic web server to store and 
        create keys.<br><br>See also a usage example here: \ref isagentkeyservices
    """
    def hasactiveprofile(self):
        """!Determine if any device profile is active.
            

            @return
                True if an active profile is loaded and active,
                False otherwise.
                This root class always returns False
        """
        return False
    def getactiveprofile(self):
        """!Get the current device profile of the agent.
            

            @return
                Returns the active device profile object. If no active
                profile is set, then None will be returned. You can also
                call Agent.hasactiveprofile() to determine if there is an
                active profile.
                This root class always returns None
        """
        return None
    def createkey(self, attributesdict = None, metadatadict = None, mutableAttributesdict = None):
        """!Creates a single protection key with attributes
            This method must be overridden in a subclass
            Otherwise, root class version will raise an exception.
            
            @param
                attributesdict (KeyAttributesDict, optional): The protection key
                    attributes to use for creating the protection key.
            @param
                metadatadict (MetadataDict, optional): The metadata properties to send
                    along with the request.
            @param
                mutableAttributesdict (KeyAttributesDict, optional): The protection key
                    mutable attributes to use for creating the protection key.
            
            @return
                A KeyData object with the newly created protection key.
        """
        raise Exception("Implement this method!")
        raise IonicServerException("Raise this error in case of HTTP errors!")
        return None # key data
    def createkeys(self, keycount, attributesdict = None, metadatadict = None, mutableAttributesdict = None):
        """!Creates protection keys.
            This method must be overridden in a subclass
            Otherwise, root class version will raise an exception.
            
            @param
                keycount (int): The number of keys to create.
            @param
                attributesdict (KeyAttributesDict, optional): The protection key
                    attributes to use for creating the protection keys.
            @param
                metadatadict (MetadataDict, optional): The metadata properties
                    to send along with the HTTP request.
            @param
                mutableAttributesdict (KeyAttributesDict, optional): The protection key
                    mutable attributes to use for creating the protection key.
            
            @return
                The KeyDataList of newly created protection keys.
            """
        raise Exception("Implement this method!")
        raise IonicServerException("Raise this error in case of HTTP errors!")
        return None # list of key data
    def getkey(self, keyidstring, metadatadict = None):
        """!Gets a single protection key.
            This method must be overridden in a subclass.
            Otherwise, root class version will raise an exception.
            
            @param
                keyidstring (string): The protection key ID to fetch.
            @param
                metadatadict (MetadataDict, optional): The metadata properties
                    to send along with the HTTP request.
            
            @return
                A KeyData object containing the requested key.
        """
        raise Exception("Implement this method!")
        raise IonicServerException("Raise this error in case of HTTP errors!")
        return None # key data
    def getkeys(self, keyidstringlist, metadatadict = None):
        """!Gets protection keys.
            This method must be overridden in a subclass
            Otherwise, root class version will raise an exception.
            
            @param
                keyidstringlist (string): The list of protection key IDs to fetch.
            @param
                metadatadict (MetadataDict, optional): The metadata properties
                    to send along with the HTTP request.
            
            @return
                A list of keys that were successfully retrieved.  It is
                important to note that even if the function succeeds, it
                does NOT mean that any or all of the requested keys were
                provided. The caller can iterate through the response object
                and determine which keys were returned by looking at the key
                ID property (KeyData.id).
        """
        raise Exception("Implement this method!")
        raise IonicServerException("Raise this error in case of HTTP errors!")
        return None # list of key data
    def updatekey(self, keydata, metadatadict = None):
        """!Updates the Mutable Attributes of a single protection key.
            This method must be overridden in a subclass.
            Otherwise, root class version will raise an exception.
            
            @param
                keydata (KeyData): The protection key data with modified Mutable
                    Attributes to update.
            @param
                metadatadict (MetadataDict, optional): The metadata properties
                    to send along with the HTTP request.
            
            @return
                A KeyData object containing the updated key.
        """
        raise Exception("Implement this method!")
        raise IonicServerException("Raise this error in case of HTTP errors!")
        return None # key data
    def updatekeys(self, keydatalist, metadatadict = None):
        """!Updates the Mutable Attributes of protection keys.
            This method must be overridden in a subclass
            Otherwise, root class version will raise an exception.
            
            @param
                keydatalist (KeyDataList): The list of protection keys with
                    modified Mutable Attributes to update.
            @param
                metadatadict (MetadataDict, optional): The metadata properties
                    to send along with the HTTP request.
            
            @return
                A list of keys that were successfully updated.  It is
                important to note that even if the function succeeds, it
                does NOT mean that any or all of the requested keys were
                provided. The caller can iterate through the response object
                and determine which keys were returned by looking at the key
                ID property (KeyData.id).
        """
        raise Exception("Implement this method!")
        raise IonicServerException("Raise this error in case of HTTP errors!")
        return None # list of key data
    #--# Optional functions to handle any memory management or ref counting
    #def releasekeydata(self, keyobject):
    #    raise Exception("Implement this method!")
    #    return 0
    #def releasekeydataarray(self, keylistobject):
    #    raise Exception("Implement this method!")
    #    return 0
    #def releaseserverresponse(self, servererrorobject):
    #    raise Exception("Implement this method!")
    #    return 0
    #def releasedeviceprofile(self, deviceprofileobject):
    #    raise Exception("Implement this method!")
    #    return 0
    #def releaseupdatekeydata(self, updatekeydata)
    #    raise Exception("Implement this method!")
    #    return 0
    #def releaseupdatekeydataarray
    #    raise Exception("Implement this method!")
    #    return 0
    
##(List) Internal variable that tracks 'C' marshalling instances across callbacks.
refs = list()

class _ServicesInternal:
    def __init__(self, servicesBase):
        self.service = servicesBase

    def logCallbackError(self, err):
        # Get the frame info from up the stack
        frameinfo = getframeinfo(currentframe().f_back)
        ionicsdk.log.log(ionicsdk.log.SEV_ERROR, ionicsdk.log.PYTHON_LOG_CHANNEL, frameinfo.lineno, frameinfo.filename, "Python Services Callback exception: " + str(err))
        ionicsdk.log.log(ionicsdk.log.SEV_TRACE, ionicsdk.log.PYTHON_LOG_CHANNEL, frameinfo.lineno, frameinfo.filename, traceback.format_exc())

    def getServices(self):
        self.refmap = {}
        def cb_hasactiveprofile(cContext):
            return self.service.hasactiveprofile()
        def cb_getactiveprofile(cContext):
            pyDeviceProfile = self.service.getactiveprofile()
            pDeviceProfile = _private.pointer(DeviceProfile._marshalToC(pyDeviceProfile))

            ref = _private.cast(pDeviceProfile, _private.c_void_p)
            self.refmap[ref.value] = [pyDeviceProfile, pDeviceProfile, ref]
            return ref.value
        def cb_createkey(cContext, cAttrsMap, cMutableAttrsMap, cMetaMap, pKeyDataOut, pServerResponseOut):
            try:
                attrdict = KeyAttributesDict._marshalFromC(cAttrsMap)
                mutableAttrdict = KeyAttributesDict._marshalFromC(cMutableAttrsMap)
                metadict = MetadataDict._marshalFromC(cMetaMap)
                keydata = None
                try:
                    keydata = self.service.createkey(attributesdict=attrdict, metadatadict=metadict, mutableAttributesdict=mutableAttrdict)
                except TypeError: # We had the wrong arguments, try older interfaces
                    frameinfo = getframeinfo(currentframe())
                    ionicsdk.log.log(ionicsdk.log.SEV_WARN, ionicsdk.log.PYTHON_LOG_CHANNEL, frameinfo.lineno, frameinfo.filename,
                        "Did not find a current createkey services interface. Please update deprecated interfaces.")
                    try: # first try the '2' interface from v1.4
                        keydata = self.service.createkey2(attributesdict=attrdict, mutableAttributesdict=mutableAttrdict, metadatadict=metadict)
                    except AttributeError: # If there's no '2' interface, try v1.3
                        if mutableAttrdict is not None and len(mutableAttrdict) > 0:
                            # Mutable attributes were specified but not supported
                            raise Exception("Mutable Attributes were specified but no key services implementation supports them.")
                        keydata = self.service.createkey(attributesdict=attrdict, metadatadict=metadict)
                cKeyData = KeyData._marshalToC(keydata)
                pKeyDataOut[0] = _private.pointer(cKeyData)
                # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
                ref = _private.cast(pKeyDataOut[0],_private.c_void_p)
                self.refmap[ref.value] = [keydata, cKeyData, ref]
                return IonicError.AGENT_OK
            except IonicServerException as err:
                if pServerResponseOut != 0:
                    serverResponse = IonicServerException._marshalToC(err)
                    pServerResponseOut[0] = _private.pointer(serverResponse)
                    ref = _private.cast(pServerResponseOut[0],_private.c_void_p)
                    self.refmap[ref.value] = [serverResponse, pServerResponseOut[0], ref]
                    return err.code
                return IonicError.AGENT_UNEXPECTEDRESPONSE
            except IonicException as err:
                return err.code
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN
            
        def cb_createkeys(cContext, cAttrsMap, cMutableAttrsMap, nCount, cMetaMap, pKeyArrayOut, pServerResponseOut):
            try:
                attrdict = KeyAttributesDict._marshalFromC(cAttrsMap)
                mutableAttrdict = KeyAttributesDict._marshalFromC(cMutableAttrsMap)
                metadict = MetadataDict._marshalFromC(cMetaMap)
                keydatalist = None
                try:
                    keydatalist = self.service.createkeys(nCount, attributesdict=attrdict, metadatadict=metadict, mutableAttributesdict=mutableAttrdict)
                except TypeError: # We had the wrong arguments, try older interfaces
                    frameinfo = getframeinfo(currentframe())
                    ionicsdk.log.log(ionicsdk.log.SEV_WARN, ionicsdk.log.PYTHON_LOG_CHANNEL, frameinfo.lineno, frameinfo.filename,
                        "Did not find a current createkeys services interface.")
                cKeys = _private.pointer((_private.CKeyData * nCount)())
                cKeys = _private.cast(cKeys, _private.POINTER(_private.POINTER(_private.CKeyData)))
                cKeyArray = _private.pointer(_private.CKeyDataArray(cKeys, nCount))
                i = 0
                for key in keydatalist:
                    cKeyArray[0].ppKeyArray[i] = _private.pointer(KeyData._marshalToC(key))
                    i = i + 1
                pKeyArrayOut[0] = cKeyArray
                # consider setting a 'good' server response here for completeness
                # (currently there is no way in python to retrieve a 'good' response)
                # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
                ref = _private.cast(pKeyArrayOut[0],_private.c_void_p)
                self.refmap[ref.value] = [keydatalist, cKeyArray, ref]
                return IonicError.AGENT_OK
            except IonicServerException as err:
                if pServerResponseOut != 0:
                    serverResponse = IonicServerException._marshalToC(err)
                    pServerResponseOut[0] = _private.pointer(serverResponse)
                    ref = _private.cast(pServerResponseOut[0],_private.c_void_p)
                    self.refmap[ref.value] = [serverResponse, pServerResponseOut[0], ref]
                    return err.code
                return IonicError.AGENT_UNEXPECTEDRESPONSE
            except IonicException as err:
                return err.code
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN

        def cb_createkeys3(cContext, cCreateKeysRequest, pKeyArrayOut, pServerResponseOut):
            try:
                pyCreateKeysRequest =ionicsdk.CreateKeysRequest._marshalFromC(cCreateKeysRequest)
                keydatalist = self.service.createkeys2(pyCreateKeysRequest)
                nCount = sum([keyreq.count for keyreq in pyCreateKeysRequest.keys])
                cKeys = _private.pointer((_private.CKeyData * nCount)())
                cKeys = _private.cast(cKeys, _private.POINTER(_private.POINTER(_private.CKeyData)))
                cRefs = None
                if hasattr(pyCreateKeysRequest.keys[0],"ref"):
                    cRefs = _private.pointer((_private.c_char_p * nCount)())
                    cRefs = _private.cast(cRefs, _private.POINTER(c_char_p))
                cKeyArray = _private.pointer(_private.CKeyDataArray(cKeys, nCount, cRefs))
                i = 0
                for key in keydatalist:
                    cKeyArray[0].ppKeyArray[i] = _private.pointer(KeyData._marshalToC(key))
                    if hasattr(key,"ref"):
                        cKeyArray[0].ppszRefs[i] = _private.CMarshalUtil.stringToC(key.ref)
                    else:
                        cKeyArray[0].ppszRefs[i] = _private.CMarshalUtil.stringToC("")
                    i = i + 1
                pKeyArrayOut[0] = cKeyArray
                # consider setting a 'good' server response here for completeness
                # (currently there is no way in python to retrieve a 'good' response)
                # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
                ref = _private.cast(pKeyArrayOut[0],_private.c_void_p)
                self.refmap[ref.value] = [keydatalist, cKeyArray, ref]
                return IonicError.AGENT_OK
            except IonicServerException as err:
                if pServerResponseOut != 0:
                    serverResponse = IonicServerException._marshalToC(err)
                    pServerResponseOut[0] = _private.pointer(serverResponse)
                    ref = _private.cast(pServerResponseOut[0],_private.c_void_p)
                    self.refmap[ref.value] = [serverResponse, pServerResponseOut[0], ref]
                    return err.code
                return IonicError.AGENT_UNEXPECTEDRESPONSE
            except IonicException as err:
                return err.code
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN

        def cb_getkey(cContext, sKeyId, cMetaMap, pKeyDataOut, pServerResponseOut):
            try:
                metadict = MetadataDict._marshalFromC(cMetaMap)
                keyid = _private.CMarshalUtil.stringFromC(sKeyId)
                keydata = self.service.getkey(keyid, metadict)
                cKeyData = KeyData._marshalToC(keydata)
                numKeys = _private.c_size_t(0)
                pKeyDataOut[0] = _private.pointer(cKeyData)
                # consider setting a 'good' server response here
                # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
                ref = _private.cast(pKeyDataOut[0],_private.c_void_p)
                self.refmap[ref.value] = [keydata, cKeyData, ref]
                return IonicError.AGENT_OK
            except IonicServerException as err:
                if pServerResponseOut != 0:
                    serverResponse = IonicServerException._marshalToC(err)
                    pServerResponseOut[0] = _private.pointer(serverResponse)
                    ref = _private.cast(pServerResponseOut[0],_private.c_void_p)
                    self.refmap[ref.value] = [serverResponse, pServerResponseOut[0], ref]
                    return err.code
                return IonicError.AGENT_UNEXPECTEDRESPONSE
            except IonicException as err:
                return err.code
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN

        def cb_getkeys(cContext, sKeyIdArray, nCount, cMetaMap, pKeyArrayOut, pServerResponseOut):
            try:
                metadict = MetadataDict._marshalFromC(cMetaMap)
                pyKeyIds = _private.CMarshalUtil.stringArrayFromC(sKeyIdArray, nCount)
                keydatalist = self.service.getkeys(pyKeyIds, metadict)
                cKeys = _private.pointer((_private.CKeyData * nCount)())
                cKeys = _private.cast(cKeys, _private.POINTER(_private.POINTER(_private.CKeyData)))
                cKeyArray = _private.pointer(_private.CKeyDataArray(cKeys, nCount))
                i = 0
                for key in keydatalist:
                    cKeyArray[0].ppKeyArray[i] = _private.pointer(KeyData._marshalToC(key))
                    i = i + 1
                pKeyArrayOut[0] = cKeyArray
                # consider setting a 'good' server response here
                # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
                ref = _private.cast(pKeyArrayOut[0],_private.c_void_p)
                self.refmap[ref.value] = [keydatalist, cKeyArray, ref]
                return IonicError.AGENT_OK
            except IonicServerException as err:
                if pServerResponseOut != 0:
                    serverResponse = IonicServerException._marshalToC(err)
                    pServerResponseOut[0] = _private.pointer(serverResponse)
                    ref = _private.cast(pServerResponseOut[0],_private.c_void_p)
                    self.refmap[ref.value] = [serverResponse, pServerResponseOut[0], ref]
                    return err.code
                return IonicError.AGENT_UNEXPECTEDRESPONSE
            except IonicException as err:
                return err.code
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN

        def cb_updatekey(cContext, cUpdateKeyDataIn, cMetaMap, pKeyArrayOut, pServerResponseOut):
            try:
                metadict = MetadataDict._marshalFromC(cMetaMap)
                updateKeyDataIn = UpdateKeyData._marshalFromC(cUpdateKeyDataIn)
                keyDataOut = self.service.updatekey(updateKeyDataIn, metadict)
                cKeyDataOut = KeyData._marshalToC(keyDataOut)
                numKeys = _private.c_size_t(0)
                pKeyDataOut[0] = _private.pointer(cKeyDataOut)
                # consider setting a 'good' server response here
                # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
                ref = _private.cast(pKeyDataOut[0],_private.c_void_p)
                self.refmap[ref.value] = [keydata, cKeyData, ref]
                return IonicError.AGENT_OK
            except IonicServerException as err:
                if pServerResponseOut != 0:
                    serverResponse = IonicServerException._marshalToC(err)
                    pServerResponseOut[0] = _private.pointer(serverResponse)
                    ref = _private.cast(pServerResponseOut[0],_private.c_void_p)
                    self.refmap[ref.value] = [serverResponse, pServerResponseOut[0], ref]
                    return err.code
                return IonicError.AGENT_UNEXPECTEDRESPONSE
            except IonicException as err:
                return err.code
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN

        def cb_updatekeys(cContext, cUpdateKeyDataArrayIn, cMetaMap, pKeyArrayOut, pServerResponseOut):
            try:
                metadict = MetadataDict._marshalFromC(cMetaMap)
                updateKeyDataListIn = UpdateKeyDataList._marshalFromC(cUpdateKeyDataArrayIn)
                keyDataListOut = self.service.updatekeys(updateKeyDataListIn, metadict)
                cKeys = _private.pointer((_private.CKeyData * nCount)())
                cKeys = _private.cast(cKeys, _private.POINTER(_private.POINTER(_private.CKeyData)))
                cKeyArray = _private.pointer(_private.CKeyDataArray(cKeys, nCount))
                i = 0
                for key in keyDataListOut:
                    cKeyArray[0].ppKeyArray[i] = _private.pointer(KeyData._marshalToC(key))
                    i = i + 1
                pKeyArrayOut[0] = cKeyArray
                # consider setting a 'good' server response here
                # Keep a handle to the relevant objects so they don't get free'd before the C layer finishes
                ref = _private.cast(pKeyArrayOut[0],_private.c_void_p)
                self.refmap[ref.value] = [keydatalist, cKeyArray, ref]
                return IonicError.AGENT_OK
            except IonicServerException as err:
                if pServerResponseOut != 0:
                    serverResponse = IonicServerException._marshalToC(err)
                    pServerResponseOut[0] = _private.pointer(serverResponse)
                    ref = _private.cast(pServerResponseOut[0],_private.c_void_p)
                    self.refmap[ref.value] = [serverResponse, pServerResponseOut[0], ref]
                    return err.code
                return IonicError.AGENT_UNEXPECTEDRESPONSE
            except IonicException as err:
                return err.code
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN

        def cb_releasekeydata(cContext, keydata):
            try:
                reflist = self.refmap.pop(keydata)
                self.services.releasekeydata(reflist[0])
            except AttributeError:
                pass # We're ok with this function being unimplemented
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN

            return 0
        def cb_releasekeydataarray(cContext, keyarray):
            try:
                reflist = self.refmap.pop(keyarray)
                self.services.releasekeydataarray(reflist[0])
            except AttributeError:
                pass # Optional function
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN
            return 0
        def cb_releaseserverresponse(cContext, serverresponse):
            try:
                reflist = self.refmap.pop(serverresponse)
                self.services.releaseserverresponse(reflist[0])
            except AttributeError:
                pass # Optional function
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN
            return 0
        def cb_releasedeviceprofile(cContext, deviceprofile):
            try:
                reflist = self.refmap.pop(deviceprofile)
                self.services.releasedeviceprofile(reflist[0])
            except AttributeError:
                pass # Optional function
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN
            return 0
        def cb_releaseupdatekeydata(cContext, updatekeydata):
            try:
                reflist = self.refmap.pop(updatekeydata)
                self.services.releaseupdatekeydata(reflist[0])
            except AttributeError:
                pass # Optional function
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN
            return 0
        def cb_releaseupdatekeydataarray(cContext, updatekeydataarray):
            try:
                reflist = self.refmap.pop(updatekeydataarray)
                self.services.releaseupdatekeydataarray(reflist[0])
            except AttributeError:
                pass # Optional function
            except Exception as err:
                self.logCallbackError(err)
                return IonicError.AGENT_UNKNOWN
            return 0

        cServStruct = _private.CServices()
        cServStruct.pfHasActiveProfile      = _private.ServicesCallback_has_active_profile(cb_hasactiveprofile)
        cServStruct.pfGetActiveProfile      = _private.ServicesCallback_get_active_profile(cb_getactiveprofile)
        cServStruct.pfCreateKey2            = _private.ServicesCallback_create_key2(cb_createkey)
        cServStruct.pfCreateKeys2           = _private.ServicesCallback_create_keys2(cb_createkeys)
        if 'createkeys2' in dir(self.service):
            cServStruct.pfCreateKeys3       = _private.ServicesCallback_create_keys3(cb_createkeys3)
        cServStruct.pfGetKey                = _private.ServicesCallback_get_key(cb_getkey)
        cServStruct.pfGetKeys               = _private.ServicesCallback_get_keys(cb_getkeys)
        cServStruct.pfReleaseKeyData        = _private.ServicesCallback_release_key_data(cb_releasekeydata)
        cServStruct.pfReleaseKeyDataArray   = _private.ServicesCallback_release_key_data_array(cb_releasekeydataarray)
        cServStruct.pfReleaseServerResponse = _private.ServicesCallback_release_server_response(cb_releaseserverresponse)
        cServStruct.pfReleaseDeviceProfile  = _private.ServicesCallback_release_device_profile(cb_releasedeviceprofile)
        cServStruct.pfUpdateKey             = _private.ServicesCallback_update_key(cb_updatekey)
        cServStruct.pfUpdateKeys            = _private.ServicesCallback_update_keys(cb_updatekeys)
        cServStruct.pfReleaseUpdateKeyData  = _private.ServicesCallback_release_update_key_data(cb_releaseupdatekeydata)
        cServStruct.pfReleaseUpdateKeyDataArray = _private.ServicesCallback_release_update_key_data_array(cb_releaseupdatekeydataarray)

        return cServStruct
