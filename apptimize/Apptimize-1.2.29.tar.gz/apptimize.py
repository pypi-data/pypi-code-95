# Copyright (c) Apptimize, Inc. | https://sdk.apptimize.com/license
# coding: utf-8
import sys

import math as python_lib_Math
import math as Math
from os import path as python_lib_os_Path
import inspect as python_lib_Inspect
import atexit as apptimize_native_python_AtExit
from threading import Event as apptimize_native_python_Event
from requests import Session as apptimize_native_python_Session
from requests_futures.sessions import FuturesSession as apptimize_native_python_FuturesSession
import requests as apptimize_native_python_Requests
import sys as python_lib_Sys
import builtins as python_lib_Builtins
import functools as python_lib_Functools
import json as python_lib_Json
import os as python_lib_Os
import random as python_lib_Random
import re as python_lib_Re
import ssl as python_lib_Ssl
import time as python_lib_Time
import traceback as python_lib_Traceback
from datetime import datetime as python_lib_datetime_Datetime
from datetime import timezone as python_lib_datetime_Timezone
from io import StringIO as python_lib_io_StringIO
from socket import socket as python_lib_socket_Socket
from ssl import SSLContext as python_lib_ssl_SSLContext
from threading import RLock as python_lib_threading_RLock
from threading import Thread as python_lib_threading_Thread
import urllib.parse as python_lib_urllib_Parse
from threading import Semaphore as Lock
from threading import RLock as sys_thread__Mutex_NativeRLock
import threading


class _hx_AnonObject:
    _hx_disable_getattr = False
    def __init__(self, fields):
        self.__dict__ = fields
    def __repr__(self):
        return repr(self.__dict__)
    def __contains__(self, item):
        return item in self.__dict__
    def __getitem__(self, item):
        return self.__dict__[item]
    def __getattr__(self, name):
        if (self._hx_disable_getattr):
            raise AttributeError('field does not exist')
        else:
            return None
    def _hx_hasattr(self,field):
        self._hx_disable_getattr = True
        try:
            getattr(self, field)
            self._hx_disable_getattr = False
            return True
        except AttributeError:
            self._hx_disable_getattr = False
            return False



_hx_classes = {}


class Enum:
    _hx_class_name = "Enum"
    __slots__ = ("tag", "index", "params")
    _hx_fields = ["tag", "index", "params"]
    _hx_methods = ["__str__"]

    def __init__(self,tag,index,params):
        self.tag = tag
        self.index = index
        self.params = params

    def __str__(self):
        if (self.params is None):
            return self.tag
        else:
            return self.tag + '(' + (', '.join(str(v) for v in self.params)) + ')'

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.tag = None
        _hx_o.index = None
        _hx_o.params = None
Enum._hx_class = Enum
_hx_classes["Enum"] = Enum


class apptimize_Apptimize:
    _hx_class_name = "apptimize.Apptimize"
    __slots__ = ()
    _hx_statics = ["_isInitialized", "_getApptimizeAnonUserId", "setAppVersion", "setAppName", "setOnParticipationCallback", "setOnMetadataUpdatedCallback", "setOnApptimizeInitializedCallback", "setOnParticipatedInExperimentCallback", "setup", "shutdown", "updateApptimizeMetadataOnce", "flushTracking", "getApptimizeSDKVersion", "getApptimizeSDKPlatform", "_initialize", "_getAlterations", "_getCodeBlockMethod", "runCodeBlock", "isFeatureFlagEnabled", "getString", "getBool", "getInt", "getDouble", "getStringArray", "getBoolArray", "getIntArray", "getDoubleArray", "getStringDictionary", "getBoolDictionary", "getIntDictionary", "getDoubleDictionary", "_getValue", "getVariantInfo", "_getVariantInfoForAlteration", "_getVariantInfoForDynamicVariable", "_getVariantInfoForExperiment", "track", "trackValue"]

    @staticmethod
    def _isInitialized():
        return apptimize_ApptimizeInternal._isInitialized()

    @staticmethod
    def _getApptimizeAnonUserId():
        anonUserId = apptimize_support_persistence_ABTPersistence.loadString(apptimize_support_persistence_ABTPersistence.kAnonymousGuidKey)
        if (((anonUserId is None) or ((anonUserId == ""))) or (not apptimize_api_ABTUserGuid.isValidGuid(anonUserId))):
            anonUserId = apptimize_api_ABTUserGuid.generateUserGuid()
            apptimize_support_persistence_ABTPersistence.saveString(apptimize_support_persistence_ABTPersistence.kAnonymousGuidKey,anonUserId)
        return anonUserId

    @staticmethod
    def setAppVersion(version):
        apptimize_support_properties_ABTApplicationProperties.sharedInstance().setProperty("app_version",version)
        app_version = apptimize_support_properties_ABTApplicationProperties.sharedInstance().valueForProperty("app_version")
        apptimize_ABTLogger.v(("App Version set to: " + ("null" if app_version is None else app_version)),_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 244, 'className': "apptimize.Apptimize", 'methodName': "setAppVersion"}))

    @staticmethod
    def setAppName(name):
        apptimize_support_properties_ABTApplicationProperties.sharedInstance().setProperty("app_name",name)
        app_name = apptimize_support_properties_ABTApplicationProperties.sharedInstance().valueForProperty("app_name")
        apptimize_ABTLogger.v(("App Name set to: " + ("null" if app_name is None else app_name)),_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 255, 'className': "apptimize.Apptimize", 'methodName': "setAppName"}))

    @staticmethod
    def setOnParticipationCallback(callback):
        apptimize_events_ABTEventManager.setOnParticipationCallback(callback)
        apptimize_ABTLogger.w("setOnParticipationCallback is deprecated - please use setOnParticipatedInExperimentCallback.",_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 276, 'className': "apptimize.Apptimize", 'methodName': "setOnParticipationCallback"}))

    @staticmethod
    def setOnMetadataUpdatedCallback(callback):
        apptimize_events_ABTEventManager.setOnMetadataUpdatedCallback(callback)
        apptimize_ABTLogger.v("OnMetadataProcessedCallback set!",_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 295, 'className': "apptimize.Apptimize", 'methodName': "setOnMetadataUpdatedCallback"}))

    @staticmethod
    def setOnApptimizeInitializedCallback(callback):
        apptimize_events_ABTEventManager.setOnApptimizeInitializedCallback(callback)
        apptimize_ABTLogger.v("OnApptimizeInitializedCallback set!",_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 314, 'className': "apptimize.Apptimize", 'methodName': "setOnApptimizeInitializedCallback"}))

    @staticmethod
    def setOnParticipatedInExperimentCallback(callback):
        apptimize_events_ABTEventManager.setOnParticipatedInExperimentCallback(callback)
        apptimize_ABTLogger.v("OnParticipatedInExperimentCallback set!",_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 332, 'className': "apptimize.Apptimize", 'methodName': "setOnParticipatedInExperimentCallback"}))

    @staticmethod
    def setup(appKey,configAttributes = None):
        if ((appKey is None) or ((appKey == ""))):
            apptimize_ABTLogger.c("Unable to initialize Apptimize due to missing app key.",_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 384, 'className': "apptimize.Apptimize", 'methodName': "setup"}))
            return
        elif ((apptimize_ABTDataStore.getAppKey() is not None) and ((apptimize_ABTDataStore.getAppKey() == appKey))):
            apptimize_ABTLogger.w((("Apptimize is already initialized with app key: \"" + ("null" if appKey is None else appKey)) + "\"."),_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 387, 'className': "apptimize.Apptimize", 'methodName': "setup"}))
            return
        def _hx_local_0():
            if ((apptimize_ABTDataStore.getAppKey() is not None) and ((apptimize_ABTDataStore.getAppKey() != appKey))):
                apptimize_ABTDataStore.clear()
            apptimize_ABTLogger.v(("Set Anonymous User ID: " + HxOverrides.stringOrNull(apptimize_Apptimize._getApptimizeAnonUserId())),_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 398, 'className': "apptimize.Apptimize", 'methodName': "setup"}))
            apptimize_ABTLogger.i(((("Apptimize " + HxOverrides.stringOrNull(apptimize_Apptimize.getApptimizeSDKPlatform())) + " SDK initialized.\nApptimize SDK Version: ") + HxOverrides.stringOrNull(apptimize_Apptimize.getApptimizeSDKVersion())),_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 399, 'className': "apptimize.Apptimize", 'methodName': "setup"}))
            apptimize_Apptimize._initialize(appKey)
        apptimize_ApptimizeInternal._setup(appKey,configAttributes,_hx_local_0)

    @staticmethod
    def shutdown():
        apptimize_ApptimizeInternal.shutdown()

    @staticmethod
    def updateApptimizeMetadataOnce():
        apptimize_ABTDataStore.checkForUpdatedMetaData(True)

    @staticmethod
    def flushTracking():
        if apptimize_Apptimize._isInitialized():
            apptimize_ABTDataStore.sharedInstance().flushTracking()
        else:
            apptimize_ABTLogger.w("Tracking can only be flushed after setup().",_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 442, 'className': "apptimize.Apptimize", 'methodName': "flushTracking"}))

    @staticmethod
    def getApptimizeSDKVersion():
        return "1.2.29"

    @staticmethod
    def getApptimizeSDKPlatform():
        sdkPlatform = "N/A"
        sdkPlatform = "Python"
        return sdkPlatform

    @staticmethod
    def _initialize(appKey):
        apptimize_ABTDataStore.sharedInstance().loadMetaData(appKey)
        apptimize_ApptimizeInternal.setState(2)
        if (apptimize_ABTDataStore.sharedInstance().hasMetadata(apptimize_ABTDataStore.getAppKey()) and apptimize_ApptimizeInternal._trySetReady()):
            apptimize_events_ABTEventManager.dispatchOnApptimizeInitialized()
        apptimize_ABTLogger.i((("Apptimize initialized with app key \"" + ("null" if appKey is None else appKey)) + "\"."),_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 497, 'className': "apptimize.Apptimize", 'methodName': "_initialize"}))

    @staticmethod
    def _getAlterations(userID,customAttributes):
        apptimize_ABTDataStore._checkForUpdatedMetadataIfNecessary()
        if apptimize_Apptimize._isInitialized():
            envParams = apptimize_filter_ABTFilterEnvParams(userID,apptimize_Apptimize._getApptimizeAnonUserId(),customAttributes,apptimize_ABTDataStore.getAppKey(),apptimize_support_properties_ABTApplicationProperties.sharedInstance())
            return apptimize_ApptimizeInternal._getAlterations(envParams)
        return list()

    @staticmethod
    def _getCodeBlockMethod(codeBlockVariableName,userID,customAttributes):
        apptimize_ABTDataStore._checkForUpdatedMetadataIfNecessary()
        envParams = apptimize_filter_ABTFilterEnvParams(userID,apptimize_Apptimize._getApptimizeAnonUserId(),customAttributes,apptimize_ABTDataStore.getAppKey(),apptimize_support_properties_ABTApplicationProperties.sharedInstance())
        return apptimize_ApptimizeInternal._getCodeBlockMethod(envParams,codeBlockVariableName)

    @staticmethod
    def runCodeBlock(codeBlockVariableName,callback,userID,customAttributes = None):
        if ((not apptimize_util_ABTTypes.isNullOrString(userID)) or ((StringTools.ltrim(userID) == ""))):
            apptimize_ABTLogger.w("The `userID` argument cannot be set to a non-string value, be empty or be whitespace only, setting to null instead.",_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 46, 'className': "apptimize.Apptimize", 'methodName': "runCodeBlock"}))
            userID = None
        if ((userID is None) and False):
            apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize.runCodeBlock"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 51, 'className': "apptimize.Apptimize", 'methodName': "runCodeBlock"}))
        if ((customAttributes is None) and False):
            apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize.runCodeBlock"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 57, 'className': "apptimize.Apptimize", 'methodName': "runCodeBlock"}))
        attrs = apptimize_util_ABTUtilDictionary.nativeObjectToStringMap(customAttributes)
        methodName = apptimize_Apptimize._getCodeBlockMethod(codeBlockVariableName,userID,attrs)
        callbackMap = apptimize_util_ABTUtilDictionary.nativeObjectToStringMap(callback)
        if ((methodName is None) or ((methodName == ""))):
            apptimize_ABTLogger.w((("No Code Block with variable name " + ("null" if codeBlockVariableName is None else codeBlockVariableName)) + " found, skipping callback."),_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 591, 'className': "apptimize.Apptimize", 'methodName': "runCodeBlock"}))
            return
        elif ((callback is None) or ((callbackMap.h.get(methodName,None) is None))):
            method = Reflect.getProperty(callback,methodName)
            if (method is not None):
                Reflect.callMethod(callback,method,[])
            else:
                apptimize_ABTLogger.w(("Supplied callbacks do not include method: " + ("null" if methodName is None else methodName)),_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 599, 'className': "apptimize.Apptimize", 'methodName': "runCodeBlock"}))
        else:
            apptimize_ABTLogger.v(("Calling callback method: " + ("null" if methodName is None else methodName)),_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 602, 'className': "apptimize.Apptimize", 'methodName': "runCodeBlock"}))
            func = callbackMap.h.get(methodName,None)
            if (not Reflect.isFunction(func)):
                apptimize_ABTLogger.e("runCodeBlock() called with callback that isn't a function/method.",_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 606, 'className': "apptimize.Apptimize", 'methodName': "runCodeBlock"}))
                return
            func()

    @staticmethod
    def isFeatureFlagEnabled(name,userID,customAttributes = None):
        return apptimize_Apptimize.getBool(name,False,userID,customAttributes)

    @staticmethod
    def getString(name,defaultValue,userID,customAttributes = None):
        stringValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.String,None,customAttributes)
        if (stringValue is None):
            return defaultValue
        return stringValue

    @staticmethod
    def getBool(name,defaultValue,userID,customAttributes = None):
        boolValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Boolean,None,customAttributes)
        if (boolValue is None):
            return defaultValue
        return boolValue

    @staticmethod
    def getInt(name,defaultValue,userID,customAttributes = None):
        intValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Integer,None,customAttributes)
        if (intValue is None):
            return defaultValue
        return intValue

    @staticmethod
    def getDouble(name,defaultValue,userID,customAttributes = None):
        floatValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Double,None,customAttributes)
        if (floatValue is None):
            return defaultValue
        return floatValue

    @staticmethod
    def getStringArray(name,defaultValue,userID,customAttributes = None):
        stringArrayValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Array,apptimize_ABTApptimizeVariableType.String,customAttributes)
        if (stringArrayValue is None):
            return defaultValue
        return apptimize_util_ABTUtilArray.toNativeArray(stringArrayValue,apptimize_util_ArrayType.String)

    @staticmethod
    def getBoolArray(name,defaultValue,userID,customAttributes = None):
        boolArrayValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Array,apptimize_ABTApptimizeVariableType.Boolean,customAttributes)
        if (boolArrayValue is None):
            return defaultValue
        return apptimize_util_ABTUtilArray.toNativeArray(boolArrayValue,apptimize_util_ArrayType.Bool)

    @staticmethod
    def getIntArray(name,defaultValue,userID,customAttributes = None):
        intArrayValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Array,apptimize_ABTApptimizeVariableType.Integer,customAttributes)
        if (intArrayValue is None):
            return defaultValue
        return apptimize_util_ABTUtilArray.toNativeArray(intArrayValue,apptimize_util_ArrayType.Int)

    @staticmethod
    def getDoubleArray(name,defaultValue,userID,customAttributes = None):
        doubleArrayValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Array,apptimize_ABTApptimizeVariableType.Double,customAttributes)
        if (doubleArrayValue is None):
            return defaultValue
        return apptimize_util_ABTUtilArray.toNativeArray(doubleArrayValue,apptimize_util_ArrayType.Double)

    @staticmethod
    def getStringDictionary(name,defaultValue,userID,customAttributes = None):
        stringDictionaryValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Dictionary,apptimize_ABTApptimizeVariableType.String,customAttributes)
        if (stringDictionaryValue is None):
            return defaultValue
        return stringDictionaryValue

    @staticmethod
    def getBoolDictionary(name,defaultValue,userID,customAttributes = None):
        boolDictionaryValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Dictionary,apptimize_ABTApptimizeVariableType.Boolean,customAttributes)
        if (boolDictionaryValue is None):
            return defaultValue
        return boolDictionaryValue

    @staticmethod
    def getIntDictionary(name,defaultValue,userID,customAttributes = None):
        intDictionaryValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Dictionary,apptimize_ABTApptimizeVariableType.Integer,customAttributes)
        if (intDictionaryValue is None):
            return defaultValue
        return intDictionaryValue

    @staticmethod
    def getDoubleDictionary(name,defaultValue,userID,customAttributes = None):
        doubleDictionaryValue = apptimize_Apptimize._getValue(name,userID,apptimize_ABTApptimizeVariableType.Dictionary,apptimize_ABTApptimizeVariableType.Double,customAttributes)
        if (doubleDictionaryValue is None):
            return defaultValue
        return doubleDictionaryValue

    @staticmethod
    def _getValue(name,userID,_hx_type,nestedType,customAttributes):
        if (not apptimize_Apptimize._isInitialized()):
            return None
        if ((not apptimize_util_ABTTypes.isNullOrString(userID)) or ((StringTools.ltrim(userID) == ""))):
            apptimize_ABTLogger.w("The `userID` argument cannot be set to a non-string value, be empty or be whitespace only, setting to null instead.",_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 46, 'className': "apptimize.Apptimize", 'methodName': "_getValue"}))
            userID = None
        if ((userID is None) and False):
            apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize._getValue"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 51, 'className': "apptimize.Apptimize", 'methodName': "_getValue"}))
        if ((customAttributes is None) and False):
            apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize._getValue"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 57, 'className': "apptimize.Apptimize", 'methodName': "_getValue"}))
        attrMap = apptimize_util_ABTUtilDictionary.nativeObjectToStringMap(customAttributes)
        envParams = apptimize_filter_ABTFilterEnvParams(userID,apptimize_Apptimize._getApptimizeAnonUserId(),attrMap,apptimize_ABTDataStore.getAppKey(),apptimize_support_properties_ABTApplicationProperties.sharedInstance())
        return apptimize_ABTApptimizeVariable.getValue(envParams,name,_hx_type,nestedType)

    @staticmethod
    def getVariantInfo(userID,customAttributes = None):
        if ((not apptimize_util_ABTTypes.isNullOrString(userID)) or ((StringTools.ltrim(userID) == ""))):
            apptimize_ABTLogger.w("The `userID` argument cannot be set to a non-string value, be empty or be whitespace only, setting to null instead.",_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 46, 'className': "apptimize.Apptimize", 'methodName': "getVariantInfo"}))
            userID = None
        if ((userID is None) and False):
            apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize.getVariantInfo"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 51, 'className': "apptimize.Apptimize", 'methodName': "getVariantInfo"}))
        if ((customAttributes is None) and False):
            apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize.getVariantInfo"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 57, 'className': "apptimize.Apptimize", 'methodName': "getVariantInfo"}))
        variantInfos = list()
        anonID = apptimize_Apptimize._getApptimizeAnonUserId()
        attrMap = apptimize_util_ABTUtilDictionary.nativeObjectToStringMap(customAttributes)
        envParams = apptimize_filter_ABTFilterEnvParams(userID,anonID,attrMap,apptimize_ABTDataStore.getAppKey(),apptimize_support_properties_ABTApplicationProperties.sharedInstance())
        _g = 0
        _g1 = apptimize_ApptimizeInternal._getVariants(envParams)
        while (_g < len(_g1)):
            variant = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            x = apptimize_VariantInfo.initWithVariant(variant,userID,anonID)
            variantInfos.append(x)
        return apptimize_util_ABTUtilArray.toNativeArray(variantInfos,apptimize_util_ArrayType.VariantInfo)

    @staticmethod
    def _getVariantInfoForAlteration(name,userID,customAttributes):
        anonID = apptimize_Apptimize._getApptimizeAnonUserId()
        _g = 0
        _g1 = apptimize_Apptimize._getAlterations(userID,customAttributes)
        while (_g < len(_g1)):
            alteration = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            if (alteration.getKey() == name):
                return apptimize_VariantInfo.initWithVariant(alteration.getVariant(),userID,anonID)
        return None

    @staticmethod
    def _getVariantInfoForDynamicVariable(name,userID,customAttributes = None):
        if ((not apptimize_util_ABTTypes.isNullOrString(userID)) or ((StringTools.ltrim(userID) == ""))):
            apptimize_ABTLogger.w("The `userID` argument cannot be set to a non-string value, be empty or be whitespace only, setting to null instead.",_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 46, 'className': "apptimize.Apptimize", 'methodName': "_getVariantInfoForDynamicVariable"}))
            userID = None
        if ((userID is None) and False):
            apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize._getVariantInfoForDynamicVariable"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 51, 'className': "apptimize.Apptimize", 'methodName': "_getVariantInfoForDynamicVariable"}))
        if ((customAttributes is None) and False):
            apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize._getVariantInfoForDynamicVariable"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 57, 'className': "apptimize.Apptimize", 'methodName': "_getVariantInfoForDynamicVariable"}))
        attrMap = apptimize_util_ABTUtilDictionary.nativeObjectToStringMap(customAttributes)
        return apptimize_Apptimize._getVariantInfoForAlteration(name,userID,attrMap)

    @staticmethod
    def _getVariantInfoForExperiment(name,userID,customAttributes = None):
        if ((not apptimize_util_ABTTypes.isNullOrString(userID)) or ((StringTools.ltrim(userID) == ""))):
            apptimize_ABTLogger.w("The `userID` argument cannot be set to a non-string value, be empty or be whitespace only, setting to null instead.",_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 46, 'className': "apptimize.Apptimize", 'methodName': "_getVariantInfoForExperiment"}))
            userID = None
        if ((userID is None) and False):
            apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize._getVariantInfoForExperiment"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 51, 'className': "apptimize.Apptimize", 'methodName': "_getVariantInfoForExperiment"}))
        if ((customAttributes is None) and False):
            apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize._getVariantInfoForExperiment"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 57, 'className': "apptimize.Apptimize", 'methodName': "_getVariantInfoForExperiment"}))
        anonID = apptimize_Apptimize._getApptimizeAnonUserId()
        attrMap = apptimize_util_ABTUtilDictionary.nativeObjectToStringMap(customAttributes)
        envParams = apptimize_filter_ABTFilterEnvParams(userID,anonID,attrMap,apptimize_ABTDataStore.getAppKey(),apptimize_support_properties_ABTApplicationProperties.sharedInstance())
        _g = 0
        _g1 = apptimize_ApptimizeInternal._getVariants(envParams)
        while (_g < len(_g1)):
            variant = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            if (variant.getExperimentName() == name):
                return apptimize_VariantInfo.initWithVariant(variant,userID,anonID)
        return None

    @staticmethod
    def track(eventName,userID,customAttributes = None):
        if apptimize_Apptimize._isInitialized():
            if ((not apptimize_util_ABTTypes.isNullOrString(userID)) or ((StringTools.ltrim(userID) == ""))):
                apptimize_ABTLogger.w("The `userID` argument cannot be set to a non-string value, be empty or be whitespace only, setting to null instead.",_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 46, 'className': "apptimize.Apptimize", 'methodName': "track"}))
                userID = None
            if ((userID is None) and False):
                apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize.track"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 51, 'className': "apptimize.Apptimize", 'methodName': "track"}))
            if ((customAttributes is None) and False):
                apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize.track"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 57, 'className': "apptimize.Apptimize", 'methodName': "track"}))
            attrMap = apptimize_util_ABTUtilDictionary.nativeObjectToStringMap(customAttributes)
            envParams = apptimize_filter_ABTFilterEnvParams(userID,apptimize_Apptimize._getApptimizeAnonUserId(),attrMap,apptimize_ABTDataStore.getAppKey(),apptimize_support_properties_ABTApplicationProperties.sharedInstance())
            apptimize_ApptimizeInternal.generateTrackEvent(envParams,eventName,None)
        else:
            apptimize_ABTLogger.w("Events can only be tracked after setup() has been called.",_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 1192, 'className': "apptimize.Apptimize", 'methodName': "track"}))

    @staticmethod
    def trackValue(eventName,value,userID,customAttributes = None):
        if apptimize_Apptimize._isInitialized():
            if ((not apptimize_util_ABTTypes.isNullOrString(userID)) or ((StringTools.ltrim(userID) == ""))):
                apptimize_ABTLogger.w("The `userID` argument cannot be set to a non-string value, be empty or be whitespace only, setting to null instead.",_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 46, 'className': "apptimize.Apptimize", 'methodName': "trackValue"}))
                userID = None
            if ((userID is None) and False):
                apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize.trackValue"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 51, 'className': "apptimize.Apptimize", 'methodName': "trackValue"}))
            if ((customAttributes is None) and False):
                apptimize_ABTLogger.c(((("The parameter " + HxOverrides.stringOrNull(None)) + " is required for ") + "apptimize.Apptimize.trackValue"),_hx_AnonObject({'fileName': "src/apptimize/macros/ABTClientMacro.hx", 'lineNumber': 57, 'className': "apptimize.Apptimize", 'methodName': "trackValue"}))
            if ((not Std.isOfType(value,Float)) and (not Std.isOfType(value,apptimize_util_ArrayType.Int))):
                apptimize_ABTLogger.w("trackValue() called with a non-float value. Event not logged.",_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 1223, 'className': "apptimize.Apptimize", 'methodName': "trackValue"}))
                return
            attrMap = apptimize_util_ABTUtilDictionary.nativeObjectToStringMap(customAttributes)
            envParams = apptimize_filter_ABTFilterEnvParams(userID,apptimize_Apptimize._getApptimizeAnonUserId(),attrMap,apptimize_ABTDataStore.getAppKey(),apptimize_support_properties_ABTApplicationProperties.sharedInstance())
            apptimize_ApptimizeInternal.generateTrackEvent(envParams,eventName,value)
        else:
            apptimize_ABTLogger.w("Events can only be tracked after setup() has been called.",_hx_AnonObject({'fileName': "src/apptimize/Apptimize.hx", 'lineNumber': 1231, 'className': "apptimize.Apptimize", 'methodName': "trackValue"}))
apptimize_Apptimize._hx_class = apptimize_Apptimize
_hx_classes["apptimize.Apptimize"] = apptimize_Apptimize


class Apptimize(apptimize_Apptimize):
    _hx_class_name = "Apptimize"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = []
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_Apptimize

Apptimize._hx_class = Apptimize
_hx_classes["Apptimize"] = Apptimize


class apptimize_VariantInfo:
    _hx_class_name = "apptimize.VariantInfo"
    __slots__ = ("_variantId", "_variantName", "_experimentId", "_experimentName", "_experimentType", "_experimentTypeName", "_currentPhase", "_participationPhase", "_cycle", "_userId", "_anonymousUserId", "_userHasParticipated")
    _hx_fields = ["_variantId", "_variantName", "_experimentId", "_experimentName", "_experimentType", "_experimentTypeName", "_currentPhase", "_participationPhase", "_cycle", "_userId", "_anonymousUserId", "_userHasParticipated"]
    _hx_methods = ["getVariantId", "getVariantName", "getExperimentId", "getExperimentName", "getExperimentType", "getExperimentTypeName", "getCurrentPhase", "getParticipationPhase", "getCycle", "getUserId", "getAnonymousUserId"]
    _hx_statics = ["initWithVariant", "apptimizeExperimentTypeForString"]

    def __init__(self,variantId,variantName,experimentId,experimentName,experimentType,cycle,currentPhase,participationPhase,userId,anonymousUserId,userHasParticipated):
        self._variantId = variantId
        self._variantName = variantName
        self._experimentId = experimentId
        self._experimentName = experimentName
        self._experimentType = apptimize_VariantInfo.apptimizeExperimentTypeForString(experimentType)
        self._experimentTypeName = experimentType
        self._cycle = cycle
        self._currentPhase = currentPhase
        self._participationPhase = participationPhase
        self._userId = userId
        self._anonymousUserId = anonymousUserId
        self._userHasParticipated = userHasParticipated

    def getVariantId(self):
        return self._variantId

    def getVariantName(self):
        return self._variantName

    def getExperimentId(self):
        return self._experimentId

    def getExperimentName(self):
        return self._experimentName

    def getExperimentType(self):
        return self._experimentType

    def getExperimentTypeName(self):
        return self._experimentTypeName

    def getCurrentPhase(self):
        return self._currentPhase

    def getParticipationPhase(self):
        return self._participationPhase

    def getCycle(self):
        return self._cycle

    def getUserId(self):
        return self._userId

    def getAnonymousUserId(self):
        return self._anonymousUserId

    @staticmethod
    def initWithVariant(variant,userId,anonymousUserId):
        participationPhase = 0
        variantString = ((("v" + Std.string(variant.getVariantID())) + "_") + Std.string(variant.getCycle()))
        userHasParticipated = False
        return apptimize_VariantInfo(variant.getVariantID(),variant.getVariantName(),variant.getExperimentID(),variant.getExperimentName(),variant.getExperimentType(),variant.getCycle(),variant.getPhase(),participationPhase,userId,anonymousUserId,userHasParticipated)

    @staticmethod
    def apptimizeExperimentTypeForString(stringType):
        _hx_type = stringType.lower()
        type1 = _hx_type
        _hx_local_0 = len(type1)
        if (_hx_local_0 == 10):
            if (type1 == "code-block"):
                return apptimize_ApptimizeExperimentType.CodeBlock
            else:
                return apptimize_ApptimizeExperimentType.Unknown
        elif (_hx_local_0 == 9):
            if (type1 == "int-value"):
                return apptimize_ApptimizeExperimentType.DynamicVariables
            elif (type1 == "variables"):
                return apptimize_ApptimizeExperimentType.DynamicVariables
            else:
                return apptimize_ApptimizeExperimentType.Unknown
        elif (_hx_local_0 == 12):
            if (type1 == "double-value"):
                return apptimize_ApptimizeExperimentType.DynamicVariables
            elif (type1 == "feature-flag"):
                return apptimize_ApptimizeExperimentType.FeatureFlag
            elif (type1 == "string-value"):
                return apptimize_ApptimizeExperimentType.DynamicVariables
            else:
                return apptimize_ApptimizeExperimentType.Unknown
        elif (_hx_local_0 == 7):
            if (type1 == "wysiwyg"):
                return apptimize_ApptimizeExperimentType.Visual
            else:
                return apptimize_ApptimizeExperimentType.Unknown
        elif (_hx_local_0 == 14):
            if (type1 == "feature-config"):
                return apptimize_ApptimizeExperimentType.FeatureVariables
            else:
                return apptimize_ApptimizeExperimentType.Unknown
        else:
            return apptimize_ApptimizeExperimentType.Unknown

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._variantId = None
        _hx_o._variantName = None
        _hx_o._experimentId = None
        _hx_o._experimentName = None
        _hx_o._experimentType = None
        _hx_o._experimentTypeName = None
        _hx_o._currentPhase = None
        _hx_o._participationPhase = None
        _hx_o._cycle = None
        _hx_o._userId = None
        _hx_o._anonymousUserId = None
        _hx_o._userHasParticipated = None
apptimize_VariantInfo._hx_class = apptimize_VariantInfo
_hx_classes["apptimize.VariantInfo"] = apptimize_VariantInfo


class VariantInfo(apptimize_VariantInfo):
    _hx_class_name = "VariantInfo"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = []
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_VariantInfo


    def __init__(self,variantId,variantName,experimentId,experimentName,experimentType,cycle,currentPhase,participationPhase,userId,anonymousUserId,userHasParticipated):
        super().__init__(variantId,variantName,experimentId,experimentName,experimentType,cycle,currentPhase,participationPhase,userId,anonymousUserId,userHasParticipated)
VariantInfo._hx_class = VariantInfo
_hx_classes["VariantInfo"] = VariantInfo


class Class: pass


class Date:
    _hx_class_name = "Date"
    __slots__ = ("date", "dateUTC")
    _hx_fields = ["date", "dateUTC"]
    _hx_methods = ["toString"]
    _hx_statics = ["now", "fromTime", "makeLocal", "fromString"]

    def __init__(self,year,month,day,hour,_hx_min,sec):
        self.dateUTC = None
        if (year < python_lib_datetime_Datetime.min.year):
            year = python_lib_datetime_Datetime.min.year
        if (day == 0):
            day = 1
        self.date = Date.makeLocal(python_lib_datetime_Datetime(year,(month + 1),day,hour,_hx_min,sec,0))
        self.dateUTC = self.date.astimezone(python_lib_datetime_Timezone.utc)

    def toString(self):
        return self.date.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def now():
        d = Date(2000,0,1,0,0,0)
        d.date = Date.makeLocal(python_lib_datetime_Datetime.now())
        d.dateUTC = d.date.astimezone(python_lib_datetime_Timezone.utc)
        return d

    @staticmethod
    def fromTime(t):
        d = Date(2000,0,1,0,0,0)
        d.date = Date.makeLocal(python_lib_datetime_Datetime.fromtimestamp((t / 1000.0)))
        d.dateUTC = d.date.astimezone(python_lib_datetime_Timezone.utc)
        return d

    @staticmethod
    def makeLocal(date):
        try:
            return date.astimezone()
        except BaseException as _g:
            None
            tzinfo = python_lib_datetime_Datetime.now(python_lib_datetime_Timezone.utc).astimezone().tzinfo
            return date.replace(**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'tzinfo': tzinfo})))

    @staticmethod
    def fromString(s):
        _g = len(s)
        if (_g == 8):
            k = s.split(":")
            return Date.fromTime((((Std.parseInt((k[0] if 0 < len(k) else None)) * 3600000.) + ((Std.parseInt((k[1] if 1 < len(k) else None)) * 60000.))) + ((Std.parseInt((k[2] if 2 < len(k) else None)) * 1000.))))
        elif (_g == 10):
            k = s.split("-")
            return Date(Std.parseInt((k[0] if 0 < len(k) else None)),(Std.parseInt((k[1] if 1 < len(k) else None)) - 1),Std.parseInt((k[2] if 2 < len(k) else None)),0,0,0)
        elif (_g == 19):
            k = s.split(" ")
            _this = (k[0] if 0 < len(k) else None)
            y = _this.split("-")
            _this = (k[1] if 1 < len(k) else None)
            t = _this.split(":")
            return Date(Std.parseInt((y[0] if 0 < len(y) else None)),(Std.parseInt((y[1] if 1 < len(y) else None)) - 1),Std.parseInt((y[2] if 2 < len(y) else None)),Std.parseInt((t[0] if 0 < len(t) else None)),Std.parseInt((t[1] if 1 < len(t) else None)),Std.parseInt((t[2] if 2 < len(t) else None)))
        else:
            raise haxe_Exception.thrown(("Invalid date format : " + ("null" if s is None else s)))

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.date = None
        _hx_o.dateUTC = None
Date._hx_class = Date
_hx_classes["Date"] = Date


class EReg:
    _hx_class_name = "EReg"
    __slots__ = ("pattern", "matchObj", "_hx_global")
    _hx_fields = ["pattern", "matchObj", "global"]
    _hx_methods = ["replace", "map"]

    def __init__(self,r,opt):
        self.matchObj = None
        self._hx_global = False
        options = 0
        _g = 0
        _g1 = len(opt)
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            c = (-1 if ((i >= len(opt))) else ord(opt[i]))
            if (c == 109):
                options = (options | python_lib_Re.M)
            if (c == 105):
                options = (options | python_lib_Re.I)
            if (c == 115):
                options = (options | python_lib_Re.S)
            if (c == 117):
                options = (options | python_lib_Re.U)
            if (c == 103):
                self._hx_global = True
        self.pattern = python_lib_Re.compile(r,options)

    def replace(self,s,by):
        _this = by.split("$$")
        by = "_hx_#repl#__".join([python_Boot.toString1(x1,'') for x1 in _this])
        def _hx_local_0(x):
            res = by
            g = x.groups()
            _g = 0
            _g1 = len(g)
            while (_g < _g1):
                i = _g
                _g = (_g + 1)
                gs = g[i]
                if (gs is None):
                    continue
                delimiter = ("$" + HxOverrides.stringOrNull(str((i + 1))))
                _this = (list(res) if ((delimiter == "")) else res.split(delimiter))
                res = gs.join([python_Boot.toString1(x1,'') for x1 in _this])
            _this = res.split("_hx_#repl#__")
            res = "$".join([python_Boot.toString1(x1,'') for x1 in _this])
            return res
        replace = _hx_local_0
        return python_lib_Re.sub(self.pattern,replace,s,(0 if (self._hx_global) else 1))

    def map(self,s,f):
        buf_b = python_lib_io_StringIO()
        pos = 0
        right = s
        cur = self
        while (pos < len(s)):
            if (self.matchObj is None):
                self.matchObj = python_lib_Re.search(self.pattern,s)
            else:
                self.matchObj = self.matchObj.re.search(s,pos)
            if (self.matchObj is None):
                break
            pos1 = self.matchObj.end()
            curPos_pos = cur.matchObj.start()
            curPos_len = (cur.matchObj.end() - cur.matchObj.start())
            buf_b.write(Std.string(HxString.substr(HxString.substr(cur.matchObj.string,0,cur.matchObj.start()),pos,None)))
            buf_b.write(Std.string(f(cur)))
            right = HxString.substr(cur.matchObj.string,cur.matchObj.end(),None)
            if (not self._hx_global):
                buf_b.write(Std.string(right))
                return buf_b.getvalue()
            if (curPos_len == 0):
                buf_b.write(Std.string(("" if (((pos1 < 0) or ((pos1 >= len(s))))) else s[pos1])))
                right = HxString.substr(right,1,None)
                pos = (pos1 + 1)
            else:
                pos = pos1
        buf_b.write(Std.string(right))
        return buf_b.getvalue()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.pattern = None
        _hx_o.matchObj = None
        _hx_o._hx_global = None
EReg._hx_class = EReg
_hx_classes["EReg"] = EReg


class Lambda:
    _hx_class_name = "Lambda"
    __slots__ = ()
    _hx_statics = ["array"]

    @staticmethod
    def array(it):
        a = list()
        i = HxOverrides.iterator(it)
        while i.hasNext():
            i1 = i.next()
            a.append(i1)
        return a
Lambda._hx_class = Lambda
_hx_classes["Lambda"] = Lambda


class _Math_Math_Impl_:
    _hx_class_name = "_Math.Math_Impl_"
    __slots__ = ()
    _hx_statics = ["random"]

    @staticmethod
    def random():
        return python_lib_Random.random()
_Math_Math_Impl_._hx_class = _Math_Math_Impl_
_hx_classes["_Math.Math_Impl_"] = _Math_Math_Impl_


class Reflect:
    _hx_class_name = "Reflect"
    __slots__ = ()
    _hx_statics = ["field", "setField", "getProperty", "callMethod", "isFunction"]

    @staticmethod
    def field(o,field):
        return python_Boot.field(o,field)

    @staticmethod
    def setField(o,field,value):
        setattr(o,(("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field)),value)

    @staticmethod
    def getProperty(o,field):
        if (o is None):
            return None
        if (field in python_Boot.keywords):
            field = ("_hx_" + field)
        elif ((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95))):
            field = ("_hx_" + field)
        if isinstance(o,_hx_AnonObject):
            return Reflect.field(o,field)
        tmp = Reflect.field(o,("get_" + ("null" if field is None else field)))
        if ((tmp is not None) and callable(tmp)):
            return tmp()
        else:
            return Reflect.field(o,field)

    @staticmethod
    def callMethod(o,func,args):
        if callable(func):
            return func(*args)
        else:
            return None

    @staticmethod
    def isFunction(f):
        if (not ((python_lib_Inspect.isfunction(f) or python_lib_Inspect.ismethod(f)))):
            return python_Boot.hasField(f,"func_code")
        else:
            return True
Reflect._hx_class = Reflect
_hx_classes["Reflect"] = Reflect


class Std:
    _hx_class_name = "Std"
    __slots__ = ()
    _hx_statics = ["is", "isOfType", "string", "parseInt", "shortenPossibleNumber", "parseFloat"]

    @staticmethod
    def _hx_is(v,t):
        return Std.isOfType(v,t)

    @staticmethod
    def isOfType(v,t):
        if ((v is None) and ((t is None))):
            return False
        if (t is None):
            return False
        if (t == Dynamic):
            return (v is not None)
        isBool = isinstance(v,bool)
        if ((t == Bool) and isBool):
            return True
        if ((((not isBool) and (not (t == Bool))) and (t == Int)) and isinstance(v,int)):
            return True
        vIsFloat = isinstance(v,float)
        tmp = None
        tmp1 = None
        if (((not isBool) and vIsFloat) and (t == Int)):
            f = v
            tmp1 = (((f != Math.POSITIVE_INFINITY) and ((f != Math.NEGATIVE_INFINITY))) and (not python_lib_Math.isnan(f)))
        else:
            tmp1 = False
        if tmp1:
            tmp1 = None
            try:
                tmp1 = int(v)
            except BaseException as _g:
                None
                tmp1 = None
            tmp = (v == tmp1)
        else:
            tmp = False
        if ((tmp and ((v <= 2147483647))) and ((v >= -2147483648))):
            return True
        if (((not isBool) and (t == Float)) and isinstance(v,(float, int))):
            return True
        if (t == str):
            return isinstance(v,str)
        isEnumType = (t == Enum)
        if ((isEnumType and python_lib_Inspect.isclass(v)) and hasattr(v,"_hx_constructs")):
            return True
        if isEnumType:
            return False
        isClassType = (t == Class)
        if ((((isClassType and (not isinstance(v,Enum))) and python_lib_Inspect.isclass(v)) and hasattr(v,"_hx_class_name")) and (not hasattr(v,"_hx_constructs"))):
            return True
        if isClassType:
            return False
        tmp = None
        try:
            tmp = isinstance(v,t)
        except BaseException as _g:
            None
            tmp = False
        if tmp:
            return True
        if python_lib_Inspect.isclass(t):
            cls = t
            loop = None
            def _hx_local_1(intf):
                f = (intf._hx_interfaces if (hasattr(intf,"_hx_interfaces")) else [])
                if (f is not None):
                    _g = 0
                    while (_g < len(f)):
                        i = (f[_g] if _g >= 0 and _g < len(f) else None)
                        _g = (_g + 1)
                        if (i == cls):
                            return True
                        else:
                            l = loop(i)
                            if l:
                                return True
                    return False
                else:
                    return False
            loop = _hx_local_1
            currentClass = v.__class__
            result = False
            while (currentClass is not None):
                if loop(currentClass):
                    result = True
                    break
                currentClass = python_Boot.getSuperClass(currentClass)
            return result
        else:
            return False

    @staticmethod
    def string(s):
        return python_Boot.toString1(s,"")

    @staticmethod
    def parseInt(x):
        if (x is None):
            return None
        try:
            return int(x)
        except BaseException as _g:
            None
            base = 10
            _hx_len = len(x)
            foundCount = 0
            sign = 0
            firstDigitIndex = 0
            lastDigitIndex = -1
            previous = 0
            _g = 0
            _g1 = _hx_len
            while (_g < _g1):
                i = _g
                _g = (_g + 1)
                c = (-1 if ((i >= len(x))) else ord(x[i]))
                if (((c > 8) and ((c < 14))) or ((c == 32))):
                    if (foundCount > 0):
                        return None
                    continue
                else:
                    c1 = c
                    if (c1 == 43):
                        if (foundCount == 0):
                            sign = 1
                        elif (not (((48 <= c) and ((c <= 57))))):
                            if (not (((base == 16) and ((((97 <= c) and ((c <= 122))) or (((65 <= c) and ((c <= 90))))))))):
                                break
                    elif (c1 == 45):
                        if (foundCount == 0):
                            sign = -1
                        elif (not (((48 <= c) and ((c <= 57))))):
                            if (not (((base == 16) and ((((97 <= c) and ((c <= 122))) or (((65 <= c) and ((c <= 90))))))))):
                                break
                    elif (c1 == 48):
                        if (not (((foundCount == 0) or (((foundCount == 1) and ((sign != 0))))))):
                            if (not (((48 <= c) and ((c <= 57))))):
                                if (not (((base == 16) and ((((97 <= c) and ((c <= 122))) or (((65 <= c) and ((c <= 90))))))))):
                                    break
                    elif ((c1 == 120) or ((c1 == 88))):
                        if ((previous == 48) and ((((foundCount == 1) and ((sign == 0))) or (((foundCount == 2) and ((sign != 0))))))):
                            base = 16
                        elif (not (((48 <= c) and ((c <= 57))))):
                            if (not (((base == 16) and ((((97 <= c) and ((c <= 122))) or (((65 <= c) and ((c <= 90))))))))):
                                break
                    elif (not (((48 <= c) and ((c <= 57))))):
                        if (not (((base == 16) and ((((97 <= c) and ((c <= 122))) or (((65 <= c) and ((c <= 90))))))))):
                            break
                if (((foundCount == 0) and ((sign == 0))) or (((foundCount == 1) and ((sign != 0))))):
                    firstDigitIndex = i
                foundCount = (foundCount + 1)
                lastDigitIndex = i
                previous = c
            if (firstDigitIndex <= lastDigitIndex):
                digits = HxString.substring(x,firstDigitIndex,(lastDigitIndex + 1))
                try:
                    return (((-1 if ((sign == -1)) else 1)) * int(digits,base))
                except BaseException as _g:
                    return None
            return None

    @staticmethod
    def shortenPossibleNumber(x):
        r = ""
        _g = 0
        _g1 = len(x)
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            c = ("" if (((i < 0) or ((i >= len(x))))) else x[i])
            _g2 = HxString.charCodeAt(c,0)
            if (_g2 is None):
                break
            else:
                _g3 = _g2
                if (((((((((((_g3 == 57) or ((_g3 == 56))) or ((_g3 == 55))) or ((_g3 == 54))) or ((_g3 == 53))) or ((_g3 == 52))) or ((_g3 == 51))) or ((_g3 == 50))) or ((_g3 == 49))) or ((_g3 == 48))) or ((_g3 == 46))):
                    r = (("null" if r is None else r) + ("null" if c is None else c))
                else:
                    break
        return r

    @staticmethod
    def parseFloat(x):
        try:
            return float(x)
        except BaseException as _g:
            None
            if (x is not None):
                r1 = Std.shortenPossibleNumber(x)
                if (r1 != x):
                    return Std.parseFloat(r1)
            return Math.NaN
Std._hx_class = Std
_hx_classes["Std"] = Std


class Float: pass


class Int: pass


class Bool: pass


class Dynamic: pass


class StringBuf:
    _hx_class_name = "StringBuf"
    __slots__ = ("b",)
    _hx_fields = ["b"]
    _hx_methods = ["get_length"]

    def __init__(self):
        self.b = python_lib_io_StringIO()

    def get_length(self):
        pos = self.b.tell()
        self.b.seek(0,2)
        _hx_len = self.b.tell()
        self.b.seek(pos,0)
        return _hx_len

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.b = None
StringBuf._hx_class = StringBuf
_hx_classes["StringBuf"] = StringBuf


class StringTools:
    _hx_class_name = "StringTools"
    __slots__ = ()
    _hx_statics = ["isSpace", "ltrim", "rtrim", "trim", "lpad", "replace", "hex"]

    @staticmethod
    def isSpace(s,pos):
        if (((len(s) == 0) or ((pos < 0))) or ((pos >= len(s)))):
            return False
        c = HxString.charCodeAt(s,pos)
        if (not (((c > 8) and ((c < 14))))):
            return (c == 32)
        else:
            return True

    @staticmethod
    def ltrim(s):
        l = len(s)
        r = 0
        while ((r < l) and StringTools.isSpace(s,r)):
            r = (r + 1)
        if (r > 0):
            return HxString.substr(s,r,(l - r))
        else:
            return s

    @staticmethod
    def rtrim(s):
        l = len(s)
        r = 0
        while ((r < l) and StringTools.isSpace(s,((l - r) - 1))):
            r = (r + 1)
        if (r > 0):
            return HxString.substr(s,0,(l - r))
        else:
            return s

    @staticmethod
    def trim(s):
        return StringTools.ltrim(StringTools.rtrim(s))

    @staticmethod
    def lpad(s,c,l):
        if (len(c) <= 0):
            return s
        buf = StringBuf()
        l = (l - len(s))
        while (buf.get_length() < l):
            s1 = Std.string(c)
            buf.b.write(s1)
        s1 = Std.string(s)
        buf.b.write(s1)
        return buf.b.getvalue()

    @staticmethod
    def replace(s,sub,by):
        _this = (list(s) if ((sub == "")) else s.split(sub))
        return by.join([python_Boot.toString1(x1,'') for x1 in _this])

    @staticmethod
    def hex(n,digits = None):
        s = ""
        hexChars = "0123456789ABCDEF"
        while True:
            index = (n & 15)
            s = (HxOverrides.stringOrNull((("" if (((index < 0) or ((index >= len(hexChars))))) else hexChars[index]))) + ("null" if s is None else s))
            n = HxOverrides.rshift(n, 4)
            if (not ((n > 0))):
                break
        if ((digits is not None) and ((len(s) < digits))):
            diff = (digits - len(s))
            _g = 0
            _g1 = diff
            while (_g < _g1):
                _ = _g
                _g = (_g + 1)
                s = ("0" + ("null" if s is None else s))
        return s
StringTools._hx_class = StringTools
_hx_classes["StringTools"] = StringTools


class sys_FileSystem:
    _hx_class_name = "sys.FileSystem"
    __slots__ = ()
    _hx_statics = ["exists", "createDirectory", "deleteFile"]

    @staticmethod
    def exists(path):
        return python_lib_os_Path.exists(path)

    @staticmethod
    def createDirectory(path):
        python_lib_Os.makedirs(path,511,True)

    @staticmethod
    def deleteFile(path):
        python_lib_Os.remove(path)
sys_FileSystem._hx_class = sys_FileSystem
_hx_classes["sys.FileSystem"] = sys_FileSystem


class Sys:
    _hx_class_name = "Sys"
    __slots__ = ()
    _hx_statics = ["sleep", "systemName"]

    @staticmethod
    def sleep(seconds):
        python_lib_Time.sleep(seconds)

    @staticmethod
    def systemName():
        _g = python_lib_Sys.platform
        x = _g
        if x.startswith("linux"):
            return "Linux"
        else:
            _g1 = _g
            _hx_local_0 = len(_g1)
            if (_hx_local_0 == 5):
                if (_g1 == "win32"):
                    return "Windows"
                else:
                    raise haxe_Exception.thrown("not supported platform")
            elif (_hx_local_0 == 6):
                if (_g1 == "cygwin"):
                    return "Windows"
                elif (_g1 == "darwin"):
                    return "Mac"
                else:
                    raise haxe_Exception.thrown("not supported platform")
            else:
                raise haxe_Exception.thrown("not supported platform")
Sys._hx_class = Sys
_hx_classes["Sys"] = Sys

class ValueType(Enum):
    __slots__ = ()
    _hx_class_name = "ValueType"
    _hx_constructs = ["TNull", "TInt", "TFloat", "TBool", "TObject", "TFunction", "TClass", "TEnum", "TUnknown"]

    @staticmethod
    def TClass(c):
        return ValueType("TClass", 6, (c,))

    @staticmethod
    def TEnum(e):
        return ValueType("TEnum", 7, (e,))
ValueType.TNull = ValueType("TNull", 0, ())
ValueType.TInt = ValueType("TInt", 1, ())
ValueType.TFloat = ValueType("TFloat", 2, ())
ValueType.TBool = ValueType("TBool", 3, ())
ValueType.TObject = ValueType("TObject", 4, ())
ValueType.TFunction = ValueType("TFunction", 5, ())
ValueType.TUnknown = ValueType("TUnknown", 8, ())
ValueType._hx_class = ValueType
_hx_classes["ValueType"] = ValueType


class Type:
    _hx_class_name = "Type"
    __slots__ = ()
    _hx_statics = ["getClass", "getSuperClass", "getClassName", "getEnumName", "resolveClass", "resolveEnum", "createEmptyInstance", "createEnum", "getEnumConstructs", "typeof"]

    @staticmethod
    def getClass(o):
        if (o is None):
            return None
        o1 = o
        if ((o1 is not None) and ((HxOverrides.eq(o1,str) or python_lib_Inspect.isclass(o1)))):
            return None
        if isinstance(o,_hx_AnonObject):
            return None
        if hasattr(o,"_hx_class"):
            return o._hx_class
        if hasattr(o,"__class__"):
            return o.__class__
        else:
            return None

    @staticmethod
    def getSuperClass(c):
        return python_Boot.getSuperClass(c)

    @staticmethod
    def getClassName(c):
        if hasattr(c,"_hx_class_name"):
            return c._hx_class_name
        else:
            if (c == list):
                return "Array"
            if (c == Math):
                return "Math"
            if (c == str):
                return "String"
            try:
                return c.__name__
            except BaseException as _g:
                None
                return None

    @staticmethod
    def getEnumName(e):
        return e._hx_class_name

    @staticmethod
    def resolveClass(name):
        if (name == "Array"):
            return list
        if (name == "Math"):
            return Math
        if (name == "String"):
            return str
        cl = _hx_classes.get(name,None)
        tmp = None
        if (cl is not None):
            o = cl
            tmp = (not (((o is not None) and ((HxOverrides.eq(o,str) or python_lib_Inspect.isclass(o))))))
        else:
            tmp = True
        if tmp:
            return None
        return cl

    @staticmethod
    def resolveEnum(name):
        if (name == "Bool"):
            return Bool
        o = Type.resolveClass(name)
        if hasattr(o,"_hx_constructs"):
            return o
        else:
            return None

    @staticmethod
    def createEmptyInstance(cl):
        i = cl.__new__(cl)
        callInit = None
        def _hx_local_0(cl):
            sc = Type.getSuperClass(cl)
            if (sc is not None):
                callInit(sc)
            if hasattr(cl,"_hx_empty_init"):
                cl._hx_empty_init(i)
        callInit = _hx_local_0
        callInit(cl)
        return i

    @staticmethod
    def createEnum(e,constr,params = None):
        f = Reflect.field(e,constr)
        if (f is None):
            raise haxe_Exception.thrown(("No such constructor " + ("null" if constr is None else constr)))
        if Reflect.isFunction(f):
            if (params is None):
                raise haxe_Exception.thrown((("Constructor " + ("null" if constr is None else constr)) + " need parameters"))
            return Reflect.callMethod(e,f,params)
        if ((params is not None) and ((len(params) != 0))):
            raise haxe_Exception.thrown((("Constructor " + ("null" if constr is None else constr)) + " does not need parameters"))
        return f

    @staticmethod
    def getEnumConstructs(e):
        if hasattr(e,"_hx_constructs"):
            x = e._hx_constructs
            return list(x)
        else:
            return []

    @staticmethod
    def typeof(v):
        if (v is None):
            return ValueType.TNull
        elif isinstance(v,bool):
            return ValueType.TBool
        elif isinstance(v,int):
            return ValueType.TInt
        elif isinstance(v,float):
            return ValueType.TFloat
        elif isinstance(v,str):
            return ValueType.TClass(str)
        elif isinstance(v,list):
            return ValueType.TClass(list)
        elif (isinstance(v,_hx_AnonObject) or python_lib_Inspect.isclass(v)):
            return ValueType.TObject
        elif isinstance(v,Enum):
            return ValueType.TEnum(v.__class__)
        elif (isinstance(v,type) or hasattr(v,"_hx_class")):
            return ValueType.TClass(v.__class__)
        elif callable(v):
            return ValueType.TFunction
        else:
            return ValueType.TUnknown
Type._hx_class = Type
_hx_classes["Type"] = Type

class apptimize_ABTApptimizeVariableType(Enum):
    __slots__ = ()
    _hx_class_name = "apptimize.ABTApptimizeVariableType"
    _hx_constructs = ["Invalid", "String", "Double", "Integer", "Boolean", "Array", "Dictionary"]
apptimize_ABTApptimizeVariableType.Invalid = apptimize_ABTApptimizeVariableType("Invalid", 0, ())
apptimize_ABTApptimizeVariableType.String = apptimize_ABTApptimizeVariableType("String", 1, ())
apptimize_ABTApptimizeVariableType.Double = apptimize_ABTApptimizeVariableType("Double", 2, ())
apptimize_ABTApptimizeVariableType.Integer = apptimize_ABTApptimizeVariableType("Integer", 3, ())
apptimize_ABTApptimizeVariableType.Boolean = apptimize_ABTApptimizeVariableType("Boolean", 4, ())
apptimize_ABTApptimizeVariableType.Array = apptimize_ABTApptimizeVariableType("Array", 5, ())
apptimize_ABTApptimizeVariableType.Dictionary = apptimize_ABTApptimizeVariableType("Dictionary", 6, ())
apptimize_ABTApptimizeVariableType._hx_class = apptimize_ABTApptimizeVariableType
_hx_classes["apptimize.ABTApptimizeVariableType"] = apptimize_ABTApptimizeVariableType


class apptimize_ABTApptimizeVariable:
    _hx_class_name = "apptimize.ABTApptimizeVariable"
    __slots__ = ()
    _hx_statics = ["getValue", "apptimizeVariableTypeForString"]

    @staticmethod
    def getValue(params,name,_hx_type,nestedType = None):
        apptimize_ABTDataStore._checkForUpdatedMetadataIfNecessary()
        metadata = apptimize_ABTDataStore.sharedInstance().getMetaData(params.appkey)
        if (metadata is None):
            return None
        env = metadata.makeEnvironment(params)
        alterations = metadata.selectAlterationsIntoArray(env)
        _g = 0
        while (_g < len(alterations)):
            alteration = (alterations[_g] if _g >= 0 and _g < len(alterations) else None)
            _g = (_g + 1)
            try:
                if (alteration.getKey() == name):
                    def _hx_local_2():
                        _hx_local_1 = alteration
                        if (Std.isOfType(_hx_local_1,apptimize_models_ABTValueAlteration) or ((_hx_local_1 is None))):
                            _hx_local_1
                        else:
                            raise "Class cast error"
                        return _hx_local_1
                    valueAlteration = _hx_local_2()
                    alterationType = apptimize_ABTApptimizeVariable.apptimizeVariableTypeForString(valueAlteration.getType())
                    alterationNestedType = None
                    if (valueAlteration.getNestedType() is not None):
                        alterationNestedType = apptimize_ABTApptimizeVariable.apptimizeVariableTypeForString(valueAlteration.getNestedType())
                    if ((alterationType == _hx_type) and ((alterationNestedType == nestedType))):
                        variant = valueAlteration.getVariant()
                        apptimize_ABTDataStore.sharedInstance().incrementVariantRunCount(params,variant)
                        if (not valueAlteration.useDefaultValue()):
                            return valueAlteration.getValue()
            except BaseException as _g1:
                None
                if Std.isOfType(haxe_Exception.caught(_g1).unwrap(),str):
                    apptimize_ABTLogger.v((("Alteration found for key \"" + HxOverrides.stringOrNull(alteration.getKey())) + "\" isn't a value alteration."),_hx_AnonObject({'fileName': "src/apptimize/ABTApptimizeVariable.hx", 'lineNumber': 57, 'className': "apptimize.ABTApptimizeVariable", 'methodName': "getValue"}))
                    return None
                else:
                    raise _g1
        apptimize_ABTLogger.v((("No alteration found for dynamic variable \"" + ("null" if name is None else name)) + "\"."),_hx_AnonObject({'fileName': "src/apptimize/ABTApptimizeVariable.hx", 'lineNumber': 62, 'className': "apptimize.ABTApptimizeVariable", 'methodName': "getValue"}))
        return None

    @staticmethod
    def apptimizeVariableTypeForString(stringType):
        _hx_type = stringType.lower()
        if (_hx_type == "string"):
            return apptimize_ABTApptimizeVariableType.String
        elif (_hx_type == "double"):
            return apptimize_ABTApptimizeVariableType.Double
        elif (_hx_type == "int"):
            return apptimize_ABTApptimizeVariableType.Integer
        elif (_hx_type == "boolean"):
            return apptimize_ABTApptimizeVariableType.Boolean
        elif (_hx_type == "list"):
            return apptimize_ABTApptimizeVariableType.Array
        elif (_hx_type == "dictionary"):
            return apptimize_ABTApptimizeVariableType.Dictionary
        else:
            return apptimize_ABTApptimizeVariableType.Invalid
apptimize_ABTApptimizeVariable._hx_class = apptimize_ABTApptimizeVariable
_hx_classes["apptimize.ABTApptimizeVariable"] = apptimize_ABTApptimizeVariable


class apptimize_util_PlatformLock:
    _hx_class_name = "apptimize.util.PlatformLock"
    __slots__ = ()
    _hx_methods = ["acquire", "release"]
apptimize_util_PlatformLock._hx_class = apptimize_util_PlatformLock
_hx_classes["apptimize.util.PlatformLock"] = apptimize_util_PlatformLock


class apptimize_util_PythonPlatformLock:
    _hx_class_name = "apptimize.util.PythonPlatformLock"
    __slots__ = ("_lock",)
    _hx_fields = ["_lock"]
    _hx_methods = ["init", "acquire", "release", "hxUnserialize"]
    _hx_interfaces = [apptimize_util_PlatformLock]

    def __init__(self):
        self._lock = None
        self.init()

    def init(self):
        self._lock = python_lib_threading_RLock()

    def acquire(self):
        if (self._lock is None):
            self._lock = python_lib_threading_RLock()
        return self._lock.acquire()

    def release(self):
        if (self._lock is not None):
            self._lock.release()

    def hxUnserialize(self,u):
        self.init()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._lock = None
apptimize_util_PythonPlatformLock._hx_class = apptimize_util_PythonPlatformLock
_hx_classes["apptimize.util.PythonPlatformLock"] = apptimize_util_PythonPlatformLock


class apptimize_util_ABTDataLock:
    _hx_class_name = "apptimize.util.ABTDataLock"
    __slots__ = ()
    _hx_statics = ["SYSTEM_DATA_LOCK", "METADATA_LOCK", "CHECK_TIME_LOCK", "INITIALIZATION", "getNewLock"]

    @staticmethod
    def getNewLock(lockName):
        return apptimize_util_PythonPlatformLock()
apptimize_util_ABTDataLock._hx_class = apptimize_util_ABTDataLock
_hx_classes["apptimize.util.ABTDataLock"] = apptimize_util_ABTDataLock


class apptimize_ABTDataStore:
    _hx_class_name = "apptimize.ABTDataStore"
    __slots__ = ("resultLogs", "applicationResultLog", "metaDataCache", "newMdFetcher", "propChangeFetcher", "resultDispatchQueue", "sdkParameters")
    _hx_fields = ["resultLogs", "applicationResultLog", "metaDataCache", "newMdFetcher", "propChangeFetcher", "resultDispatchQueue", "sdkParameters"]
    _hx_methods = ["initialize", "hasMetadata", "_getCurrentEtag", "loadMetaData", "_resetSubmitTimeIfNeeded", "_getMinTimeBetweenPosts", "_submitResultsIfNecessary", "reloadFromDisk", "getRequestlessEnvironment", "getUrlsForMetadata", "onMetadataLoaded", "onMetadataReceived", "overrideMetadata", "getMetaData", "dispatchEnrollmentChangeCallbacks", "makeEnvironment", "writeToDiskIfNeeded", "_saveResultLogs", "addResultLogEntry", "_submitResultLog", "flushTracking", "_flushTrackingInternal", "incrementVariantRunCount", "generateEvent"]
    _hx_statics = ["appKey", "serverGuid", "_instance", "resultsLock", "sharedInstance", "clear", "shutdown", "_getLastCheckTime", "_updateLastCheckTime", "_resetCheckTimeIfNeeded", "_getLastSubmitTime", "_updateLastSubmitTime", "getAppKey", "checkForUpdatedMetaData", "_checkForUpdatedMetadataIfNecessary", "getServerGUID", "shouldDisable"]

    def __init__(self):
        self.propChangeFetcher = None
        self.newMdFetcher = None
        self.metaDataCache = None
        self.applicationResultLog = None
        self.resultLogs = None
        self.sdkParameters = apptimize_models_ABTSdkParameters(None)
        self.resultDispatchQueue = apptimize_util_ABTDispatch("Results Logging Dispatch Queue")
        self.resultDispatchQueue.start()
        self.newMdFetcher = apptimize_api_ABTSecondaryValuesClient()
        self.propChangeFetcher = apptimize_api_ABTSecondaryValuesClient()
        self.metaDataCache = haxe_ds_StringMap()

    def initialize(self):
        self.resultLogs = apptimize_support_persistence_ABTPersistence.loadObject(apptimize_support_persistence_ABTPersistence.kResultLogsKey)
        if (self.resultLogs is None):
            results_cache_size = apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.RESULTS_CACHE_SIZE_KEY)
            if (Type.getClass(results_cache_size) == str):
                results_cache_size = Std.parseInt(results_cache_size)
                if (results_cache_size is None):
                    apptimize_ABTLogger.e("Invalid value specified for results_cache_size, defaulting to 10",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 103, 'className': "apptimize.ABTDataStore", 'methodName': "initialize"}))
                    results_cache_size = 10
            self.resultLogs = apptimize_util_ABTLRUCache(results_cache_size)
        self.applicationResultLog = apptimize_models_results_ABTResultLog(None)

    def hasMetadata(self,appKey):
        hasMD = False
        apptimize_util_ABTDataLock.METADATA_LOCK.acquire()
        try:
            hasMD = (appKey in self.metaDataCache.h)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.METADATA_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.METADATA_LOCK.release()
        return hasMD

    def _getCurrentEtag(self,appKey):
        md = self.getMetaData(appKey)
        if (md is None):
            return None
        return md.getEtag()

    def loadMetaData(self,appKey):
        apptimize_ABTDataStore.appKey = appKey
        self.reloadFromDisk()
        if (not apptimize_ABTDataStore.shouldDisable()):
            if apptimize_ABTDataStore._resetCheckTimeIfNeeded():
                apptimize_api_ABTApiClient.sharedInstance().downloadMetaDataForKey(appKey,self._getCurrentEtag(appKey))

    def _resetSubmitTimeIfNeeded(self,ignoreAppConfig = None):
        if (ignoreAppConfig is None):
            ignoreAppConfig = False
        resetClock = False
        apptimize_util_ABTDataLock.CHECK_TIME_LOCK.acquire()
        try:
            timeout = self._getMinTimeBetweenPosts(ignoreAppConfig)
            currentTime = (Date.now().date.timestamp() * 1000)
            timeSinceLastCheck = (currentTime - apptimize_ABTDataStore._getLastSubmitTime())
            if (timeSinceLastCheck > timeout):
                apptimize_ABTDataStore._updateLastSubmitTime(currentTime)
                resetClock = True
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.CHECK_TIME_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.CHECK_TIME_LOCK.release()
        return resetClock

    def _getMinTimeBetweenPosts(self,ignoreAppConfig = None):
        if (ignoreAppConfig is None):
            ignoreAppConfig = False
        timeout = Std.parseFloat(apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.RESULT_POST_DELAY_MS_KEY))
        minTimeout = self.sdkParameters.minPostFrequencyMs
        if ignoreAppConfig:
            if (minTimeout is None):
                return -1
            else:
                return minTimeout
        else:
            if ((minTimeout is not None) and ((timeout < minTimeout))):
                return minTimeout
            return timeout

    def _submitResultsIfNecessary(self):
        if self._resetSubmitTimeIfNeeded():
            self._flushTrackingInternal()

    def reloadFromDisk(self):
        metadata = apptimize_support_persistence_ABTPersistence.loadObject(apptimize_support_persistence_ABTPersistence.kMetadataKey)
        if (metadata is not None):
            apptimize_ABTLogger.v("Existing metadata loaded from storage, will update if necessary.",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 261, 'className': "apptimize.ABTDataStore", 'methodName': "reloadFromDisk"}))
            self.onMetadataLoaded(metadata)
        else:
            apptimize_ABTLogger.v("No existing metadata found in storage.",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 264, 'className': "apptimize.ABTDataStore", 'methodName': "reloadFromDisk"}))

    def getRequestlessEnvironment(self,md):
        anonUserId = "anon"
        currentUserId = None
        customProperties = None
        params = apptimize_filter_ABTFilterEnvParams(currentUserId,anonUserId,customProperties,md.getAppKey(),apptimize_support_properties_ABTApplicationProperties.sharedInstance())
        env = md.makeEnvironment(params)
        return env

    def getUrlsForMetadata(self,md):
        env = self.getRequestlessEnvironment(md)
        urls = md.extractNeededSecondaryUrls(env)
        return urls

    def onMetadataLoaded(self,md):
        _gthis = self
        urls = self.getUrlsForMetadata(md)
        def _hx_local_0(values,fetched):
            currentUrls = _gthis.getUrlsForMetadata(md)
            if _gthis.newMdFetcher.needNewUrls(urls,currentUrls):
                apptimize_ABTLogger.w("urls changed while fetching values, retrying",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 312, 'className': "apptimize.ABTDataStore", 'methodName': "onMetadataLoaded"}))
                _gthis.onMetadataLoaded(md)
                return
            md.setSecondaryValues(values)
            _gthis.overrideMetadata(md,False,fetched)
        self.newMdFetcher.fetch(urls,md.getSecondaryValues(),_hx_local_0)

    def onMetadataReceived(self,md):
        _gthis = self
        if self.newMdFetcher.fetching():
            apptimize_ABTLogger.e("onMetadataReceived called while fetch already in progress",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 333, 'className': "apptimize.ABTDataStore", 'methodName': "onMetadataReceived"}))
            return
        urls = self.getUrlsForMetadata(md)
        oldValues = None
        oldMD = self.getMetaData(md.getAppKey())
        if (oldMD is not None):
            oldValues = oldMD.getSecondaryValues()
        def _hx_local_0(values,fetched):
            currentUrls = _gthis.getUrlsForMetadata(md)
            if _gthis.newMdFetcher.needNewUrls(urls,currentUrls):
                apptimize_ABTLogger.w("urls changed while fetching values, retrying",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 347, 'className': "apptimize.ABTDataStore", 'methodName': "onMetadataReceived"}))
                _gthis.onMetadataReceived(md)
                return
            md.setSecondaryValues(values)
            _gthis.overrideMetadata(md,True,fetched)
        self.newMdFetcher.fetch(urls,oldValues,_hx_local_0)

    def overrideMetadata(self,md,fromNetwork,secValsChanged):
        oldMd = None
        isKeyValid = True
        mdUpdated = False
        apptimize_util_ABTDataLock.METADATA_LOCK.acquire()
        try:
            isKeyValid = (md.getAppKey() == apptimize_ABTDataStore.getAppKey())
            key = md.getAppKey()
            oldMd = self.metaDataCache.h.get(key,None)
            if isKeyValid:
                if ((oldMd is None) or ((oldMd.getSequenceNumber() < md.getSequenceNumber()))):
                    mdUpdated = True
                if (mdUpdated or secValsChanged):
                    self.metaDataCache.h[key] = md
                    self.sdkParameters = md.extractSdkParameters(self.getRequestlessEnvironment(md))
                    if fromNetwork:
                        apptimize_support_persistence_ABTPersistence.saveObject(apptimize_support_persistence_ABTPersistence.kDisabledVersions,md.getDisabledVersions())
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.METADATA_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.METADATA_LOCK.release()
        if ((mdUpdated and fromNetwork) or secValsChanged):
            self.writeToDiskIfNeeded()
            self.dispatchEnrollmentChangeCallbacks(oldMd,md)
        if mdUpdated:
            apptimize_events_ABTEventManager.dispatchOnMetadataUpdated()
            apptimize_ABTLogger.i((("Updated metadata for app key \"" + HxOverrides.stringOrNull(md.getAppKey())) + "\"."),_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 448, 'className': "apptimize.ABTDataStore", 'methodName': "overrideMetadata"}))
            apptimize_ABTLogger.v(("New metadata:\n" + HxOverrides.stringOrNull(haxe_format_JsonPrinter.print(md.getMetaData(),None,"  "))),_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 450, 'className': "apptimize.ABTDataStore", 'methodName': "overrideMetadata"}))
            if ((oldMd is None) and apptimize_ApptimizeInternal._trySetReady()):
                apptimize_events_ABTEventManager.dispatchOnApptimizeInitialized()
        else:
            apptimize_ABTLogger.i("Existing metadata is up-to-date.",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 458, 'className': "apptimize.ABTDataStore", 'methodName': "overrideMetadata"}))

    def getMetaData(self,appKey):
        if (self.metaDataCache is None):
            return None
        md = None
        apptimize_util_ABTDataLock.METADATA_LOCK.acquire()
        try:
            md = self.metaDataCache.h.get(appKey,None)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.METADATA_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.METADATA_LOCK.release()
        if ((md is not None) and ((md.getAppKey() != appKey))):
            apptimize_ABTLogger.e("Metadata appkey does not match requested key",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 475, 'className': "apptimize.ABTDataStore", 'methodName': "getMetaData"}))
            return None
        return md

    def dispatchEnrollmentChangeCallbacks(self,oldMetadata,newMetadata):
        pass

    def makeEnvironment(self,params):
        metadata = self.getMetaData(params.appkey)
        if (metadata is None):
            return None
        return metadata.makeEnvironment(params)

    def writeToDiskIfNeeded(self):
        md = self.getMetaData(apptimize_ABTDataStore.getAppKey())
        if (md is not None):
            apptimize_support_persistence_ABTPersistence.saveObject(apptimize_support_persistence_ABTPersistence.kMetadataKey,md,None,True)

    def _saveResultLogs(self):
        apptimize_support_persistence_ABTPersistence.saveObject(apptimize_support_persistence_ABTPersistence.kResultLogsKey,self.resultLogs,None,True)

    def addResultLogEntry(self,env,entry):
        logKey = env.getUniqueUserID()
        apptimize_ABTDataStore.resultsLock.acquire()
        try:
            resultLog = self.resultLogs.getValue(logKey)
            if (resultLog is None):
                resultLog = apptimize_models_results_ABTResultLog(env)
                self.resultLogs.insert(logKey,resultLog,self._submitResultLog,self.resultDispatchQueue)
            resultLog.logEntry(entry)
            if (resultLog.entryCount() > apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.MAXIMUM_RESULT_ENTRIES_KEY)):
                self.resultLogs.remove(logKey,self._submitResultLog,self.resultDispatchQueue)
            self._saveResultLogs()
            self._submitResultsIfNecessary()
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_ABTDataStore.resultsLock.release()
            raise haxe_Exception.thrown(e)
        apptimize_ABTDataStore.resultsLock.release()

    def _submitResultLog(self,log):
        if apptimize_ABTDataStore.shouldDisable():
            return
        apptimize_api_ABTApiClient.sharedInstance().postResultsForKey(log.getAppKey(),log)
        self._saveResultLogs()

    def flushTracking(self):
        if self._resetSubmitTimeIfNeeded(True):
            self._flushTrackingInternal()

    def _flushTrackingInternal(self):
        apptimize_ABTLogger.v("Posting results...",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 734, 'className': "apptimize.ABTDataStore", 'methodName': "_flushTrackingInternal"}))
        apptimize_ABTDataStore.resultsLock.acquire()
        try:
            self.resultLogs.clear(self._submitResultLog,self.resultDispatchQueue)
            self._saveResultLogs()
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_ABTDataStore.resultsLock.release()
            raise haxe_Exception.thrown(e)
        apptimize_ABTDataStore.resultsLock.release()

    def incrementVariantRunCount(self,params,variant):
        if (Type.getClass(variant) == apptimize_models_ABTHotfixVariant):
            return
        variantStickyString = ((("v" + Std.string(variant.getVariantID())) + "_") + Std.string(variant.getCycle()))
        experimentStickyString = ((("e" + Std.string(variant.getExperimentID())) + "_") + Std.string(variant.getCycle()))
        phase = variant.getPhase()
        isFirstParticipation = False
        env = self.makeEnvironment(params)
        variantShownEntry = apptimize_models_results_ABTResultEntryVariantShown(env,variant.getVariantID(),variant.getCycle(),phase)
        apptimize_ABTLogger.v((("Incrementing variant run count for variant ID \"" + Std.string(variant.getVariantID())) + "\"."),_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 769, 'className': "apptimize.ABTDataStore", 'methodName': "incrementVariantRunCount"}))
        variantInfo = apptimize_VariantInfo.initWithVariant(variant,env.userID,env.anonID)
        apptimize_events_ABTEventManager.dispatchOnParticipatedInExperiment(variantInfo,isFirstParticipation)
        self.addResultLogEntry(env,variantShownEntry)

    def generateEvent(self,eventName,eventSource,eventAttributes,params):
        if ((not apptimize_Apptimize._isInitialized()) or ((apptimize_ABTDataStore.sharedInstance().getMetaData(params.appkey) is None))):
            apptimize_ABTLogger.w((("Event \"" + ("null" if eventName is None else eventName)) + "\" will not be tracked until Apptimize.setup() is called and MetaData available."),_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 780, 'className': "apptimize.ABTDataStore", 'methodName': "generateEvent"}))
            return
        env = self.makeEnvironment(params)
        eventEntry = apptimize_models_results_ABTResultEntryEvent(env,eventName,eventSource,eventAttributes)
        logString = (("Event \"" + ("null" if eventName is None else eventName)) + "\"")
        if (eventAttributes is not None):
            logString = ((("null" if logString is None else logString) + " with value ") + Std.string(eventAttributes.h.get(apptimize_ApptimizeInternal.kABTValueEventKey,None)))
        logString = (("null" if logString is None else logString) + " tracked.")
        apptimize_ABTLogger.v(logString,_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 794, 'className': "apptimize.ABTDataStore", 'methodName': "generateEvent"}))
        self.addResultLogEntry(env,eventEntry)
    appKey = None
    serverGuid = None
    _instance = None

    @staticmethod
    def sharedInstance():
        if (apptimize_ABTDataStore._instance is None):
            apptimize_ABTDataStore._instance = apptimize_ABTDataStore()
        return apptimize_ABTDataStore._instance

    @staticmethod
    def clear():
        apptimize_support_persistence_ABTPersistence.clear()
        apptimize_ABTDataStore._instance = None

    @staticmethod
    def shutdown():
        apptimize_ABTDataStore._instance = None
        apptimize_ABTDataStore.appKey = None
        apptimize_ABTDataStore.serverGuid = None

    @staticmethod
    def _getLastCheckTime():
        lastCheckTime = apptimize_support_persistence_ABTPersistence.loadString(apptimize_support_persistence_ABTPersistence.kMetadataLastCheckTimeKey)
        if (lastCheckTime is not None):
            return Std.parseFloat(lastCheckTime)
        return -10000.0

    @staticmethod
    def _updateLastCheckTime(checkTime):
        apptimize_support_persistence_ABTPersistence.saveString(apptimize_support_persistence_ABTPersistence.kMetadataLastCheckTimeKey,Std.string(checkTime))

    @staticmethod
    def _resetCheckTimeIfNeeded():
        resetClock = False
        apptimize_util_ABTDataLock.CHECK_TIME_LOCK.acquire()
        try:
            timeout = Std.parseFloat(apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.METADATA_POLLING_INTERVAL_MS_KEY))
            currentTime = (Date.now().date.timestamp() * 1000)
            timeSinceLastCheck = (currentTime - apptimize_ABTDataStore._getLastCheckTime())
            if (timeSinceLastCheck > timeout):
                apptimize_ABTDataStore._updateLastCheckTime(currentTime)
                resetClock = True
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.CHECK_TIME_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.CHECK_TIME_LOCK.release()
        return resetClock

    @staticmethod
    def _getLastSubmitTime():
        lastSubmitCheckTime = apptimize_support_persistence_ABTPersistence.loadString(apptimize_support_persistence_ABTPersistence.kResultLastSubmitTimeKey)
        if (lastSubmitCheckTime is not None):
            return Std.parseFloat(lastSubmitCheckTime)
        return -10000.0

    @staticmethod
    def _updateLastSubmitTime(checkTime):
        apptimize_support_persistence_ABTPersistence.saveString(apptimize_support_persistence_ABTPersistence.kResultLastSubmitTimeKey,Std.string(checkTime))

    @staticmethod
    def getAppKey():
        return apptimize_ABTDataStore.appKey

    @staticmethod
    def checkForUpdatedMetaData(checkImmediately = None):
        if (checkImmediately is None):
            checkImmediately = False
        if apptimize_ABTDataStore.shouldDisable():
            apptimize_ABTLogger.w("This SDK version disabled; not checking for updated metadata",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 223, 'className': "apptimize.ABTDataStore", 'methodName': "checkForUpdatedMetaData"}))
            return
        apptimize_ABTLogger.v("Checking for updated metadata...",_hx_AnonObject({'fileName': "src/apptimize/ABTDataStore.hx", 'lineNumber': 226, 'className': "apptimize.ABTDataStore", 'methodName': "checkForUpdatedMetaData"}))
        if (apptimize_Apptimize._isInitialized() and ((apptimize_ABTDataStore._resetCheckTimeIfNeeded() or checkImmediately))):
            apptimize_api_ABTApiClient.sharedInstance().downloadMetaDataForKey(apptimize_ABTDataStore.getAppKey(),apptimize_ABTDataStore.sharedInstance()._getCurrentEtag(apptimize_ABTDataStore.getAppKey()))

    @staticmethod
    def _checkForUpdatedMetadataIfNecessary():
        if ((not apptimize_api_ABTMetadataPoller.isPolling()) and ((apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.METADATA_POLLING_INTERVAL_MS_KEY) >= 0))):
            apptimize_ABTDataStore.checkForUpdatedMetaData()
        apptimize_ABTDataStore.sharedInstance()._submitResultsIfNecessary()

    @staticmethod
    def getServerGUID():
        if (apptimize_ABTDataStore.serverGuid is None):
            apptimize_ABTDataStore.serverGuid = apptimize_api_ABTUserGuid.generateUserGuid()
        return apptimize_ABTDataStore.serverGuid

    @staticmethod
    def shouldDisable():
        disabledVersions = apptimize_support_persistence_ABTPersistence.loadObject(apptimize_support_persistence_ABTPersistence.kDisabledVersions)
        if (disabledVersions is None):
            return False
        if (python_internal_ArrayImpl.indexOf(disabledVersions,apptimize_Apptimize.getApptimizeSDKVersion(),None) > -1):
            return True
        return False

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.resultLogs = None
        _hx_o.applicationResultLog = None
        _hx_o.metaDataCache = None
        _hx_o.newMdFetcher = None
        _hx_o.propChangeFetcher = None
        _hx_o.resultDispatchQueue = None
        _hx_o.sdkParameters = None
apptimize_ABTDataStore._hx_class = apptimize_ABTDataStore
_hx_classes["apptimize.ABTDataStore"] = apptimize_ABTDataStore


class apptimize_ABTLogger:
    _hx_class_name = "apptimize.ABTLogger"
    __slots__ = ()
    _hx_statics = ["LOG_LEVEL_VERBOSE", "LOG_LEVEL_DEBUG", "LOG_LEVEL_INFO", "LOG_LEVEL_WARN", "LOG_LEVEL_ERROR", "LOG_LEVEL_NONE", "logLevel", "useTraceForLogging", "logLevelFromString", "setLogLevel", "c", "e", "w", "i", "d", "v", "log_out", "redirectTraceStatements", "traceInternal", "trace"]

    @staticmethod
    def logLevelFromString(logLevel):
        level = logLevel.upper()
        if (level == "LOG_LEVEL_VERBOSE"):
            return apptimize_ABTLogger.LOG_LEVEL_VERBOSE
        if (level == "LOG_LEVEL_DEBUG"):
            return apptimize_ABTLogger.LOG_LEVEL_DEBUG
        if (level == "LOG_LEVEL_INFO"):
            return apptimize_ABTLogger.LOG_LEVEL_INFO
        if (level == "LOG_LEVEL_WARN"):
            return apptimize_ABTLogger.LOG_LEVEL_WARN
        if (level == "LOG_LEVEL_ERROR"):
            return apptimize_ABTLogger.LOG_LEVEL_ERROR
        if (level == "LOG_LEVEL_NONE"):
            return apptimize_ABTLogger.LOG_LEVEL_NONE
        return apptimize_ABTLogger.LOG_LEVEL_NONE

    @staticmethod
    def setLogLevel(level):
        apptimize_ABTLogger.logLevel = level

    @staticmethod
    def c(msg,infos = None):
        apptimize_ABTLogger.log_out(msg,infos)
        apptimize_util_ABTException.throwException(msg)

    @staticmethod
    def e(msg,infos = None):
        if (apptimize_ABTLogger.logLevel <= apptimize_ABTLogger.LOG_LEVEL_ERROR):
            apptimize_ABTLogger.log_out(msg,infos)

    @staticmethod
    def w(msg,infos = None):
        if (apptimize_ABTLogger.logLevel <= apptimize_ABTLogger.LOG_LEVEL_WARN):
            apptimize_ABTLogger.log_out(msg,infos)

    @staticmethod
    def i(msg,infos = None):
        if (apptimize_ABTLogger.logLevel <= apptimize_ABTLogger.LOG_LEVEL_INFO):
            apptimize_ABTLogger.log_out(msg,infos)

    @staticmethod
    def d(msg,infos = None):
        if (apptimize_ABTLogger.logLevel <= apptimize_ABTLogger.LOG_LEVEL_DEBUG):
            apptimize_ABTLogger.log_out(msg,infos)

    @staticmethod
    def v(msg,infos = None):
        if (apptimize_ABTLogger.logLevel <= apptimize_ABTLogger.LOG_LEVEL_VERBOSE):
            apptimize_ABTLogger.log_out(msg,infos)

    @staticmethod
    def log_out(msg,infos):
        if (apptimize_ABTLogger.useTraceForLogging and ((haxe_Log.trace != apptimize_ABTLogger.trace))):
            haxe_Log.trace(msg,infos)
            return
        apptimize_ABTLogger.traceInternal(("Apptimize: " + ("null" if msg is None else msg)),infos)

    @staticmethod
    def redirectTraceStatements():
        haxe_Log.trace = apptimize_ABTLogger.trace

    @staticmethod
    def traceInternal(_hx_str,infos = None):
        str1 = Std.string(_hx_str)
        python_Lib.printString((("" + ("null" if str1 is None else str1)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))

    @staticmethod
    def trace(val,infos = None):
        _hx_str = Std.string(val)
        apptimize_ABTLogger.v(_hx_str,infos)
apptimize_ABTLogger._hx_class = apptimize_ABTLogger
_hx_classes["apptimize.ABTLogger"] = apptimize_ABTLogger


class apptimize_ApptimizeInternal:
    _hx_class_name = "apptimize.ApptimizeInternal"
    __slots__ = ()
    _hx_statics = ["kABTEventSourceApptimize", "kABTValueEventKey", "_state", "_isInitialized", "setState", "_trySetReady", "_setup", "shutdown", "generateTrackEvent", "_getCodeBlockMethod", "_getVariants", "_getAlterations"]

    @staticmethod
    def _isInitialized():
        result = False
        apptimize_util_ABTDataLock.INITIALIZATION.acquire()
        try:
            result = ((apptimize_ApptimizeInternal._state == 2) or ((apptimize_ApptimizeInternal._state == 3)))
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.INITIALIZATION.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.INITIALIZATION.release()
        return result

    @staticmethod
    def setState(state):
        apptimize_util_ABTDataLock.INITIALIZATION.acquire()
        try:
            apptimize_ApptimizeInternal._state = state
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.INITIALIZATION.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.INITIALIZATION.release()

    @staticmethod
    def _trySetReady():
        result = False
        apptimize_util_ABTDataLock.INITIALIZATION.acquire()
        try:
            if (apptimize_ApptimizeInternal._state == 2):
                result = True
                apptimize_ApptimizeInternal._state = 3
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.INITIALIZATION.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.INITIALIZATION.release()
        return result

    @staticmethod
    def _setup(appKey,configAttributes,setupComplete):
        canInitialize = True
        apptimize_util_ABTDataLock.INITIALIZATION.acquire()
        try:
            if (apptimize_ApptimizeInternal._state != 0):
                apptimize_ABTLogger.w("Apptimize setup has already been called.",_hx_AnonObject({'fileName': "src/apptimize/ApptimizeInternal.hx", 'lineNumber': 68, 'className': "apptimize.ApptimizeInternal", 'methodName': "_setup"}))
                canInitialize = False
            else:
                apptimize_ApptimizeInternal._state = 1
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.INITIALIZATION.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.INITIALIZATION.release()
        if (canInitialize == False):
            return
        apptimize_ABTLogger.redirectTraceStatements()
        configProps = apptimize_support_properties_ABTConfigProperties.sharedInstance()
        if (configAttributes is not None):
            configProps.setProperties(apptimize_util_ABTUtilDictionary.nativeObjectToStringMap(configAttributes))
        if configProps.isPropertyAvailable(apptimize_support_properties_ABTConfigProperties.LOG_LEVEL_KEY):
            logLevel = configProps.valueForProperty(apptimize_support_properties_ABTConfigProperties.LOG_LEVEL_KEY)
            apptimize_ABTLogger.setLogLevel(apptimize_ABTLogger.logLevelFromString(logLevel))
        if (configProps.isPropertyAvailable(apptimize_support_properties_ABTConfigProperties.APPTIMIZE_ENVIRONMENT_KEY) or configProps.isPropertyAvailable(apptimize_support_properties_ABTConfigProperties.APPTIMIZE_REGION_KEY)):
            environment = configProps.valueForProperty(apptimize_support_properties_ABTConfigProperties.APPTIMIZE_ENVIRONMENT_KEY)
            if (environment is None):
                environment = "prod"
            region = configProps.valueForProperty(apptimize_support_properties_ABTConfigProperties.APPTIMIZE_REGION_KEY)
            if (region is None):
                region = "default"
            region1 = region
            _hx_local_0 = len(region1)
            if (_hx_local_0 == 4):
                if (region1 == "eucs"):
                    environment1 = environment
                    _hx_local_1 = len(environment1)
                    if (_hx_local_1 == 5):
                        if (environment1 == "local"):
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY,"https://local.apptimize.co/api/metadata/v4/")
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://local.apptimize.co")
                        else:
                            pass
                    elif (_hx_local_1 == 4):
                        if (environment1 == "prod"):
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_LL_KEY,"https://md-ll.apptimize.eu/api/metadata/v4/")
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_HL_KEY,"https://md-hl.apptimize.eu/api/metadata/v4/")
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://mapi.apptimize.eu")
                        else:
                            pass
                    elif (_hx_local_1 == 7):
                        if (environment1 == "staging"):
                            if (region != "default"):
                                apptimize_ABTLogger.v((("Apptimize region '" + ("null" if region is None else region)) + "' does not have a staging environment. Falling back to default region."),_hx_AnonObject({'fileName': "src/apptimize/ApptimizeInternal.hx", 'lineNumber': 109, 'className': "apptimize.ApptimizeInternal", 'methodName': "_setup"}))
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY,"https://staging-md.apptimize.co/api/metadata/v4/")
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://staging-mapi.apptimize.co")
                        else:
                            pass
                    else:
                        pass
                else:
                    environment1 = environment
                    _hx_local_2 = len(environment1)
                    if (_hx_local_2 == 5):
                        if (environment1 == "local"):
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY,"https://local.apptimize.co/api/metadata/v4/")
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://local.apptimize.co")
                        else:
                            pass
                    elif (_hx_local_2 == 7):
                        if (environment1 == "staging"):
                            if (region != "default"):
                                apptimize_ABTLogger.v((("Apptimize region '" + ("null" if region is None else region)) + "' does not have a staging environment. Falling back to default region."),_hx_AnonObject({'fileName': "src/apptimize/ApptimizeInternal.hx", 'lineNumber': 109, 'className': "apptimize.ApptimizeInternal", 'methodName': "_setup"}))
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY,"https://staging-md.apptimize.co/api/metadata/v4/")
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://staging-mapi.apptimize.co")
                        else:
                            pass
                    else:
                        pass
            elif (_hx_local_0 == 3):
                if (region1 == "gcp"):
                    environment1 = environment
                    _hx_local_3 = len(environment1)
                    if (_hx_local_3 == 5):
                        if (environment1 == "local"):
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY,"https://local.apptimize.co/api/metadata/v4/")
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://local.apptimize.co")
                        else:
                            pass
                    elif (_hx_local_3 == 7):
                        if (environment1 == "staging"):
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY,"https://gcp-stag-md.apptimize.co/api/metadata/v4/")
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://gcp-stag-mapi.apptimize.co")
                        else:
                            pass
                    else:
                        pass
                else:
                    environment1 = environment
                    _hx_local_4 = len(environment1)
                    if (_hx_local_4 == 5):
                        if (environment1 == "local"):
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY,"https://local.apptimize.co/api/metadata/v4/")
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://local.apptimize.co")
                        else:
                            pass
                    elif (_hx_local_4 == 7):
                        if (environment1 == "staging"):
                            if (region != "default"):
                                apptimize_ABTLogger.v((("Apptimize region '" + ("null" if region is None else region)) + "' does not have a staging environment. Falling back to default region."),_hx_AnonObject({'fileName': "src/apptimize/ApptimizeInternal.hx", 'lineNumber': 109, 'className': "apptimize.ApptimizeInternal", 'methodName': "_setup"}))
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY,"https://staging-md.apptimize.co/api/metadata/v4/")
                            configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://staging-mapi.apptimize.co")
                        else:
                            pass
                    else:
                        pass
            else:
                environment1 = environment
                _hx_local_5 = len(environment1)
                if (_hx_local_5 == 5):
                    if (environment1 == "local"):
                        configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY,"https://local.apptimize.co/api/metadata/v4/")
                        configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://local.apptimize.co")
                    else:
                        pass
                elif (_hx_local_5 == 7):
                    if (environment1 == "staging"):
                        if (region != "default"):
                            apptimize_ABTLogger.v((("Apptimize region '" + ("null" if region is None else region)) + "' does not have a staging environment. Falling back to default region."),_hx_AnonObject({'fileName': "src/apptimize/ApptimizeInternal.hx", 'lineNumber': 109, 'className': "apptimize.ApptimizeInternal", 'methodName': "_setup"}))
                        configProps.setProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY,"https://staging-md.apptimize.co/api/metadata/v4/")
                        configProps.setProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY,"https://staging-mapi.apptimize.co")
                    else:
                        pass
                else:
                    pass
        if (appKey is not None):
            apptimize_ABTLogger.v((("Initializing Apptimize with app key: \"" + ("null" if appKey is None else appKey)) + "\"."),_hx_AnonObject({'fileName': "src/apptimize/ApptimizeInternal.hx", 'lineNumber': 120, 'className': "apptimize.ApptimizeInternal", 'methodName': "_setup"}))
        apptimize_ABTDataStore.sharedInstance().initialize()
        apptimize_support_initialize_ABTPlatformInitialize.initialize()
        threadCount = 8
        if configProps.isPropertyAvailable(apptimize_support_properties_ABTConfigProperties.RESULT_POST_THREAD_POOL_SIZE_KEY):
            threadCount = configProps.valueForProperty(apptimize_support_properties_ABTConfigProperties.RESULT_POST_THREAD_POOL_SIZE_KEY)
        def _hx_local_6():
            apptimize_api_ABTApiResultsPost.loadPendingLogs()
            setupComplete()
            apptimize_api_ABTApiResultsPost.startDispatching(threadCount)
        apptimize_support_persistence_ABTPersistence.loadFromHighLatency(_hx_local_6)

    @staticmethod
    def shutdown():
        apptimize_util_ABTDataLock.INITIALIZATION.acquire()
        try:
            if ((apptimize_ApptimizeInternal._state == 2) or ((apptimize_ApptimizeInternal._state == 3))):
                apptimize_api_ABTApiResultsPost.savePendingLogs()
                apptimize_support_persistence_ABTPersistence.saveToHighLatency()
                apptimize_support_initialize_ABTPlatformInitialize.shutdownPlatform()
                apptimize_ABTDataStore.shutdown()
                apptimize_support_persistence_ABTPersistence.shutdown()
                apptimize_ApptimizeInternal._state = 0
                apptimize_ABTLogger.i("Apptimize has shutdown",_hx_AnonObject({'fileName': "src/apptimize/ApptimizeInternal.hx", 'lineNumber': 151, 'className': "apptimize.ApptimizeInternal", 'methodName': "shutdown"}))
            else:
                apptimize_ABTLogger.w("Apptimize is not initialized. Unable to shutdown().",_hx_AnonObject({'fileName': "src/apptimize/ApptimizeInternal.hx", 'lineNumber': 153, 'className': "apptimize.ApptimizeInternal", 'methodName': "shutdown"}))
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.INITIALIZATION.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.INITIALIZATION.release()

    @staticmethod
    def generateTrackEvent(envParams,eventName,eventValue):
        value = None
        if (eventValue is not None):
            _g = haxe_ds_StringMap()
            _g.h[apptimize_ApptimizeInternal.kABTValueEventKey] = eventValue
            value = _g
        apptimize_ABTDataStore.sharedInstance().generateEvent(eventName,apptimize_ApptimizeInternal.kABTEventSourceApptimize,value,envParams)

    @staticmethod
    def _getCodeBlockMethod(envParams,codeBlockVariableName):
        cbVarName = codeBlockVariableName
        if ((cbVarName is None) or ((cbVarName == ""))):
            apptimize_ABTLogger.w("Attempting to runCodeBlock() without specifying a code block name! Returning baseline original variant.",_hx_AnonObject({'fileName': "src/apptimize/ApptimizeInternal.hx", 'lineNumber': 170, 'className': "apptimize.ApptimizeInternal", 'methodName': "_getCodeBlockMethod"}))
        else:
            _g = 0
            _g1 = apptimize_ApptimizeInternal._getAlterations(envParams)
            while (_g < len(_g1)):
                alteration = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                if ((alteration is not None) and ((Type.getClass(alteration) == apptimize_models_ABTBlockAlteration))):
                    block = alteration
                    variant = block.getVariant()
                    if (variant.getCodeBlockName() != cbVarName):
                        continue
                    apptimize_ABTDataStore.sharedInstance().incrementVariantRunCount(envParams,block.getVariant())
                    return block.methodName
            apptimize_ABTLogger.w((("Not participating in any code block experiments with name \"" + ("null" if codeBlockVariableName is None else codeBlockVariableName)) + "\". Returning baseline original variant."),_hx_AnonObject({'fileName': "src/apptimize/ApptimizeInternal.hx", 'lineNumber': 185, 'className': "apptimize.ApptimizeInternal", 'methodName': "_getCodeBlockMethod"}))
        return "baseline"

    @staticmethod
    def _getVariants(envParams):
        apptimize_ABTDataStore._checkForUpdatedMetadataIfNecessary()
        alterations = apptimize_ApptimizeInternal._getAlterations(envParams)
        variants = haxe_ds_IntMap()
        _g = 0
        while (_g < len(alterations)):
            alteration = (alterations[_g] if _g >= 0 and _g < len(alterations) else None)
            _g = (_g + 1)
            variant = alteration.getVariant()
            if ((Type.getClass(variant) != apptimize_models_ABTHotfixVariant) and (not (variant.getVariantID() in variants.h))):
                variants.set(variant.getVariantID(),variant)
        return Lambda.array(variants)

    @staticmethod
    def _getAlterations(envParams):
        alterations = []
        metadata = apptimize_ABTDataStore.sharedInstance().getMetaData(envParams.appkey)
        if (metadata is not None):
            alterations = metadata.selectAlterationsIntoArray(metadata.makeEnvironment(envParams))
        return alterations
apptimize_ApptimizeInternal._hx_class = apptimize_ApptimizeInternal
_hx_classes["apptimize.ApptimizeInternal"] = apptimize_ApptimizeInternal

class apptimize_ApptimizeExperimentType(Enum):
    __slots__ = ()
    _hx_class_name = "apptimize.ApptimizeExperimentType"
    _hx_constructs = ["CodeBlock", "FeatureFlag", "DynamicVariables", "Visual", "Unknown", "FeatureVariables"]
apptimize_ApptimizeExperimentType.CodeBlock = apptimize_ApptimizeExperimentType("CodeBlock", 0, ())
apptimize_ApptimizeExperimentType.FeatureFlag = apptimize_ApptimizeExperimentType("FeatureFlag", 1, ())
apptimize_ApptimizeExperimentType.DynamicVariables = apptimize_ApptimizeExperimentType("DynamicVariables", 2, ())
apptimize_ApptimizeExperimentType.Visual = apptimize_ApptimizeExperimentType("Visual", 3, ())
apptimize_ApptimizeExperimentType.Unknown = apptimize_ApptimizeExperimentType("Unknown", 4, ())
apptimize_ApptimizeExperimentType.FeatureVariables = apptimize_ApptimizeExperimentType("FeatureVariables", 5, ())
apptimize_ApptimizeExperimentType._hx_class = apptimize_ApptimizeExperimentType
_hx_classes["apptimize.ApptimizeExperimentType"] = apptimize_ApptimizeExperimentType


class apptimize_api_ABTApiClient:
    _hx_class_name = "apptimize.api.ABTApiClient"
    __slots__ = ()
    _hx_methods = ["downloadMetaDataForKey", "postResultsForKey"]
    _hx_statics = ["_instance", "sharedInstance"]

    def __init__(self):
        pass

    def downloadMetaDataForKey(self,appKey,etag):
        def _hx_local_0(json,etag):
            md = apptimize_models_ABTMetadata.loadFromString(json)
            md.setEtag(etag)
            apptimize_ABTDataStore.sharedInstance().onMetadataReceived(md)
        def _hx_local_1(error):
            apptimize_ABTLogger.e(("Failed to download metadata with error: " + ("null" if error is None else error)),_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiClient.hx", 'lineNumber': 24, 'className': "apptimize.api.ABTApiClient", 'methodName': "downloadMetaDataForKey"}))
        mdRequest = apptimize_api_ABTApiMetadataRequest(self,appKey,etag,_hx_local_0,_hx_local_1)

    def postResultsForKey(self,appKey,log):
        def _hx_local_0(response):
            pass
        def _hx_local_1(response):
            pass
        resultsRequest = apptimize_api_ABTApiResultsPost(self,appKey,log,_hx_local_0,_hx_local_1)
        apptimize_api_ABTApiResultsPost.pushRequest(resultsRequest)
    _instance = None

    @staticmethod
    def sharedInstance():
        if (apptimize_api_ABTApiClient._instance is None):
            apptimize_api_ABTApiClient._instance = apptimize_api_ABTApiClient()
        return apptimize_api_ABTApiClient._instance

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_api_ABTApiClient._hx_class = apptimize_api_ABTApiClient
_hx_classes["apptimize.api.ABTApiClient"] = apptimize_api_ABTApiClient


class apptimize_api_ABTApiMetadataRequest:
    _hx_class_name = "apptimize.api.ABTApiMetadataRequest"
    __slots__ = ("apiClient", "appKey", "successCallback", "failureCallback")
    _hx_fields = ["apiClient", "appKey", "successCallback", "failureCallback"]
    _hx_methods = ["_apiSuccess", "_getMetadataUrl", "_headersForRequest"]

    def __init__(self,client,applicationKey,etag,success,failure):
        self.failureCallback = None
        self.successCallback = None
        self.appKey = None
        self.apiClient = None
        _gthis = self
        self.apiClient = client
        self.appKey = applicationKey
        self.successCallback = success
        self.failureCallback = failure
        url = self._getMetadataUrl()
        url = (("null" if url is None else url) + ("null" if applicationKey is None else applicationKey))
        apptimize_ABTLogger.v(("Checking for new metadata from url: " + ("null" if url is None else url)),_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiMetadataRequest.hx", 'lineNumber': 27, 'className': "apptimize.api.ABTApiMetadataRequest", 'methodName': "new"}))
        def _hx_local_1(response):
            _gthis._apiSuccess(response)
        def _hx_local_2(response):
            _gthis.failureCallback(response.text)
        apptimize_http_ABTHttpRequest.get(url,self._headersForRequest(etag),_hx_local_1,_hx_local_2)

    def _apiSuccess(self,response):
        if (response.responseCode == 304):
            apptimize_ABTLogger.v("Got HTTP response 304, metadata not updated.",_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiMetadataRequest.hx", 'lineNumber': 38, 'className': "apptimize.api.ABTApiMetadataRequest", 'methodName': "_apiSuccess"}))
            return
        json = apptimize_api_ABTMetadataProcessor.jsonFromMetadataDownload(response.bytes)
        if (json is not None):
            apptimize_ABTLogger.v("Request for metadata completed successfully.",_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiMetadataRequest.hx", 'lineNumber': 45, 'className': "apptimize.api.ABTApiMetadataRequest", 'methodName': "_apiSuccess"}))
            self.successCallback(json,response.etag)
        else:
            errorString = "Failed to download metadata with error: response was empty."
            apptimize_ABTLogger.w(errorString,_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiMetadataRequest.hx", 'lineNumber': 49, 'className': "apptimize.api.ABTApiMetadataRequest", 'methodName': "_apiSuccess"}))
            self.failureCallback(errorString)

    def _getMetadataUrl(self):
        metadataUrl = apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY)
        if (metadataUrl is not None):
            return metadataUrl
        elif apptimize_ABTDataStore.sharedInstance().hasMetadata(self.appKey):
            return apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_HL_KEY)
        else:
            return apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.META_DATA_URL_LL_KEY)

    def _headersForRequest(self,etag):
        if (etag is not None):
            _g = haxe_ds_StringMap()
            _g.h["ETag"] = etag
            _g.h["If-None-Match"] = etag
            return _g
        else:
            return None

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.apiClient = None
        _hx_o.appKey = None
        _hx_o.successCallback = None
        _hx_o.failureCallback = None
apptimize_api_ABTApiMetadataRequest._hx_class = apptimize_api_ABTApiMetadataRequest
_hx_classes["apptimize.api.ABTApiMetadataRequest"] = apptimize_api_ABTApiMetadataRequest


class hx_concurrent_atomic__AtomicInt_AtomicIntImpl:
    _hx_class_name = "hx.concurrent.atomic._AtomicInt.AtomicIntImpl"
    __slots__ = ("lock", "_value")
    _hx_fields = ["lock", "_value"]
    _hx_methods = ["get_value", "set_value", "getAndIncrement", "incrementAndGet"]

    def __init__(self,initialValue = None):
        if (initialValue is None):
            initialValue = 0
        self.lock = hx_concurrent_lock_RLock()
        self._value = initialValue

    def get_value(self):
        self.lock.acquire()
        result = self._value
        self.lock.release()
        return result

    def set_value(self,val):
        self.lock.acquire()
        self._value = val
        self.lock.release()
        return val

    def getAndIncrement(self,amount = None):
        if (amount is None):
            amount = 1
        self.lock.acquire()
        old = self._value
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._value
        _hx_local_0._value = (_hx_local_1 + amount)
        _hx_local_0._value
        self.lock.release()
        return old

    def incrementAndGet(self,amount = None):
        if (amount is None):
            amount = 1
        self.lock.acquire()
        result = self
        def _hx_local_1():
            result._value = (result._value + amount)
            return result._value
        result1 = _hx_local_1()
        self.lock.release()
        return result1

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.lock = None
        _hx_o._value = None
hx_concurrent_atomic__AtomicInt_AtomicIntImpl._hx_class = hx_concurrent_atomic__AtomicInt_AtomicIntImpl
_hx_classes["hx.concurrent.atomic._AtomicInt.AtomicIntImpl"] = hx_concurrent_atomic__AtomicInt_AtomicIntImpl


class haxe_IMap:
    _hx_class_name = "haxe.IMap"
    __slots__ = ()
haxe_IMap._hx_class = haxe_IMap
_hx_classes["haxe.IMap"] = haxe_IMap


class haxe_ds_StringMap:
    _hx_class_name = "haxe.ds.StringMap"
    __slots__ = ("h",)
    _hx_fields = ["h"]
    _hx_methods = ["remove", "keys"]
    _hx_interfaces = [haxe_IMap]

    def __init__(self):
        self.h = dict()

    def remove(self,key):
        has = (key in self.h)
        if has:
            del self.h[key]
        return has

    def keys(self):
        return python_HaxeIterator(iter(self.h.keys()))

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.h = None
haxe_ds_StringMap._hx_class = haxe_ds_StringMap
_hx_classes["haxe.ds.StringMap"] = haxe_ds_StringMap


class hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedList_Impl_:
    _hx_class_name = "hx.concurrent.collection._SynchronizedLinkedList.SynchronizedLinkedList_Impl_"
    __slots__ = ()
    _hx_statics = ["_new"]

    @staticmethod
    def _new(initialValues = None):
        this1 = hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedListImpl()
        if (initialValues is not None):
            this1.addAll(initialValues)
        return this1
hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedList_Impl_._hx_class = hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedList_Impl_
_hx_classes["hx.concurrent.collection._SynchronizedLinkedList.SynchronizedLinkedList_Impl_"] = hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedList_Impl_


class hx_concurrent_collection_Collection:
    _hx_class_name = "hx.concurrent.collection.Collection"
    __slots__ = ()
    _hx_methods = ["iterator"]
hx_concurrent_collection_Collection._hx_class = hx_concurrent_collection_Collection
_hx_classes["hx.concurrent.collection.Collection"] = hx_concurrent_collection_Collection


class hx_concurrent_collection_OrderedCollection:
    _hx_class_name = "hx.concurrent.collection.OrderedCollection"
    __slots__ = ()
    _hx_interfaces = [hx_concurrent_collection_Collection]
hx_concurrent_collection_OrderedCollection._hx_class = hx_concurrent_collection_OrderedCollection
_hx_classes["hx.concurrent.collection.OrderedCollection"] = hx_concurrent_collection_OrderedCollection


class hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedListImpl:
    _hx_class_name = "hx.concurrent.collection._SynchronizedLinkedList.SynchronizedLinkedListImpl"
    __slots__ = ("_items", "_sync")
    _hx_fields = ["_items", "_sync"]
    _hx_methods = ["add", "addAll", "clear", "remove", "indexOf", "iterator", "toArray"]
    _hx_interfaces = [hx_concurrent_collection_OrderedCollection]

    def __init__(self):
        self._sync = hx_concurrent_lock_RLock()
        self._items = haxe_ds_List()

    def add(self,item):
        _gthis = self
        def _hx_local_0():
            _gthis._items.add(item)
        self._sync.execute(_hx_local_0)

    def addAll(self,coll):
        _gthis = self
        def _hx_local_1():
            _g = coll
            tmp = _g.index
            if (tmp == 0):
                coll1 = _g.params[0]
                i = coll1.iterator()
                while i.hasNext():
                    i1 = i.next()
                    _gthis._items.add(i1)
            elif (tmp == 1):
                arr = _g.params[0]
                _g1 = 0
                while (_g1 < len(arr)):
                    i = (arr[_g1] if _g1 >= 0 and _g1 < len(arr) else None)
                    _g1 = (_g1 + 1)
                    _gthis._items.add(i)
            elif (tmp == 2):
                _hx_list = _g.params[0]
                _g_head = _hx_list.h
                while (_g_head is not None):
                    val = _g_head.item
                    _g_head = _g_head.next
                    i = val
                    _gthis._items.add(i)
            else:
                pass
        self._sync.execute(_hx_local_1)

    def clear(self):
        _gthis = self
        def _hx_local_0():
            _gthis._items = haxe_ds_List()
        self._sync.execute(_hx_local_0)

    def remove(self,x):
        _gthis = self
        def _hx_local_1():
            def _hx_local_0():
                if (_gthis.indexOf(x) == -1):
                    return False
                return _gthis._items.remove(x)
            return self._sync.execute(_hx_local_0)
        return _hx_local_1()

    def indexOf(self,x,startAt = None):
        if (startAt is None):
            startAt = 0
        _gthis = self
        def _hx_local_2():
            def _hx_local_1():
                i = 0
                _g_head = _gthis._items.h
                while (_g_head is not None):
                    val = _g_head.item
                    _g_head = _g_head.next
                    item = val
                    if ((i >= startAt) and (HxOverrides.eq(item,x))):
                        return i
                    i = (i + 1)
                return -1
            return self._sync.execute(_hx_local_1)
        return _hx_local_2()

    def iterator(self):
        _gthis = self
        def _hx_local_1():
            def _hx_local_0():
                return haxe_ds__List_ListIterator(_gthis._items.h)
            return self._sync.execute(_hx_local_0)
        return _hx_local_1()

    def toArray(self):
        _gthis = self
        def _hx_local_1():
            def _hx_local_0():
                arr = list()
                _g_head = _gthis._items.h
                while (_g_head is not None):
                    val = _g_head.item
                    _g_head = _g_head.next
                    item = val
                    arr.append(item)
                return arr
            return self._sync.execute(_hx_local_0)
        return _hx_local_1()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._items = None
        _hx_o._sync = None
hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedListImpl._hx_class = hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedListImpl
_hx_classes["hx.concurrent.collection._SynchronizedLinkedList.SynchronizedLinkedListImpl"] = hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedListImpl


class apptimize_util_ABTDispatch:
    _hx_class_name = "apptimize.util.ABTDispatch"
    __slots__ = ("executor", "delayedTasks", "name")
    _hx_fields = ["executor", "delayedTasks", "name"]
    _hx_methods = ["dispatch", "start"]
    _hx_statics = ["dispatchImmediately"]

    def __init__(self,name):
        self.delayedTasks = hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedList_Impl_._new()
        self.executor = None
        self.name = name

    def dispatch(self,task,delay = None):
        if (delay is None):
            delay = 0
        if (self.executor is None):
            self.delayedTasks.add(apptimize_util_ABTDispatchTask(task,delay))
            return
        try:
            this1 = hx_concurrent_internal__Either2__Either2.a(task)
            self.executor.submit(this1,hx_concurrent_executor_Schedule.ONCE(delay))
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_ABTLogger.e(((("Dispatcher '" + HxOverrides.stringOrNull(self.name)) + "' threw an exception submitting a task: ") + Std.string(e)),_hx_AnonObject({'fileName': "src/apptimize/util/ABTDispatch.hx", 'lineNumber': 56, 'className': "apptimize.util.ABTDispatch", 'methodName': "dispatch"}))

    def start(self,maxThreads = None):
        if (maxThreads is None):
            maxThreads = 1
        if (self.executor is not None):
            return
        if (maxThreads < 1):
            apptimize_ABTLogger.w((((("Invalid thread count of " + Std.string(maxThreads)) + ". Starting dispatcher '") + HxOverrides.stringOrNull(self.name)) + "' with minimum thread pool size of 1."),_hx_AnonObject({'fileName': "src/apptimize/util/ABTDispatch.hx", 'lineNumber': 76, 'className': "apptimize.util.ABTDispatch", 'methodName': "start"}))
            maxThreads = 1
        self.executor = hx_concurrent_executor_Executor.create(maxThreads)
        errors = haxe_ds_List()
        task = self.delayedTasks.iterator()
        while task.hasNext():
            task1 = task.next()
            try:
                b = (task1.startTimestampMs - ((Date.now().date.timestamp() * 1000)))
                def _hx_local_1():
                    _hx_local_0 = (0 if (python_lib_Math.isnan(0)) else (b if (python_lib_Math.isnan(b)) else max(0,b)))
                    if (Std.isOfType(_hx_local_0,Int) or ((_hx_local_0 is None))):
                        _hx_local_0
                    else:
                        raise "Class cast error"
                    return _hx_local_0
                delay = _hx_local_1()
                this1 = hx_concurrent_internal__Either2__Either2.a(task1.task)
                self.executor.submit(this1,hx_concurrent_executor_Schedule.ONCE(delay))
            except BaseException as _g:
                None
                e = haxe_Exception.caught(_g).unwrap()
                errors.add(e)
        self.delayedTasks.clear()
        if (not errors.isEmpty()):
            apptimize_ABTLogger.e((("One or more errors occurred starting dispatcher '" + HxOverrides.stringOrNull(self.name)) + "':"),_hx_AnonObject({'fileName': "src/apptimize/util/ABTDispatch.hx", 'lineNumber': 97, 'className': "apptimize.util.ABTDispatch", 'methodName': "start"}))
            _g_head = errors.h
            while (_g_head is not None):
                val = _g_head.item
                _g_head = _g_head.next
                error = val
                apptimize_ABTLogger.e(((("Dispatcher '" + HxOverrides.stringOrNull(self.name)) + "' threw an exception submitting a task: ") + ("null" if error is None else error)),_hx_AnonObject({'fileName': "src/apptimize/util/ABTDispatch.hx", 'lineNumber': 99, 'className': "apptimize.util.ABTDispatch", 'methodName': "start"}))

    @staticmethod
    def dispatchImmediately(task):
        task()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.executor = None
        _hx_o.delayedTasks = None
        _hx_o.name = None
apptimize_util_ABTDispatch._hx_class = apptimize_util_ABTDispatch
_hx_classes["apptimize.util.ABTDispatch"] = apptimize_util_ABTDispatch


class apptimize_api_ABTApiResultsPost:
    _hx_class_name = "apptimize.api.ABTApiResultsPost"
    __slots__ = ("_apiClient", "_appKey", "_uniqueID", "_requestBytes", "_success", "_failure", "_failureCount", "_url")
    _hx_fields = ["_apiClient", "_appKey", "_uniqueID", "_requestBytes", "_success", "_failure", "_failureCount", "_url"]
    _hx_methods = ["_getUrl", "_post", "incrementFailureCountForCode", "hxSerialize", "hxUnserialize"]
    _hx_statics = ["MAX_FAILURE_DELAY_MS", "DEFAULT_FAILURE_DELAY_MS", "_failureDelayMs", "_pendingMap", "_pendingResults", "_postDispatch", "_loadedPending", "PENDING_LOCK", "_getPendingResultsCount", "onSuccess", "postNextRequestForID", "decrementPendingCount", "incrementFailureDelay", "clearFailureDelay", "onFailure", "pushRequest", "savePendingLogs", "loadPendingLogs", "startDispatching"]

    def __init__(self,client,applicationKey,log,success,failure):
        self._url = None
        self._requestBytes = None
        self._failureCount = 0
        self._apiClient = client
        self._appKey = applicationKey
        self._success = success
        self._failure = failure
        self._uniqueID = log.getUniqueUserKey()
        self._url = self._getUrl(applicationKey)
        jsonBytes = haxe_io_Bytes.ofString(log.toJSON())
        self._requestBytes = jsonBytes

    def _getUrl(self,appKey):
        metadata = apptimize_ABTDataStore.sharedInstance().getMetaData(appKey)
        if (metadata is None):
            return None
        urls = metadata.getCheckinUrls()
        if ((urls is None) or ((len(urls) < 1))):
            return None
        index = Math.floor(((((len(urls) - 1) + 1)) * python_lib_Random.random()))
        endpoint = "server/v4/"
        return (HxOverrides.stringOrNull((urls[index] if index >= 0 and index < len(urls) else None)) + ("null" if endpoint is None else endpoint))

    def _post(self):
        _gthis = self
        if (not apptimize_ApptimizeInternal._isInitialized()):
            return
        if (self._url is None):
            self._url = self._getUrl(self._appKey)
            if (self._url is None):
                apptimize_ABTLogger.e("Unable to post results until metadata is available.",_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiResultsPost.hx", 'lineNumber': 155, 'className': "apptimize.api.ABTApiResultsPost", 'methodName': "_post"}))
                apptimize_api_ABTApiResultsPost.onFailure(self,None)
                return
        apptimize_ABTLogger.v(("Posting results to: " + HxOverrides.stringOrNull(self._url)),_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiResultsPost.hx", 'lineNumber': 161, 'className': "apptimize.api.ABTApiResultsPost", 'methodName': "_post"}))
        def _hx_local_0(response):
            apptimize_ABTLogger.d("Successfully posted results.",_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiResultsPost.hx", 'lineNumber': 171, 'className': "apptimize.api.ABTApiResultsPost", 'methodName': "_post"}))
            apptimize_ABTLogger.d(("Results JSON:\n" + Std.string(_gthis._requestBytes)),_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiResultsPost.hx", 'lineNumber': 172, 'className': "apptimize.api.ABTApiResultsPost", 'methodName': "_post"}))
            apptimize_api_ABTApiResultsPost.onSuccess(_gthis,response)
        def _hx_local_1(response):
            _gthis.incrementFailureCountForCode(response.responseCode)
            apptimize_ABTLogger.e(((("Failed to post results, queuing for retry later: " + Std.string(response.responseCode)) + " ") + HxOverrides.stringOrNull(response.text)),_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiResultsPost.hx", 'lineNumber': 179, 'className': "apptimize.api.ABTApiResultsPost", 'methodName': "_post"}))
            apptimize_ABTLogger.e(("Results JSON:\n" + Std.string(_gthis._requestBytes)),_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiResultsPost.hx", 'lineNumber': 180, 'className': "apptimize.api.ABTApiResultsPost", 'methodName': "_post"}))
            apptimize_api_ABTApiResultsPost.onFailure(_gthis,response)
        apptimize_http_ABTHttpRequest.post(self._url,self._requestBytes,self._appKey,_hx_local_0,_hx_local_1)

    def incrementFailureCountForCode(self,status):
        if (status >= 400):
            _hx_local_0 = self
            _hx_local_1 = _hx_local_0._failureCount
            _hx_local_0._failureCount = (_hx_local_1 + 1)
            _hx_local_1

    def hxSerialize(self,s):
        s.serialize(self._appKey)
        s.serialize(self._requestBytes)
        s.serialize(self._failureCount)
        s.serialize(self._url)
        s.serialize(self._uniqueID)

    def hxUnserialize(self,u):
        self._appKey = u.unserialize()
        self._requestBytes = u.unserialize()
        self._failureCount = u.unserialize()
        self._url = u.unserialize()
        self._uniqueID = u.unserialize()

    @staticmethod
    def _getPendingResultsCount():
        count = 0
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.acquire()
        try:
            _this = apptimize_api_ABTApiResultsPost._pendingResults
            _gthis = _this
            def _hx_local_1():
                _hx_len = 0
                _g_head = _gthis._items.h
                while (_g_head is not None):
                    val = _g_head.item
                    _g_head = _g_head.next
                    item = val
                    _hx_len = (_hx_len + 1)
                return _hx_len
            count = _this._sync.execute(_hx_local_1)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
        return count

    @staticmethod
    def onSuccess(request,response):
        apptimize_api_ABTApiResultsPost.clearFailureDelay()
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.acquire()
        try:
            apptimize_api_ABTApiResultsPost._pendingResults.remove(request)
            count = apptimize_api_ABTApiResultsPost.decrementPendingCount(request._uniqueID)
            if (count > 0):
                apptimize_api_ABTApiResultsPost.postNextRequestForID(request._uniqueID)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
        if ((request is not None) and ((request._success is not None))):
            request._success(response)

    @staticmethod
    def postNextRequestForID(id):
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.acquire()
        try:
            request = apptimize_api_ABTApiResultsPost._pendingResults.iterator()
            while request.hasNext():
                request1 = [request.next()]
                if ((request1[0] if 0 < len(request1) else None)._uniqueID == id):
                    def _hx_local_1(request):
                        def _hx_local_0():
                            (request[0] if 0 < len(request) else None)._post()
                        return _hx_local_0
                    task = _hx_local_1(request1)
                    if (apptimize_api_ABTApiResultsPost._postDispatch is not None):
                        apptimize_api_ABTApiResultsPost._postDispatch.dispatch(task,0)
                    else:
                        apptimize_util_ABTDispatch.dispatchImmediately(task)
                    break
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()

    @staticmethod
    def decrementPendingCount(id):
        count = 0
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.acquire()
        try:
            count = apptimize_api_ABTApiResultsPost._pendingMap.h.get(id,None)
            count = (count - 1)
            if (count == 0):
                apptimize_api_ABTApiResultsPost._pendingMap.remove(id)
            else:
                apptimize_api_ABTApiResultsPost._pendingMap.h[id] = count
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
        return count

    @staticmethod
    def incrementFailureDelay():
        delay = (apptimize_api_ABTApiResultsPost._failureDelayMs.get_value() * 2)
        if (delay > apptimize_api_ABTApiResultsPost.MAX_FAILURE_DELAY_MS):
            delay = apptimize_api_ABTApiResultsPost.MAX_FAILURE_DELAY_MS
        apptimize_api_ABTApiResultsPost._failureDelayMs.set_value(delay)
        return apptimize_api_ABTApiResultsPost._failureDelayMs.get_value()

    @staticmethod
    def clearFailureDelay():
        apptimize_api_ABTApiResultsPost._failureDelayMs.set_value(apptimize_api_ABTApiResultsPost.DEFAULT_FAILURE_DELAY_MS)

    @staticmethod
    def onFailure(request,response):
        if (request._failureCount > apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.MAXIMUM_RESULT_POST_FAILURE_KEY)):
            apptimize_ABTLogger.e("Dropping result post after repeated failure.",_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiResultsPost.hx", 'lineNumber': 265, 'className': "apptimize.api.ABTApiResultsPost", 'methodName': "onFailure"}))
            apptimize_api_ABTApiResultsPost.PENDING_LOCK.acquire()
            try:
                apptimize_api_ABTApiResultsPost._pendingResults.remove(request)
                count = apptimize_api_ABTApiResultsPost.decrementPendingCount(request._uniqueID)
                if (count > 0):
                    apptimize_api_ABTApiResultsPost.postNextRequestForID(request._uniqueID)
            except BaseException as _g:
                None
                e = haxe_Exception.caught(_g).unwrap()
                apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
                raise haxe_Exception.thrown(e)
            apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
        else:
            def _hx_local_0():
                request._post()
            task = _hx_local_0
            if (apptimize_api_ABTApiResultsPost._postDispatch is not None):
                apptimize_api_ABTApiResultsPost._postDispatch.dispatch(task,apptimize_api_ABTApiResultsPost.incrementFailureDelay())
            else:
                apptimize_util_ABTDispatch.dispatchImmediately(task)
        if (request._failure is not None):
            request._failure(response)

    @staticmethod
    def pushRequest(resultRequest,savePending = None):
        if (savePending is None):
            savePending = True
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.acquire()
        try:
            apptimize_api_ABTApiResultsPost._pendingResults.add(resultRequest)
            if (not (resultRequest._uniqueID in apptimize_api_ABTApiResultsPost._pendingMap.h)):
                apptimize_api_ABTApiResultsPost._pendingMap.h[resultRequest._uniqueID] = 1
                def _hx_local_0():
                    resultRequest._post()
                task = _hx_local_0
                if (apptimize_api_ABTApiResultsPost._postDispatch is not None):
                    apptimize_api_ABTApiResultsPost._postDispatch.dispatch(task,0)
                else:
                    apptimize_util_ABTDispatch.dispatchImmediately(task)
            else:
                _this = apptimize_api_ABTApiResultsPost._pendingMap
                key = resultRequest._uniqueID
                value = (apptimize_api_ABTApiResultsPost._pendingMap.h.get(resultRequest._uniqueID,None) + 1)
                _this.h[key] = value
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()

    @staticmethod
    def savePendingLogs():
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.acquire()
        try:
            apptimize_support_persistence_ABTPersistence.saveObject(apptimize_support_persistence_ABTPersistence.kResultPostsListKey,apptimize_api_ABTApiResultsPost._pendingResults.toArray())
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()

    @staticmethod
    def loadPendingLogs():
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.acquire()
        try:
            if (apptimize_api_ABTApiResultsPost._loadedPending == False):
                pendingObject = apptimize_support_persistence_ABTPersistence.loadObject(apptimize_support_persistence_ABTPersistence.kResultPostsListKey)
                try:
                    pendingArray = (list() if ((pendingObject is None)) else pendingObject)
                    _g = 0
                    while (_g < len(pendingArray)):
                        p = (pendingArray[_g] if _g >= 0 and _g < len(pendingArray) else None)
                        _g = (_g + 1)
                        apptimize_api_ABTApiResultsPost.pushRequest(p,False)
                except BaseException as _g:
                    None
                    e = haxe_Exception.caught(_g).unwrap()
                    apptimize_ABTLogger.e(("Unable to load pending results posts: " + Std.string(e)),_hx_AnonObject({'fileName': "src/apptimize/api/ABTApiResultsPost.hx", 'lineNumber': 333, 'className': "apptimize.api.ABTApiResultsPost", 'methodName': "loadPendingLogs"}))
            apptimize_api_ABTApiResultsPost._loadedPending = True
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_api_ABTApiResultsPost.PENDING_LOCK.release()

    @staticmethod
    def startDispatching(threadCount):
        apptimize_api_ABTApiResultsPost._postDispatch.start(threadCount)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._apiClient = None
        _hx_o._appKey = None
        _hx_o._uniqueID = None
        _hx_o._requestBytes = None
        _hx_o._success = None
        _hx_o._failure = None
        _hx_o._failureCount = None
        _hx_o._url = None
apptimize_api_ABTApiResultsPost._hx_class = apptimize_api_ABTApiResultsPost
_hx_classes["apptimize.api.ABTApiResultsPost"] = apptimize_api_ABTApiResultsPost


class apptimize_api_ABTMetadataPoller:
    _hx_class_name = "apptimize.api.ABTMetadataPoller"
    __slots__ = ()
    _hx_statics = ["_metadataTimer", "_interval", "_backgroundInterval", "_isPolling", "_isThreadingEnabled", "isPolling", "stopPolling", "startPolling", "_stopMetadataTimer", "_startMetadataTimer"]
    _metadataTimer = None
    _interval = None
    _backgroundInterval = None
    _isPolling = None
    _isThreadingEnabled = None

    @staticmethod
    def isPolling():
        return apptimize_api_ABTMetadataPoller._isPolling

    @staticmethod
    def stopPolling():
        apptimize_api_ABTMetadataPoller._stopMetadataTimer()
        apptimize_api_ABTMetadataPoller._isPolling = False

    @staticmethod
    def startPolling(foreground = None):
        if (foreground is None):
            foreground = True
        apptimize_api_ABTMetadataPoller._isThreadingEnabled = apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.THREADING_ENABLED_KEY)
        apptimize_api_ABTMetadataPoller._interval = apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.METADATA_POLLING_INTERVAL_MS_KEY)
        apptimize_api_ABTMetadataPoller._backgroundInterval = apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.METADATA_POLLING_BACKGROUND_INTERVAL_MS_KEY)
        apptimize_api_ABTMetadataPoller._stopMetadataTimer()
        time = (apptimize_api_ABTMetadataPoller._interval if foreground else apptimize_api_ABTMetadataPoller._backgroundInterval)
        if (time > 0):
            apptimize_ABTLogger.v((("Metadata update interval set to " + Std.string(time)) + " milliseconds."),_hx_AnonObject({'fileName': "src/apptimize/api/ABTMetadataPoller.hx", 'lineNumber': 52, 'className': "apptimize.api.ABTMetadataPoller", 'methodName': "startPolling"}))
            apptimize_api_ABTMetadataPoller._startMetadataTimer(time)
            apptimize_api_ABTMetadataPoller._isPolling = True

    @staticmethod
    def _stopMetadataTimer():
        if (apptimize_api_ABTMetadataPoller._metadataTimer is not None):
            apptimize_api_ABTMetadataPoller._metadataTimer.stop()
            apptimize_api_ABTMetadataPoller._metadataTimer = None

    @staticmethod
    def _startMetadataTimer(interval):
        if (not apptimize_api_ABTMetadataPoller._isThreadingEnabled):
            return
        if (apptimize_api_ABTMetadataPoller._metadataTimer is not None):
            apptimize_api_ABTMetadataPoller._stopMetadataTimer()
        apptimize_api_ABTMetadataPoller._metadataTimer = apptimize_util_ABTTimer(interval)
        apptimize_api_ABTMetadataPoller._metadataTimer.run = apptimize_Apptimize.updateApptimizeMetadataOnce
apptimize_api_ABTMetadataPoller._hx_class = apptimize_api_ABTMetadataPoller
_hx_classes["apptimize.api.ABTMetadataPoller"] = apptimize_api_ABTMetadataPoller


class apptimize_api_ABTMetadataProcessor:
    _hx_class_name = "apptimize.api.ABTMetadataProcessor"
    __slots__ = ()
    _hx_statics = ["jsonFromMetadataDownload"]

    @staticmethod
    def jsonFromMetadataDownload(_hx_bytes):
        decompressedData = apptimize_util_ABTUtilGzip.decompress(_hx_bytes)
        return decompressedData.getString(0,decompressedData.length)
apptimize_api_ABTMetadataProcessor._hx_class = apptimize_api_ABTMetadataProcessor
_hx_classes["apptimize.api.ABTMetadataProcessor"] = apptimize_api_ABTMetadataProcessor


class apptimize_api_ABTSecondaryValuesClient:
    _hx_class_name = "apptimize.api.ABTSecondaryValuesClient"
    __slots__ = ("_fetching",)
    _hx_fields = ["_fetching"]
    _hx_methods = ["fetching", "fetch", "fetchNext", "needNewUrls"]

    def __init__(self):
        self._fetching = False

    def fetching(self):
        return self._fetching

    def fetch(self,urls,startingValues,done):
        _gthis = self
        self._fetching = True
        state = apptimize_api_ABTSecValFetchState(urls,startingValues)
        needFetch = (not state.missingUrls.isEmpty())
        def _hx_local_0(allValues):
            _gthis._fetching = False
            done(allValues,needFetch)
        self.fetchNext(state,_hx_local_0)

    def fetchNext(self,state,done):
        _gthis = self
        if state.missingUrls.isEmpty():
            done(state.allValues)
            return
        url = state.missingUrls.pop()
        def _hx_local_0(response):
            _hx_bytes = haxe_io_Bytes.ofData(response.bytes)
            this1 = state.allValues
            v = python_lib_Json.loads(_hx_bytes.getString(0,_hx_bytes.length),**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'object_hook': python_Lib.dictToAnon})))
            this1.h[url] = v
            _gthis.fetchNext(state,done)
        def _hx_local_1(response):
            apptimize_ABTLogger.e(((("GET " + ("null" if url is None else url)) + " failed: ") + Std.string(response.responseCode)),_hx_AnonObject({'fileName': "src/apptimize/api/ABTSecondaryValuesClient.hx", 'lineNumber': 47, 'className': "apptimize.api.ABTSecondaryValuesClient", 'methodName': "fetchNext"}))
            _gthis.fetchNext(state,done)
        apptimize_http_ABTHttpRequest.get(url,None,_hx_local_0,_hx_local_1)

    def needNewUrls(self,old,current):
        def _hx_local_1():
            def _hx_local_0(item):
                return (python_internal_ArrayImpl.indexOf(old,item,None) < 0)
            return (len(list(filter(_hx_local_0,current))) > 0)
        return _hx_local_1()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._fetching = None
apptimize_api_ABTSecondaryValuesClient._hx_class = apptimize_api_ABTSecondaryValuesClient
_hx_classes["apptimize.api.ABTSecondaryValuesClient"] = apptimize_api_ABTSecondaryValuesClient


class apptimize_api_ABTSecValFetchState:
    _hx_class_name = "apptimize.api.ABTSecValFetchState"
    __slots__ = ("missingUrls", "allValues")
    _hx_fields = ["missingUrls", "allValues"]

    def __init__(self,allUrls,oldValues):
        missingUrls = haxe_ds_List()
        startingValues = haxe_ds_StringMap()
        _g = 0
        while (_g < len(allUrls)):
            url = (allUrls[_g] if _g >= 0 and _g < len(allUrls) else None)
            _g = (_g + 1)
            if ((oldValues is not None) and (url in oldValues.h)):
                v = oldValues.h.get(url,None)
                startingValues.h[url] = v
            else:
                missingUrls.add(url)
        self.missingUrls = missingUrls
        self.allValues = startingValues

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.missingUrls = None
        _hx_o.allValues = None
apptimize_api_ABTSecValFetchState._hx_class = apptimize_api_ABTSecValFetchState
_hx_classes["apptimize.api.ABTSecValFetchState"] = apptimize_api_ABTSecValFetchState


class apptimize_api_ABTUserGuid:
    _hx_class_name = "apptimize.api.ABTUserGuid"
    __slots__ = ()
    _hx_statics = ["_userGuid", "generateUserGuid", "S4", "isValidGuid"]
    _userGuid = None

    @staticmethod
    def generateUserGuid():
        apptimize_api_ABTUserGuid._userGuid = (((((((((((HxOverrides.stringOrNull(apptimize_api_ABTUserGuid.S4()) + HxOverrides.stringOrNull(apptimize_api_ABTUserGuid.S4())) + "-") + HxOverrides.stringOrNull(apptimize_api_ABTUserGuid.S4())) + "-") + HxOverrides.stringOrNull(apptimize_api_ABTUserGuid.S4())) + "-") + HxOverrides.stringOrNull(apptimize_api_ABTUserGuid.S4())) + "-") + HxOverrides.stringOrNull(apptimize_api_ABTUserGuid.S4())) + HxOverrides.stringOrNull(apptimize_api_ABTUserGuid.S4())) + HxOverrides.stringOrNull(apptimize_api_ABTUserGuid.S4()))
        return apptimize_api_ABTUserGuid._userGuid

    @staticmethod
    def S4(randomFunction = None):
        if (randomFunction is None):
            randomFunction = _Math_Math_Impl_.random
        x = (randomFunction() * 65536)
        rnd = None
        try:
            rnd = int(x)
        except BaseException as _g:
            None
            rnd = None
        return StringTools.hex(rnd,4)

    @staticmethod
    def isValidGuid(guid):
        regex = EReg("(^([0-9A-Fa-f]{8}[-][0-9A-Fa-f]{4}[-][0-9A-Fa-f]{4}[-][0-9A-Fa-f]{4}[-][0-9A-Fa-f]{12})$)","")
        regex.matchObj = python_lib_Re.search(regex.pattern,guid)
        return (regex.matchObj is not None)
apptimize_api_ABTUserGuid._hx_class = apptimize_api_ABTUserGuid
_hx_classes["apptimize.api.ABTUserGuid"] = apptimize_api_ABTUserGuid


class apptimize_events_ABTEventManager:
    _hx_class_name = "apptimize.events.ABTEventManager"
    __slots__ = ()
    _hx_statics = ["_onParticipationCallback", "_onMetadataUpdatedCallback", "_onParticipatedInExperimentCallback", "_onApptimizeInitializedCallback", "setOnMetadataUpdatedCallback", "dispatchOnMetadataUpdated", "setOnParticipationCallback", "dispatchOnParticipation", "setOnParticipatedInExperimentCallback", "dispatchOnParticipatedInExperiment", "setOnApptimizeInitializedCallback", "dispatchOnApptimizeInitialized"]
    _onParticipationCallback = None
    _onMetadataUpdatedCallback = None
    _onParticipatedInExperimentCallback = None
    _onApptimizeInitializedCallback = None

    @staticmethod
    def setOnMetadataUpdatedCallback(updatedCallback):
        apptimize_events_ABTEventManager._onMetadataUpdatedCallback = updatedCallback

    @staticmethod
    def dispatchOnMetadataUpdated():
        if (apptimize_events_ABTEventManager._onMetadataUpdatedCallback is not None):
            apptimize_events_ABTEventManager._onMetadataUpdatedCallback()

    @staticmethod
    def setOnParticipationCallback(runCallback):
        apptimize_events_ABTEventManager._onParticipationCallback = runCallback

    @staticmethod
    def dispatchOnParticipation(experimentName,variantName):
        if (apptimize_events_ABTEventManager._onParticipationCallback is not None):
            apptimize_events_ABTEventManager._onParticipationCallback(experimentName,variantName)

    @staticmethod
    def setOnParticipatedInExperimentCallback(callback):
        apptimize_events_ABTEventManager._onParticipatedInExperimentCallback = callback

    @staticmethod
    def dispatchOnParticipatedInExperiment(variantInfo,isFirstParticipation):
        if (apptimize_events_ABTEventManager._onParticipatedInExperimentCallback is not None):
            apptimize_events_ABTEventManager._onParticipatedInExperimentCallback(variantInfo,isFirstParticipation)
        apptimize_events_ABTEventManager.dispatchOnParticipation(variantInfo.getExperimentName(),variantInfo.getVariantName())

    @staticmethod
    def setOnApptimizeInitializedCallback(callback):
        apptimize_events_ABTEventManager._onApptimizeInitializedCallback = callback

    @staticmethod
    def dispatchOnApptimizeInitialized():
        if (apptimize_events_ABTEventManager._onApptimizeInitializedCallback is not None):
            apptimize_events_ABTEventManager._onApptimizeInitializedCallback()
apptimize_events_ABTEventManager._hx_class = apptimize_events_ABTEventManager
_hx_classes["apptimize.events.ABTEventManager"] = apptimize_events_ABTEventManager

class apptimize_filter_ABTFilterResult(Enum):
    __slots__ = ()
    _hx_class_name = "apptimize.filter.ABTFilterResult"
    _hx_constructs = ["ABTFilterResultUnknown", "ABTFilterResultFalse", "ABTFilterResultTrue"]
apptimize_filter_ABTFilterResult.ABTFilterResultUnknown = apptimize_filter_ABTFilterResult("ABTFilterResultUnknown", 0, ())
apptimize_filter_ABTFilterResult.ABTFilterResultFalse = apptimize_filter_ABTFilterResult("ABTFilterResultFalse", 1, ())
apptimize_filter_ABTFilterResult.ABTFilterResultTrue = apptimize_filter_ABTFilterResult("ABTFilterResultTrue", 2, ())
apptimize_filter_ABTFilterResult._hx_class = apptimize_filter_ABTFilterResult
_hx_classes["apptimize.filter.ABTFilterResult"] = apptimize_filter_ABTFilterResult

class apptimize_filter_ABTFilterPropertySource(Enum):
    __slots__ = ()
    _hx_class_name = "apptimize.filter.ABTFilterPropertySource"
    _hx_constructs = ["ABTFilterPropertySourceDevice", "ABTFilterPropertySourceUser", "ABTFilterPropertySourcePrefixed"]
apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourceDevice = apptimize_filter_ABTFilterPropertySource("ABTFilterPropertySourceDevice", 0, ())
apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourceUser = apptimize_filter_ABTFilterPropertySource("ABTFilterPropertySourceUser", 1, ())
apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourcePrefixed = apptimize_filter_ABTFilterPropertySource("ABTFilterPropertySourcePrefixed", 2, ())
apptimize_filter_ABTFilterPropertySource._hx_class = apptimize_filter_ABTFilterPropertySource
_hx_classes["apptimize.filter.ABTFilterPropertySource"] = apptimize_filter_ABTFilterPropertySource

class apptimize_filter_ABTFilterType(Enum):
    __slots__ = ()
    _hx_class_name = "apptimize.filter.ABTFilterType"
    _hx_constructs = ["ABTFilterTypeUnknown", "ABTFilterTypeSimple", "ABTFilterTypeList", "ABTFilterTypeSet", "ABTFilterTypeCompound", "ABTFilterTypePropertyless", "ABTFilterTypeNamed"]
apptimize_filter_ABTFilterType.ABTFilterTypeUnknown = apptimize_filter_ABTFilterType("ABTFilterTypeUnknown", 0, ())
apptimize_filter_ABTFilterType.ABTFilterTypeSimple = apptimize_filter_ABTFilterType("ABTFilterTypeSimple", 1, ())
apptimize_filter_ABTFilterType.ABTFilterTypeList = apptimize_filter_ABTFilterType("ABTFilterTypeList", 2, ())
apptimize_filter_ABTFilterType.ABTFilterTypeSet = apptimize_filter_ABTFilterType("ABTFilterTypeSet", 3, ())
apptimize_filter_ABTFilterType.ABTFilterTypeCompound = apptimize_filter_ABTFilterType("ABTFilterTypeCompound", 4, ())
apptimize_filter_ABTFilterType.ABTFilterTypePropertyless = apptimize_filter_ABTFilterType("ABTFilterTypePropertyless", 5, ())
apptimize_filter_ABTFilterType.ABTFilterTypeNamed = apptimize_filter_ABTFilterType("ABTFilterTypeNamed", 6, ())
apptimize_filter_ABTFilterType._hx_class = apptimize_filter_ABTFilterType
_hx_classes["apptimize.filter.ABTFilterType"] = apptimize_filter_ABTFilterType

class apptimize_filter_ABTFilterOperator(Enum):
    __slots__ = ()
    _hx_class_name = "apptimize.filter.ABTFilterOperator"
    _hx_constructs = ["ABTFilterOperatorUnknown", "ABTFilterOperatorEquals", "ABTFilterOperatorNotEquals", "ABTFilterOperatorRegex", "ABTFilterOperatorNotRegex", "ABTFilterOperatorGreaterThan", "ABTFilterOperatorGreaterThanOrEqual", "ABTFilterOperatorLessThan", "ABTFilterOperatorLessThanOrEqual", "ABTFilterOperatorInList", "ABTFilterOperatorNotInList", "ABTFilterOperatorIntersection", "ABTFilterOperatorCompoundOr", "ABTFilterOperatorCompoundAnd", "ABTFilterOperatorCompoundSingleNot", "ABTFilterOperatorCompoundSingleIsNull", "ABTFilterOperatorCompoundSingleIsNotNull", "ABTFilterOperatorPropertyIsNull", "ABTFilterOperatorPropertyIsNotNull", "ABTFilterOperatorPropertyIsRecognized", "ABTFilterOperatorPropertyIsNotRecognized", "ABTFilterOperatorOperatorIsRecognized", "ABTFilterOperatorOperatorIsNotRecognized", "ABTFilterOperatorValueOf"]
apptimize_filter_ABTFilterOperator.ABTFilterOperatorUnknown = apptimize_filter_ABTFilterOperator("ABTFilterOperatorUnknown", 0, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorEquals = apptimize_filter_ABTFilterOperator("ABTFilterOperatorEquals", 1, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotEquals = apptimize_filter_ABTFilterOperator("ABTFilterOperatorNotEquals", 2, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorRegex = apptimize_filter_ABTFilterOperator("ABTFilterOperatorRegex", 3, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotRegex = apptimize_filter_ABTFilterOperator("ABTFilterOperatorNotRegex", 4, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorGreaterThan = apptimize_filter_ABTFilterOperator("ABTFilterOperatorGreaterThan", 5, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorGreaterThanOrEqual = apptimize_filter_ABTFilterOperator("ABTFilterOperatorGreaterThanOrEqual", 6, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorLessThan = apptimize_filter_ABTFilterOperator("ABTFilterOperatorLessThan", 7, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorLessThanOrEqual = apptimize_filter_ABTFilterOperator("ABTFilterOperatorLessThanOrEqual", 8, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorInList = apptimize_filter_ABTFilterOperator("ABTFilterOperatorInList", 9, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotInList = apptimize_filter_ABTFilterOperator("ABTFilterOperatorNotInList", 10, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorIntersection = apptimize_filter_ABTFilterOperator("ABTFilterOperatorIntersection", 11, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundOr = apptimize_filter_ABTFilterOperator("ABTFilterOperatorCompoundOr", 12, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundAnd = apptimize_filter_ABTFilterOperator("ABTFilterOperatorCompoundAnd", 13, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundSingleNot = apptimize_filter_ABTFilterOperator("ABTFilterOperatorCompoundSingleNot", 14, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundSingleIsNull = apptimize_filter_ABTFilterOperator("ABTFilterOperatorCompoundSingleIsNull", 15, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundSingleIsNotNull = apptimize_filter_ABTFilterOperator("ABTFilterOperatorCompoundSingleIsNotNull", 16, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsNull = apptimize_filter_ABTFilterOperator("ABTFilterOperatorPropertyIsNull", 17, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsNotNull = apptimize_filter_ABTFilterOperator("ABTFilterOperatorPropertyIsNotNull", 18, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsRecognized = apptimize_filter_ABTFilterOperator("ABTFilterOperatorPropertyIsRecognized", 19, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsNotRecognized = apptimize_filter_ABTFilterOperator("ABTFilterOperatorPropertyIsNotRecognized", 20, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorOperatorIsRecognized = apptimize_filter_ABTFilterOperator("ABTFilterOperatorOperatorIsRecognized", 21, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorOperatorIsNotRecognized = apptimize_filter_ABTFilterOperator("ABTFilterOperatorOperatorIsNotRecognized", 22, ())
apptimize_filter_ABTFilterOperator.ABTFilterOperatorValueOf = apptimize_filter_ABTFilterOperator("ABTFilterOperatorValueOf", 23, ())
apptimize_filter_ABTFilterOperator._hx_class = apptimize_filter_ABTFilterOperator
_hx_classes["apptimize.filter.ABTFilterOperator"] = apptimize_filter_ABTFilterOperator


class apptimize_filter_ABTFilter:
    _hx_class_name = "apptimize.filter.ABTFilter"
    __slots__ = ("property", "propertySource", "value", "filterType", "filterOperator", "callServerURLKey")
    _hx_fields = ["property", "propertySource", "value", "filterType", "filterOperator", "callServerURLKey"]
    _hx_methods = ["fromJSON", "isSupportedOperator", "isSupportedProperty", "currentDeviceValue", "hasSupportedProperty", "filterMatchesEnvironment", "getUrlKeys"]
    _hx_statics = ["kABTFilterKeyValue", "kABTFilterKeyType", "kABTFilterKeyProperty", "kABTFilterKeyOperator", "kABTFilterKeyPropertySource", "kABTFilterKeyCallServerInputs", "kABTFilterKeyCallURLKey", "kABTFilterKeyUserAttribute", "kABTFilterKeyPrefixedAttribute", "kABTFilterKeyNamedFilter", "filterFromJSON", "classForType", "filterForTypeFromJSON", "operatorFromString", "typeFromOperator"]

    def __init__(self):
        self.callServerURLKey = None
        self.filterOperator = None
        self.filterType = None
        self.value = None
        self.propertySource = None
        self.property = None

    def fromJSON(self,json):
        jsonProperty = Reflect.field(json,apptimize_filter_ABTFilter.kABTFilterKeyProperty)
        if (jsonProperty is not None):
            self.property = jsonProperty
            self.propertySource = apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourceDevice
        else:
            jsonProperty = Reflect.field(json,apptimize_filter_ABTFilter.kABTFilterKeyUserAttribute)
            if (jsonProperty is not None):
                self.property = jsonProperty
                self.propertySource = apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourceUser
            else:
                jsonProperty = Reflect.field(json,apptimize_filter_ABTFilter.kABTFilterKeyPrefixedAttribute)
                if (jsonProperty is not None):
                    self.property = jsonProperty
                    self.propertySource = apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourcePrefixed
        self.filterOperator = apptimize_filter_ABTFilter.operatorFromString(Reflect.field(json,apptimize_filter_ABTFilter.kABTFilterKeyOperator))
        self.filterType = apptimize_filter_ABTFilter.filterForTypeFromJSON(json)
        if (self.filterType == apptimize_filter_ABTFilterType.ABTFilterTypeUnknown):
            apptimize_ABTLogger.w("Unknown filter type: setting value without type checking.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 149, 'className': "apptimize.filter.ABTFilter", 'methodName': "fromJSON"}))
            self.value = Reflect.field(json,apptimize_filter_ABTFilter.kABTFilterKeyValue)
        self.callServerURLKey = Reflect.field(json,apptimize_filter_ABTFilter.kABTFilterKeyCallURLKey)

    def isSupportedOperator(self,operatorStr):
        return (apptimize_filter_ABTFilter.operatorFromString(operatorStr) != apptimize_filter_ABTFilterOperator.ABTFilterOperatorUnknown)

    def isSupportedProperty(self,env,property,source):
        found = (None != env.valueForProperty(property,source))
        if (not found):
            apptimize_ABTLogger.d((("Property \"" + ("null" if property is None else property)) + "\" not found which is expected by a filter."),_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 166, 'className': "apptimize.filter.ABTFilter", 'methodName': "isSupportedProperty"}))
        return found

    def currentDeviceValue(self,env):
        return env.valueForProperty(self.property,self.propertySource)

    def hasSupportedProperty(self,env):
        return self.isSupportedProperty(env,self.property,self.propertySource)

    def filterMatchesEnvironment(self,env):
        apptimize_ABTLogger.e("Unknown filter type. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 181, 'className': "apptimize.filter.ABTFilter", 'methodName': "filterMatchesEnvironment"}))
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown

    def getUrlKeys(self):
        if (self.callServerURLKey is None):
            return []
        return [self.callServerURLKey]

    @staticmethod
    def filterFromJSON(json):
        filterType = apptimize_filter_ABTFilter.filterForTypeFromJSON(json)
        classType = apptimize_filter_ABTFilter.classForType(filterType)
        if (classType is None):
            apptimize_ABTLogger.e(("Unable to find filter type: " + Std.string(filterType)),_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 110, 'className': "apptimize.filter.ABTFilter", 'methodName': "filterFromJSON"}))
            return None
        abtFilter = classType(*[])
        abtFilter.fromJSON(json)
        return abtFilter

    @staticmethod
    def classForType(filterType):
        if (filterType == apptimize_filter_ABTFilterType.ABTFilterTypeSimple):
            return apptimize_filter_ABTSimpleFilter
        if (filterType == apptimize_filter_ABTFilterType.ABTFilterTypeCompound):
            return apptimize_filter_ABTCompoundFilter
        if (filterType == apptimize_filter_ABTFilterType.ABTFilterTypeList):
            return apptimize_filter_ABTListFilter
        if (filterType == apptimize_filter_ABTFilterType.ABTFilterTypeSet):
            return apptimize_filter_ABTSetFilter
        if (filterType == apptimize_filter_ABTFilterType.ABTFilterTypeNamed):
            return apptimize_filter_ABTNamedFilter
        return apptimize_filter_ABTUnknownFilter

    @staticmethod
    def filterForTypeFromJSON(json):
        abtOperator = apptimize_filter_ABTFilter.operatorFromString(Reflect.field(json,apptimize_filter_ABTFilter.kABTFilterKeyOperator))
        _hx_type = apptimize_filter_ABTFilter.typeFromOperator(abtOperator)
        return _hx_type

    @staticmethod
    def operatorFromString(string):
        if ("=" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorEquals
        if ("!=" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotEquals
        if ("regex" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorRegex
        if ("not_regex" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotRegex
        if (">" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorGreaterThan
        if (">=" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorGreaterThanOrEqual
        if ("<" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorLessThan
        if ("<=" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorLessThanOrEqual
        if ("in" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorInList
        if ("not_in" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotInList
        if ("intersection" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorIntersection
        if ("or" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundOr
        if ("and" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundAnd
        if ("not" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundSingleNot
        if ("is_null" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundSingleIsNull
        if ("is_not_null" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundSingleIsNotNull
        if ("is_property_null" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsNull
        if ("is_property_not_null" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsNotNull
        if ("is_recognized_property" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsRecognized
        if ("is_not_recognized_property" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsNotRecognized
        if ("is_recognized_operator" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorOperatorIsRecognized
        if ("is_not_recognized_operator" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorOperatorIsNotRecognized
        if ("value_of" == string):
            return apptimize_filter_ABTFilterOperator.ABTFilterOperatorValueOf
        return apptimize_filter_ABTFilterOperator.ABTFilterOperatorUnknown

    @staticmethod
    def typeFromOperator(abtOperator):
        tmp = abtOperator.index
        if (tmp == 0):
            pass
        elif (tmp == 1):
            return apptimize_filter_ABTFilterType.ABTFilterTypeSimple
        elif (tmp == 2):
            return apptimize_filter_ABTFilterType.ABTFilterTypeSimple
        elif (tmp == 3):
            return apptimize_filter_ABTFilterType.ABTFilterTypeSimple
        elif (tmp == 4):
            return apptimize_filter_ABTFilterType.ABTFilterTypeSimple
        elif (tmp == 5):
            return apptimize_filter_ABTFilterType.ABTFilterTypeSimple
        elif (tmp == 6):
            return apptimize_filter_ABTFilterType.ABTFilterTypeSimple
        elif (tmp == 7):
            return apptimize_filter_ABTFilterType.ABTFilterTypeSimple
        elif (tmp == 8):
            return apptimize_filter_ABTFilterType.ABTFilterTypeSimple
        elif (tmp == 9):
            return apptimize_filter_ABTFilterType.ABTFilterTypeList
        elif (tmp == 10):
            return apptimize_filter_ABTFilterType.ABTFilterTypeList
        elif (tmp == 11):
            return apptimize_filter_ABTFilterType.ABTFilterTypeSet
        elif (tmp == 12):
            return apptimize_filter_ABTFilterType.ABTFilterTypeCompound
        elif (tmp == 13):
            return apptimize_filter_ABTFilterType.ABTFilterTypeCompound
        elif (tmp == 14):
            return apptimize_filter_ABTFilterType.ABTFilterTypeCompound
        elif (tmp == 15):
            return apptimize_filter_ABTFilterType.ABTFilterTypeCompound
        elif (tmp == 16):
            return apptimize_filter_ABTFilterType.ABTFilterTypeCompound
        elif (tmp == 17):
            return apptimize_filter_ABTFilterType.ABTFilterTypePropertyless
        elif (tmp == 18):
            return apptimize_filter_ABTFilterType.ABTFilterTypePropertyless
        elif (tmp == 19):
            return apptimize_filter_ABTFilterType.ABTFilterTypePropertyless
        elif (tmp == 20):
            return apptimize_filter_ABTFilterType.ABTFilterTypePropertyless
        elif (tmp == 21):
            return apptimize_filter_ABTFilterType.ABTFilterTypePropertyless
        elif (tmp == 22):
            return apptimize_filter_ABTFilterType.ABTFilterTypePropertyless
        elif (tmp == 23):
            return apptimize_filter_ABTFilterType.ABTFilterTypeNamed
        else:
            pass
        apptimize_ABTLogger.e("Unknown filter type. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 298, 'className': "apptimize.filter.ABTFilter", 'methodName': "typeFromOperator"}))
        return apptimize_filter_ABTFilterType.ABTFilterTypeUnknown

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.property = None
        _hx_o.propertySource = None
        _hx_o.value = None
        _hx_o.filterType = None
        _hx_o.filterOperator = None
        _hx_o.callServerURLKey = None
apptimize_filter_ABTFilter._hx_class = apptimize_filter_ABTFilter
_hx_classes["apptimize.filter.ABTFilter"] = apptimize_filter_ABTFilter


class apptimize_filter_ABTSimpleFilter(apptimize_filter_ABTFilter):
    _hx_class_name = "apptimize.filter.ABTSimpleFilter"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["fromJSON", "filterMatchesEnvironment"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilter


    def __init__(self):
        super().__init__()

    def fromJSON(self,json):
        super().fromJSON(json)
        self.value = Reflect.field(json,apptimize_filter_ABTFilter.kABTFilterKeyValue)

    def filterMatchesEnvironment(self,env):
        if (not self.hasSupportedProperty(env)):
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        currentValue = self.currentDeviceValue(env)
        filterValue = self.value
        if ((currentValue is None) or ((filterValue is None))):
            apptimize_ABTLogger.w("Filter has null value type. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 329, 'className': "apptimize.filter.ABTSimpleFilter", 'methodName': "filterMatchesEnvironment"}))
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        if (Type.getClass(currentValue) == str):
            if ((Type.typeof(filterValue) == ValueType.TFloat) or ((Type.typeof(filterValue) == ValueType.TInt))):
                return apptimize_filter_ABTFilterUtils.ABTEvaluateNumber(currentValue,self.filterOperator,filterValue)
            if (Type.getClass(filterValue) != str):
                apptimize_ABTLogger.w("Filter value does not match property type of string. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 340, 'className': "apptimize.filter.ABTSimpleFilter", 'methodName': "filterMatchesEnvironment"}))
                return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
            if ((((self.property == "apptimize_version") or ((self.property == "system_version"))) or ((self.property == "app_version"))) or ((self.property == "operating_system_version"))):
                return apptimize_filter_ABTFilterUtils.ABTEvaluateVersionString(currentValue,self.filterOperator,filterValue)
            return apptimize_filter_ABTFilterUtils.ABTEvaluateString(currentValue,self.filterOperator,filterValue)
        if ((Type.typeof(currentValue) == ValueType.TFloat) or ((Type.typeof(currentValue) == ValueType.TInt))):
            if (Type.getClass(filterValue) == str):
                return apptimize_filter_ABTFilterUtils.ABTEvaluateNumber(currentValue,self.filterOperator,filterValue)
            if ((Type.typeof(filterValue) != ValueType.TFloat) and ((Type.typeof(filterValue) != ValueType.TInt))):
                apptimize_ABTLogger.w("Filter value does not match property type of number. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 358, 'className': "apptimize.filter.ABTSimpleFilter", 'methodName': "filterMatchesEnvironment"}))
                return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
            return apptimize_filter_ABTFilterUtils.ABTEvaluateNumber(currentValue,self.filterOperator,filterValue)
        if (Type.typeof(currentValue) == ValueType.TBool):
            if (Type.getClass(filterValue) == str):
                if (Reflect.field(filterValue,"toLowerCase")() == "true"):
                    filterValue = True
                elif (Reflect.field(filterValue,"toLowerCase")() == "false"):
                    filterValue = False
            return apptimize_filter_ABTFilterUtils.ABTEvaluateBool(currentValue,self.filterOperator,filterValue)
        apptimize_ABTLogger.w("Simple filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 378, 'className': "apptimize.filter.ABTSimpleFilter", 'methodName': "filterMatchesEnvironment"}))
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_filter_ABTSimpleFilter._hx_class = apptimize_filter_ABTSimpleFilter
_hx_classes["apptimize.filter.ABTSimpleFilter"] = apptimize_filter_ABTSimpleFilter


class apptimize_filter_ABTCompoundFilter(apptimize_filter_ABTFilter):
    _hx_class_name = "apptimize.filter.ABTCompoundFilter"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["fromJSON", "filterMatchesEnvironment", "getUrlKeys"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilter


    def __init__(self):
        super().__init__()

    def fromJSON(self,json):
        super().fromJSON(json)
        filtersArray = list()
        dynamicArray = Reflect.field(json,"value")
        _g = 0
        while (_g < len(dynamicArray)):
            _hx_filter = (dynamicArray[_g] if _g >= 0 and _g < len(dynamicArray) else None)
            _g = (_g + 1)
            ff = apptimize_filter_ABTFilter.filterFromJSON(_hx_filter)
            filtersArray.append(ff)
        self.value = filtersArray

    def filterMatchesEnvironment(self,env):
        children = self.value
        if (len(children) < 1):
            apptimize_ABTLogger.w((("Compound filter \"" + Std.string(self)) + "\" has an empty compound set. Filter match is unknown."),_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 407, 'className': "apptimize.filter.ABTCompoundFilter", 'methodName': "filterMatchesEnvironment"}))
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        if (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundAnd):
            result = apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            _g = 0
            while (_g < len(children)):
                _hx_filter = (children[_g] if _g >= 0 and _g < len(children) else None)
                _g = (_g + 1)
                currentResult = _hx_filter.filterMatchesEnvironment(env)
                result = apptimize_filter_ABTFilterUtils.ABTFilterAnd(result,currentResult)
            return result
        if (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundOr):
            result = apptimize_filter_ABTFilterResult.ABTFilterResultFalse
            _g = 0
            while (_g < len(children)):
                _hx_filter = (children[_g] if _g >= 0 and _g < len(children) else None)
                _g = (_g + 1)
                currentResult = _hx_filter.filterMatchesEnvironment(env)
                result = apptimize_filter_ABTFilterUtils.ABTFilterOr(result,currentResult)
            return result
        if ((self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundSingleNot) and ((len(children) == 1))):
            child = (children[0] if 0 < len(children) else None)
            result = child.filterMatchesEnvironment(env)
            if (result == apptimize_filter_ABTFilterResult.ABTFilterResultFalse):
                result = apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            elif (result == apptimize_filter_ABTFilterResult.ABTFilterResultTrue):
                result = apptimize_filter_ABTFilterResult.ABTFilterResultFalse
            return result
        if ((self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundSingleIsNull) and ((len(children) == 1))):
            child = (children[0] if 0 < len(children) else None)
            result = (apptimize_filter_ABTFilterResult.ABTFilterResultTrue if ((child.filterMatchesEnvironment(env) == apptimize_filter_ABTFilterResult.ABTFilterResultUnknown)) else apptimize_filter_ABTFilterResult.ABTFilterResultFalse)
            return result
        if ((self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorCompoundSingleIsNotNull) and ((len(children) == 1))):
            child = (children[0] if 0 < len(children) else None)
            if (child.filterMatchesEnvironment(env) != apptimize_filter_ABTFilterResult.ABTFilterResultUnknown):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        apptimize_ABTLogger.w((("Filter \"" + Std.string(self)) + "\" has an unsupported compound operator or children count. Filter match is unknown."),_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 463, 'className': "apptimize.filter.ABTCompoundFilter", 'methodName': "filterMatchesEnvironment"}))
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown

    def getUrlKeys(self):
        children = self.value
        _g = []
        _g_current = 0
        _g_array = children
        while (_g_current < len(_g_array)):
            x = _g_current
            _g_current = (_g_current + 1)
            x1 = (_g_array[x] if x >= 0 and x < len(_g_array) else None)
            x2 = x1.getUrlKeys()
            _g.append(x2)
        _g1 = []
        e = HxOverrides.iterator(_g)
        while e.hasNext():
            e1 = e.next()
            x = HxOverrides.iterator(e1)
            while x.hasNext():
                x1 = x.next()
                _g1.append(x1)
        childUrls = Lambda.array(_g1)
        if (self.callServerURLKey is None):
            return childUrls
        return ([self.callServerURLKey] + childUrls)

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_filter_ABTCompoundFilter._hx_class = apptimize_filter_ABTCompoundFilter
_hx_classes["apptimize.filter.ABTCompoundFilter"] = apptimize_filter_ABTCompoundFilter


class apptimize_filter_ABTListFilter(apptimize_filter_ABTFilter):
    _hx_class_name = "apptimize.filter.ABTListFilter"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["fromJSON", "filterMatchesEnvironment"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilter


    def __init__(self):
        super().__init__()

    def fromJSON(self,json):
        super().fromJSON(json)
        self.value = Reflect.field(json,"value")

    def filterMatchesEnvironment(self,env):
        if (not self.hasSupportedProperty(env)):
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        children = self.value
        currentValue = self.currentDeviceValue(env)
        if (currentValue is None):
            apptimize_ABTLogger.w((("Filter \"" + Std.string(self)) + "\" is attempting to match against a null device property."),_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 502, 'className': "apptimize.filter.ABTListFilter", 'methodName': "filterMatchesEnvironment"}))
            if (python_internal_ArrayImpl.indexOf(children,currentValue,None) > -1):
                if (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorInList):
                    return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
                else:
                    return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
            elif (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorInList):
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
        inList = False
        _g = 0
        while (_g < len(children)):
            childValue = (children[_g] if _g >= 0 and _g < len(children) else None)
            _g = (_g + 1)
            if (Type.getClass(currentValue) == str):
                inList = (inList or ((apptimize_filter_ABTFilterUtils.ABTEvaluateString(currentValue,apptimize_filter_ABTFilterOperator.ABTFilterOperatorEquals,childValue) == apptimize_filter_ABTFilterResult.ABTFilterResultTrue)))
            else:
                inList = (inList or ((apptimize_filter_ABTFilterUtils.ABTEvaluateNumber(currentValue,apptimize_filter_ABTFilterOperator.ABTFilterOperatorEquals,childValue) == apptimize_filter_ABTFilterResult.ABTFilterResultTrue)))
        if (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotInList):
            if (not inList):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if inList:
            return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
        else:
            return apptimize_filter_ABTFilterResult.ABTFilterResultFalse

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_filter_ABTListFilter._hx_class = apptimize_filter_ABTListFilter
_hx_classes["apptimize.filter.ABTListFilter"] = apptimize_filter_ABTListFilter


class apptimize_filter_ABTSetFilter(apptimize_filter_ABTFilter):
    _hx_class_name = "apptimize.filter.ABTSetFilter"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["fromJSON", "filterMatchesEnvironment"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilter


    def __init__(self):
        super().__init__()

    def fromJSON(self,json):
        super().fromJSON(json)
        values = list()
        dynamicArray = Reflect.field(json,"value")
        _g = 0
        while (_g < len(dynamicArray)):
            val = (dynamicArray[_g] if _g >= 0 and _g < len(dynamicArray) else None)
            _g = (_g + 1)
            values.append(val)
        self.value = values

    def filterMatchesEnvironment(self,env):
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_filter_ABTSetFilter._hx_class = apptimize_filter_ABTSetFilter
_hx_classes["apptimize.filter.ABTSetFilter"] = apptimize_filter_ABTSetFilter


class apptimize_filter_ABTUnknownFilter(apptimize_filter_ABTFilter):
    _hx_class_name = "apptimize.filter.ABTUnknownFilter"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["fromJSON", "filterMatchesEnvironment"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilter


    def __init__(self):
        super().__init__()

    def fromJSON(self,json):
        super().fromJSON(json)

    def filterMatchesEnvironment(self,env):
        apptimize_ABTLogger.e("Unknown filter requested. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 600, 'className': "apptimize.filter.ABTUnknownFilter", 'methodName': "filterMatchesEnvironment"}))
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_filter_ABTUnknownFilter._hx_class = apptimize_filter_ABTUnknownFilter
_hx_classes["apptimize.filter.ABTUnknownFilter"] = apptimize_filter_ABTUnknownFilter


class apptimize_filter_ABTPropertylessFilter(apptimize_filter_ABTFilter):
    _hx_class_name = "apptimize.filter.ABTPropertylessFilter"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["fromJSON", "filterMatchesEnvironment"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilter


    def __init__(self):
        super().__init__()

    def fromJSON(self,json):
        super().fromJSON(json)
        self.value = Reflect.field(json,apptimize_filter_ABTFilter.kABTFilterKeyValue)

    def filterMatchesEnvironment(self,env):
        filterValue = self.value
        if ((filterValue is None) or ((Type.getClass(filterValue) != str))):
            apptimize_ABTLogger.w("Property-less filter requires a string value. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 620, 'className': "apptimize.filter.ABTPropertylessFilter", 'methodName': "filterMatchesEnvironment"}))
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        filterString = filterValue
        if (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsNull):
            currentValue = env.valueForProperty(filterString,apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourceDevice)
            if (currentValue is None):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsNotNull):
            currentValue = env.valueForProperty(filterString,apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourceDevice)
            if (currentValue is not None):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsRecognized):
            if (self.isSupportedProperty(env,filterString,apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourceDevice) == True):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorPropertyIsNotRecognized):
            if (self.isSupportedProperty(env,filterString,apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourceDevice) == False):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorOperatorIsRecognized):
            if (self.isSupportedOperator(filterString) == True):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (self.filterOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorOperatorIsNotRecognized):
            if (self.isSupportedOperator(filterString) == False):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        apptimize_ABTLogger.w("Property-less filter attempted with an invalid operator. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 652, 'className': "apptimize.filter.ABTPropertylessFilter", 'methodName': "filterMatchesEnvironment"}))
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_filter_ABTPropertylessFilter._hx_class = apptimize_filter_ABTPropertylessFilter
_hx_classes["apptimize.filter.ABTPropertylessFilter"] = apptimize_filter_ABTPropertylessFilter


class apptimize_filter_ABTNamedFilter(apptimize_filter_ABTFilter):
    _hx_class_name = "apptimize.filter.ABTNamedFilter"
    __slots__ = ("namedFilter",)
    _hx_fields = ["namedFilter"]
    _hx_methods = ["fromJSON", "filterMatchesEnvironment"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilter


    def __init__(self):
        self.namedFilter = None
        super().__init__()

    def fromJSON(self,json):
        super().fromJSON(json)
        self.namedFilter = Reflect.field(json,apptimize_filter_ABTFilter.kABTFilterKeyNamedFilter)

    def filterMatchesEnvironment(self,env):
        apptimize_ABTLogger.e("Named filter not implemented. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 668, 'className': "apptimize.filter.ABTNamedFilter", 'methodName': "filterMatchesEnvironment"}))
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.namedFilter = None
apptimize_filter_ABTNamedFilter._hx_class = apptimize_filter_ABTNamedFilter
_hx_classes["apptimize.filter.ABTNamedFilter"] = apptimize_filter_ABTNamedFilter


class apptimize_filter_ABTFilterUtils:
    _hx_class_name = "apptimize.filter.ABTFilterUtils"
    __slots__ = ()
    _hx_statics = ["__meta__", "ABTFilterAnd", "ABTFilterOr", "ABTEvaluateString", "ABTEvaluateBool", "ABTEvaluateNumber", "ABTEvaluateVersionString"]

    @staticmethod
    def ABTFilterAnd(left,right):
        if ((left == apptimize_filter_ABTFilterResult.ABTFilterResultTrue) and ((right == apptimize_filter_ABTFilterResult.ABTFilterResultUnknown))):
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        if ((left == apptimize_filter_ABTFilterResult.ABTFilterResultTrue) and ((right == apptimize_filter_ABTFilterResult.ABTFilterResultFalse))):
            return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if ((left == apptimize_filter_ABTFilterResult.ABTFilterResultUnknown) and ((right == apptimize_filter_ABTFilterResult.ABTFilterResultFalse))):
            return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        return left

    @staticmethod
    def ABTFilterOr(left,right):
        if ((left == apptimize_filter_ABTFilterResult.ABTFilterResultUnknown) and ((right == apptimize_filter_ABTFilterResult.ABTFilterResultFalse))):
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        if ((left == apptimize_filter_ABTFilterResult.ABTFilterResultTrue) and ((right == apptimize_filter_ABTFilterResult.ABTFilterResultFalse))):
            return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
        if ((left == apptimize_filter_ABTFilterResult.ABTFilterResultTrue) and ((right == apptimize_filter_ABTFilterResult.ABTFilterResultUnknown))):
            return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
        return right

    @staticmethod
    def ABTEvaluateString(left,abtOperator,right):
        leftString = ""
        rightString = ""
        if ((left is None) or ((right is None))):
            apptimize_ABTLogger.w("String comparison attempted with null string. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 707, 'className': "apptimize.filter.ABTFilterUtils", 'methodName': "ABTEvaluateString"}))
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        if (Type.getClass(left) == str):
            leftString = left
        if (Type.getClass(right) == str):
            rightString = right
        leftString = leftString.lower()
        rightString = rightString.lower()
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorEquals):
            if (leftString == rightString):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotEquals):
            if (leftString != rightString):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        apptimize_ABTLogger.w("String comparison attempted with an invalid operator. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 727, 'className': "apptimize.filter.ABTFilterUtils", 'methodName': "ABTEvaluateString"}))
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown

    @staticmethod
    def ABTEvaluateBool(left,abtOperator,right):
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorEquals):
            if (left == right):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotEquals):
            if (left != right):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        apptimize_ABTLogger.w("Bool comparison attempted with an invalid operator. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 736, 'className': "apptimize.filter.ABTFilterUtils", 'methodName': "ABTEvaluateBool"}))
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown

    @staticmethod
    def ABTEvaluateNumber(left,abtOperator,right):
        leftFloat = None
        rightFloat = None
        if ((left is None) or ((right is None))):
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        if (Type.getClass(left) == str):
            leftFloat = Std.parseFloat(left)
        else:
            leftFloat = left
        if (Type.getClass(right) == str):
            rightFloat = Std.parseFloat(right)
        else:
            rightFloat = right
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorEquals):
            if (leftFloat == rightFloat):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotEquals):
            if (leftFloat != rightFloat):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorGreaterThan):
            if (leftFloat > rightFloat):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorGreaterThanOrEqual):
            if (leftFloat >= rightFloat):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorLessThan):
            if (leftFloat < rightFloat):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorLessThanOrEqual):
            if (leftFloat <= rightFloat):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        apptimize_ABTLogger.w("Number comparison attempted with an invalid operator. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 768, 'className': "apptimize.filter.ABTFilterUtils", 'methodName': "ABTEvaluateNumber"}))
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown

    @staticmethod
    def ABTEvaluateVersionString(left,abtOperator,right):
        if ((left is None) or ((left == ""))):
            left = "0"
        if ((right is None) or ((right == ""))):
            right = "0"
        if ((Type.getClass(left) != str) or ((Type.getClass(right) != str))):
            apptimize_ABTLogger.w("Unable to compare versions as values are not strings. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 786, 'className': "apptimize.filter.ABTFilterUtils", 'methodName': "ABTEvaluateVersionString"}))
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        leftString = left
        rightString = right
        leftComponents = leftString.split(".")
        rightComponents = rightString.split(".")
        leftLength = len(leftComponents)
        if (leftLength < 3):
            _g = leftLength
            _g1 = 3
            while (_g < _g1):
                i = _g
                _g = (_g + 1)
                leftComponents.append("0")
        rightLength = len(rightComponents)
        if (rightLength < 3):
            _g = rightLength
            _g1 = 3
            while (_g < _g1):
                i = _g
                _g = (_g + 1)
                rightComponents.append("0")
        leftString = ".".join([python_Boot.toString1(x1,'') for x1 in leftComponents])
        rightString = ".".join([python_Boot.toString1(x1,'') for x1 in rightComponents])
        leftVersion = None
        rightVersion = None
        try:
            leftVersion = thx_semver__Version_Version_Impl_.stringToVersion(leftString)
        except BaseException as _g:
            None
            apptimize_ABTLogger.w((("Unable to validate left (current) version: " + ("null" if leftString is None else leftString)) + ". Filter match is unknown."),_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 826, 'className': "apptimize.filter.ABTFilterUtils", 'methodName': "ABTEvaluateVersionString"}))
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        try:
            rightVersion = thx_semver__Version_Version_Impl_.stringToVersion(rightString)
        except BaseException as _g:
            None
            apptimize_ABTLogger.w((("Unable to validate right (filter) version: " + ("null" if rightString is None else rightString)) + ". Filter match is unknown."),_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 832, 'className': "apptimize.filter.ABTFilterUtils", 'methodName': "ABTEvaluateVersionString"}))
            return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorEquals):
            if thx_semver__Version_Version_Impl_.equals(leftVersion,rightVersion):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorNotEquals):
            if (not thx_semver__Version_Version_Impl_.equals(leftVersion,rightVersion)):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorGreaterThan):
            if thx_semver__Version_Version_Impl_.greaterThan(leftVersion,rightVersion):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorGreaterThanOrEqual):
            if thx_semver__Version_Version_Impl_.greaterThanOrEqual(leftVersion,rightVersion):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorLessThan):
            if thx_semver__Version_Version_Impl_.lessThan(leftVersion,rightVersion):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        if (abtOperator == apptimize_filter_ABTFilterOperator.ABTFilterOperatorLessThanOrEqual):
            if thx_semver__Version_Version_Impl_.lessThanOrEqual(leftVersion,rightVersion):
                return apptimize_filter_ABTFilterResult.ABTFilterResultTrue
            else:
                return apptimize_filter_ABTFilterResult.ABTFilterResultFalse
        apptimize_ABTLogger.w("Version comparison attempted with an invalid operator. Filter match is unknown.",_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilter.hx", 'lineNumber': 844, 'className': "apptimize.filter.ABTFilterUtils", 'methodName': "ABTEvaluateVersionString"}))
        return apptimize_filter_ABTFilterResult.ABTFilterResultUnknown
apptimize_filter_ABTFilterUtils._hx_class = apptimize_filter_ABTFilterUtils
_hx_classes["apptimize.filter.ABTFilterUtils"] = apptimize_filter_ABTFilterUtils


class apptimize_filter_ABTFilterEnvParams:
    _hx_class_name = "apptimize.filter.ABTFilterEnvParams"
    __slots__ = ("userID", "anonID", "customAttrs", "appProps", "appkey")
    _hx_fields = ["userID", "anonID", "customAttrs", "appProps", "appkey"]

    def __init__(self,userId,anonId,customAttrs,appkey,appProps):
        self.userID = userId
        self.anonID = anonId
        self.customAttrs = customAttrs
        self.appkey = appkey
        self.appProps = appProps

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.userID = None
        _hx_o.anonID = None
        _hx_o.customAttrs = None
        _hx_o.appProps = None
        _hx_o.appkey = None
apptimize_filter_ABTFilterEnvParams._hx_class = apptimize_filter_ABTFilterEnvParams
_hx_classes["apptimize.filter.ABTFilterEnvParams"] = apptimize_filter_ABTFilterEnvParams


class apptimize_filter_ABTFilterEnvironment:
    _hx_class_name = "apptimize.filter.ABTFilterEnvironment"
    __slots__ = ("userID", "anonID", "customProperties", "applicationProperties", "sequenceNumber", "appkey", "secondaryValueUrlTemplates", "secondaryValueLists")
    _hx_fields = ["userID", "anonID", "customProperties", "applicationProperties", "sequenceNumber", "appkey", "secondaryValueUrlTemplates", "secondaryValueLists"]
    _hx_methods = ["getUniqueUserID", "getUserOrAnonID", "valueForProperty", "secondaryUrlForKey", "injectPropsInUrlTemplate"]

    def __init__(self,params,urlTemplates,valueLists,sequenceNumber):
        self.userID = params.userID
        self.anonID = params.anonID
        self.customProperties = apptimize_support_properties_ABTCustomProperties()
        self.secondaryValueUrlTemplates = urlTemplates
        self.secondaryValueLists = valueLists
        self.applicationProperties = params.appProps
        self.appkey = params.appkey
        self.sequenceNumber = sequenceNumber
        if (params.customAttrs is not None):
            self.customProperties.setProperties(params.customAttrs)
        self.customProperties.setPropertyForNamespace("app_key",params.appkey,apptimize_support_properties_CustomPropertyNamespace.ApptimizeLocal)

    def getUniqueUserID(self):
        return ((HxOverrides.stringOrNull(self.appkey) + "_") + HxOverrides.stringOrNull(self.getUserOrAnonID()))

    def getUserOrAnonID(self):
        if (self.userID is not None):
            return self.userID
        return self.anonID

    def valueForProperty(self,property,source):
        if (source == apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourceDevice):
            return self.applicationProperties.valueForProperty(property)
        if (source == apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourceUser):
            return self.customProperties.valueForNamespacedProperty(property,apptimize_support_properties_CustomPropertyNamespace.UserAttribute)
        if (source == apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourcePrefixed):
            value = self.customProperties.valueForProperty(property)
            return value
        return None

    def secondaryUrlForKey(self,key):
        if ((key is None) or ((key == ""))):
            return None
        urlTemplate = self.secondaryValueUrlTemplates.h.get(key,None)
        if (urlTemplate is None):
            apptimize_ABTLogger.e(("unknown secondary url key " + ("null" if key is None else key)),_hx_AnonObject({'fileName': "src/apptimize/filter/ABTFilterEnvironment.hx", 'lineNumber': 114, 'className': "apptimize.filter.ABTFilterEnvironment", 'methodName': "secondaryUrlForKey"}))
            return None
        url = self.injectPropsInUrlTemplate(urlTemplate)
        if (url is None):
            return None
        paramSep = "&"
        startIndex = None
        if (((url.find("?") if ((startIndex is None)) else HxString.indexOfImpl(url,"?",startIndex))) == -1):
            paramSep = "?"
        fullUrl = (((("" + ("null" if url is None else url)) + ("null" if paramSep is None else paramSep)) + "metadataSequenceNumber=") + Std.string(self.sequenceNumber))
        return fullUrl

    def injectPropsInUrlTemplate(self,template):
        _gthis = self
        regex = EReg("\\{([^}]+)}","g")
        missingSome = False
        def _hx_local_0(subregex):
            nonlocal missingSome
            key = subregex.matchObj.group(1)
            value = _gthis.valueForProperty(key,apptimize_filter_ABTFilterPropertySource.ABTFilterPropertySourcePrefixed)
            if (value is None):
                missingSome = True
                return (("<MISSING:" + ("null" if key is None else key)) + "}>")
            else:
                return python_lib_urllib_Parse.quote(value,"")
        mapped = regex.map(template,_hx_local_0)
        if missingSome:
            return None
        return mapped

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.userID = None
        _hx_o.anonID = None
        _hx_o.customProperties = None
        _hx_o.applicationProperties = None
        _hx_o.sequenceNumber = None
        _hx_o.appkey = None
        _hx_o.secondaryValueUrlTemplates = None
        _hx_o.secondaryValueLists = None
apptimize_filter_ABTFilterEnvironment._hx_class = apptimize_filter_ABTFilterEnvironment
_hx_classes["apptimize.filter.ABTFilterEnvironment"] = apptimize_filter_ABTFilterEnvironment


class apptimize_filter_ABTFilterableObject:
    _hx_class_name = "apptimize.filter.ABTFilterableObject"
    __slots__ = ("filters", "filters2", "overridingInclusiveFilters", "matchingFilters", "nonMatchingFilters")
    _hx_fields = ["filters", "filters2", "overridingInclusiveFilters", "matchingFilters", "nonMatchingFilters"]
    _hx_methods = ["initialize", "performFilterMatchingWithEnvironment", "computeNewOverrideState", "fromJSON", "jsonToFilterArray", "getUrlKeys", "getUrlKeyProviders", "getUrlKeysFrom", "getLocalUrlKeys", "asUrlProviders"]

    def __init__(self):
        self.nonMatchingFilters = None
        self.matchingFilters = None
        self.overridingInclusiveFilters = None
        self.filters2 = None
        self.filters = None
        self.initialize()

    def initialize(self):
        self.filters = list()
        self.filters2 = list()
        self.matchingFilters = list()
        self.nonMatchingFilters = list()
        self.overridingInclusiveFilters = list()

    def performFilterMatchingWithEnvironment(self,env):
        ret = _hx_AnonObject({'result': apptimize_filter_ABTFilterResult.ABTFilterResultTrue, 'overriding': False})
        _g = 0
        _g1 = self.filters
        while (_g < len(_g1)):
            _hx_filter = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            match = _hx_filter.filterMatchesEnvironment(env)
            ret.result = apptimize_filter_ABTFilterUtils.ABTFilterAnd(ret.result,match)
        _g = 0
        _g1 = self.overridingInclusiveFilters
        while (_g < len(_g1)):
            _hx_filter = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            match = _hx_filter.filterMatchesEnvironment(env)
            if (match == apptimize_filter_ABTFilterResult.ABTFilterResultTrue):
                ret.result = apptimize_filter_ABTFilterResult.ABTFilterResultTrue
                ret.overriding = True
        return ret

    def computeNewOverrideState(self,wasOverrideOnly,matchResult):
        if wasOverrideOnly:
            if matchResult.overriding:
                return False
        elif (matchResult.result != apptimize_filter_ABTFilterResult.ABTFilterResultTrue):
            return True
        return wasOverrideOnly

    def fromJSON(self,json):
        self.filters = self.jsonToFilterArray(Reflect.field(json,"filters"))
        self.filters2 = self.jsonToFilterArray(Reflect.field(json,"filters2"))
        self.overridingInclusiveFilters = self.jsonToFilterArray(Reflect.field(json,"overridingInclusiveFilters"))
        if (len(self.filters2) > 0):
            self.filters = (self.filters + self.filters2)

    def jsonToFilterArray(self,input):
        filterArray = (list() if ((input is None)) else input)
        def _hx_local_1():
            def _hx_local_0(_hx_filter):
                return apptimize_filter_ABTFilter.filterFromJSON(_hx_filter)
            return list(map(_hx_local_0,filterArray))
        return _hx_local_1()

    def getUrlKeys(self):
        return (self.getLocalUrlKeys() + self.getUrlKeysFrom(self.getUrlKeyProviders()))

    def getUrlKeyProviders(self):
        return []

    def getUrlKeysFrom(self,items):
        _g = []
        _g_current = 0
        _g_array = items
        while (_g_current < len(_g_array)):
            x = _g_current
            _g_current = (_g_current + 1)
            x1 = (_g_array[x] if x >= 0 and x < len(_g_array) else None)
            x2 = x1.getUrlKeys()
            _g.append(x2)
        _g1 = []
        e = HxOverrides.iterator(_g)
        while e.hasNext():
            e1 = e.next()
            x = HxOverrides.iterator(e1)
            while x.hasNext():
                x1 = x.next()
                _g1.append(x1)
        return Lambda.array(_g1)

    def getLocalUrlKeys(self):
        return (self.getUrlKeysFrom(self.filters) + self.getUrlKeysFrom(self.overridingInclusiveFilters))

    def asUrlProviders(self,items):
        def _hx_local_1():
            def _hx_local_0(item):
                return item
            return list(map(_hx_local_0,items))
        return _hx_local_1()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.filters = None
        _hx_o.filters2 = None
        _hx_o.overridingInclusiveFilters = None
        _hx_o.matchingFilters = None
        _hx_o.nonMatchingFilters = None
apptimize_filter_ABTFilterableObject._hx_class = apptimize_filter_ABTFilterableObject
_hx_classes["apptimize.filter.ABTFilterableObject"] = apptimize_filter_ABTFilterableObject


class apptimize_http_ABTHttpResponse:
    _hx_class_name = "apptimize.http.ABTHttpResponse"
    __slots__ = ("bytes", "text", "responseCode", "etag")
    _hx_fields = ["bytes", "text", "responseCode", "etag"]
    _hx_methods = ["isSuccess"]

    def __init__(self):
        self.etag = None
        self.responseCode = -1
        self.text = ""
        self.bytes = None

    def isSuccess(self):
        if (self.responseCode != 200):
            return (self.responseCode == 304)
        else:
            return True

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.bytes = None
        _hx_o.text = None
        _hx_o.responseCode = None
        _hx_o.etag = None
apptimize_http_ABTHttpResponse._hx_class = apptimize_http_ABTHttpResponse
_hx_classes["apptimize.http.ABTHttpResponse"] = apptimize_http_ABTHttpResponse


class apptimize_http_ABTHttpRequestInterface:
    _hx_class_name = "apptimize.http.ABTHttpRequestInterface"
    __slots__ = ()
    _hx_methods = ["get", "post"]
apptimize_http_ABTHttpRequestInterface._hx_class = apptimize_http_ABTHttpRequestInterface
_hx_classes["apptimize.http.ABTHttpRequestInterface"] = apptimize_http_ABTHttpRequestInterface


class apptimize_http_ABTHttpRequest:
    _hx_class_name = "apptimize.http.ABTHttpRequest"
    __slots__ = ()
    _hx_statics = ["getRequestInterface", "getRealRequestInterface", "get", "post"]

    @staticmethod
    def getRequestInterface():
        return apptimize_http_ABTHttpRequest.getRealRequestInterface()

    @staticmethod
    def getRealRequestInterface():
        return apptimize_http_ABTHttpRequestPython()

    @staticmethod
    def get(url,requestHeaders,successCallback,failureCallback):
        requestInterface = apptimize_http_ABTHttpRequest.getRequestInterface()
        requestInterface.get(url,requestHeaders,successCallback,failureCallback)

    @staticmethod
    def post(url,data,appKey,successCallback,failureCallback):
        requestInterface = apptimize_http_ABTHttpRequest.getRequestInterface()
        requestInterface.post(url,data,appKey,successCallback,failureCallback)
apptimize_http_ABTHttpRequest._hx_class = apptimize_http_ABTHttpRequest
_hx_classes["apptimize.http.ABTHttpRequest"] = apptimize_http_ABTHttpRequest


class apptimize_http_ABTHttpRequestPython:
    _hx_class_name = "apptimize.http.ABTHttpRequestPython"
    __slots__ = ("_successCallback", "_failureCallback")
    _hx_fields = ["_successCallback", "_failureCallback"]
    _hx_methods = ["get", "processGetResponse", "post", "processPostResponse"]
    _hx_interfaces = [apptimize_http_ABTHttpRequestInterface]

    def __init__(self):
        self._failureCallback = None
        self._successCallback = None

    def get(self,url,requestHeaders,successCallback,failureCallback):
        isThreaded = apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.THREADING_ENABLED_KEY)
        self._successCallback = successCallback
        self._failureCallback = failureCallback
        headers = apptimize_util_ABTUtilDictionary.stringMapToNativeDictionary(requestHeaders)
        if isThreaded:
            s = apptimize_native_python_Session()
            Reflect.field(s.headers,"update")(headers)
            session = apptimize_native_python_FuturesSession(**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'session': s})))
            session.get(url,**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'background_callback': self.processGetResponse})))
        else:
            try:
                resp = apptimize_native_python_Requests.get(url,**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'headers': headers})))
                self.processGetResponse(None,resp)
            except BaseException as _g:
                None
                exception = haxe_Exception.caught(_g).unwrap()
                response = apptimize_http_ABTHttpResponse()
                response.text = (("Failed to download with GET request with exception: \"" + Std.string(exception)) + "\".")
                self._failureCallback(response)

    def processGetResponse(self,session,response):
        httpResponse = apptimize_http_ABTHttpResponse()
        httpResponse.bytes = Reflect.field(response,"content")
        httpResponse.responseCode = Reflect.field(response,"status_code")
        responseHeaders = Reflect.field(response,"headers")
        httpResponse.etag = responseHeaders.get("etag")
        if httpResponse.isSuccess():
            self._successCallback(httpResponse)
        else:
            self._failureCallback(httpResponse)

    def post(self,url,data,appKey,successCallback,failureCallback):
        isThreaded = apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.THREADING_ENABLED_KEY)
        headers = dict()
        headers["X-App-Key"] = appKey
        headers["Content-Type"] = "application/json; charset=UTF-8"
        self._successCallback = successCallback
        self._failureCallback = failureCallback
        if isThreaded:
            s = apptimize_native_python_Session()
            Reflect.field(s.headers,"update")(headers)
            session = apptimize_native_python_FuturesSession(**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'session': s})))
            session.post(url,data.b,None,**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'background_callback': self.processPostResponse})))
        else:
            try:
                resp = apptimize_native_python_Requests.post(url,data.b,None,**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'headers': headers})))
                self.processPostResponse(None,resp)
            except BaseException as _g:
                None
                exception = haxe_Exception.caught(_g).unwrap()
                response = apptimize_http_ABTHttpResponse()
                response.text = (((("Failed to POST to url  \"" + ("null" if url is None else url)) + "\" with exception: ") + Std.string(exception)) + ".")
                self._failureCallback(response)

    def processPostResponse(self,session,response):
        httpResponse = apptimize_http_ABTHttpResponse()
        httpResponse.text = Reflect.field(response,"text")
        httpResponse.responseCode = Reflect.field(response,"status_code")
        if httpResponse.isSuccess():
            self._successCallback(httpResponse)
        else:
            self._failureCallback(httpResponse)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._successCallback = None
        _hx_o._failureCallback = None
apptimize_http_ABTHttpRequestPython._hx_class = apptimize_http_ABTHttpRequestPython
_hx_classes["apptimize.http.ABTHttpRequestPython"] = apptimize_http_ABTHttpRequestPython


class apptimize_models_ABTAlteration(apptimize_filter_ABTFilterableObject):
    _hx_class_name = "apptimize.models.ABTAlteration"
    __slots__ = ("_variant", "_key")
    _hx_fields = ["_variant", "_key"]
    _hx_methods = ["fromJSON", "selectAlterationsIntoArray", "getKey", "getVariant"]
    _hx_statics = ["alterationFromJSON", "classForType"]
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilterableObject


    def __init__(self):
        self._key = None
        self._variant = None
        super().__init__()

    def fromJSON(self,json):
        super().fromJSON(json)

    def selectAlterationsIntoArray(self,env,target,overrideOnly):
        match = self.performFilterMatchingWithEnvironment(env)
        canSelect = (match.overriding or (not overrideOnly))
        selected = (canSelect and ((match.result == apptimize_filter_ABTFilterResult.ABTFilterResultTrue)))
        if selected:
            apptimize_ABTLogger.v((((((("Selecting alteration \"" + HxOverrides.stringOrNull(self.getKey())) + "\" for variant \"") + HxOverrides.stringOrNull(self.getVariant().getVariantName())) + "\" for user ") + HxOverrides.stringOrNull(env.getUserOrAnonID())) + "."),_hx_AnonObject({'fileName': "src/apptimize/models/ABTAlteration.hx", 'lineNumber': 50, 'className': "apptimize.models.ABTAlteration", 'methodName': "selectAlterationsIntoArray"}))
            target.append(self)

    def getKey(self):
        return self._key

    def getVariant(self):
        return self._variant

    @staticmethod
    def alterationFromJSON(json,variant):
        classType = apptimize_models_ABTAlteration.classForType(Reflect.field(json,"type"))
        instance = classType(*[])
        instance.initialize()
        instance.fromJSON(json)
        instance._variant = variant
        return instance

    @staticmethod
    def classForType(_hx_type):
        if ("block" == _hx_type):
            return apptimize_models_ABTBlockAlteration
        return apptimize_models_ABTValueAlteration

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._variant = None
        _hx_o._key = None
apptimize_models_ABTAlteration._hx_class = apptimize_models_ABTAlteration
_hx_classes["apptimize.models.ABTAlteration"] = apptimize_models_ABTAlteration


class apptimize_models_ABTBlockAlteration(apptimize_models_ABTAlteration):
    _hx_class_name = "apptimize.models.ABTBlockAlteration"
    __slots__ = ("methodName",)
    _hx_fields = ["methodName"]
    _hx_methods = ["fromJSON"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_ABTAlteration


    def __init__(self):
        self.methodName = None
        super().__init__()

    def fromJSON(self,json):
        super().fromJSON(json)
        self._key = Reflect.field(json,"key")
        self.methodName = Reflect.field(json,"methodName")

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.methodName = None
apptimize_models_ABTBlockAlteration._hx_class = apptimize_models_ABTBlockAlteration
_hx_classes["apptimize.models.ABTBlockAlteration"] = apptimize_models_ABTBlockAlteration


class apptimize_models_ABTValueAlteration(apptimize_models_ABTAlteration):
    _hx_class_name = "apptimize.models.ABTValueAlteration"
    __slots__ = ("_value", "_type", "_nestedType", "_useDefaultValue")
    _hx_fields = ["_value", "_type", "_nestedType", "_useDefaultValue"]
    _hx_methods = ["fromJSON", "useDefaultValue", "getValue", "getType", "getNestedType"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_ABTAlteration


    def __init__(self):
        self._useDefaultValue = None
        self._nestedType = None
        self._type = None
        self._value = None
        super().__init__()

    def fromJSON(self,json):
        super().fromJSON(json)
        self._key = Reflect.field(json,"key")
        self._value = Reflect.field(json,"value")
        self._type = Reflect.field(json,"type")
        self._nestedType = Reflect.field(json,"nestedType")
        self._useDefaultValue = Reflect.field(json,"useDefaultValue")
        if ((self._value is not None) and ((self._type == "dictionary"))):
            self._value = apptimize_util_ABTUtilDictionary.dynamicToNativeDictionary(self._value)

    def useDefaultValue(self):
        return self._useDefaultValue

    def getValue(self):
        return self._value

    def getType(self):
        return self._type

    def getNestedType(self):
        return self._nestedType

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._value = None
        _hx_o._type = None
        _hx_o._nestedType = None
        _hx_o._useDefaultValue = None
apptimize_models_ABTValueAlteration._hx_class = apptimize_models_ABTValueAlteration
_hx_classes["apptimize.models.ABTValueAlteration"] = apptimize_models_ABTValueAlteration


class apptimize_models_ABTJSONObject:
    _hx_class_name = "apptimize.models.ABTJSONObject"
    __slots__ = ()
apptimize_models_ABTJSONObject._hx_class = apptimize_models_ABTJSONObject
_hx_classes["apptimize.models.ABTJSONObject"] = apptimize_models_ABTJSONObject


class apptimize_models_ABTMetadata:
    _hx_class_name = "apptimize.models.ABTMetadata"
    __slots__ = ("_jsonData", "_seedGroups", "_hotfixes", "_alterationCache", "_etag", "_secondaryValues")
    _hx_fields = ["_jsonData", "_seedGroups", "_hotfixes", "_alterationCache", "_etag", "_secondaryValues"]
    _hx_methods = ["makeEnvironment", "getGroupsUrlTemplate", "_load_data", "reprocessJson", "uncachedSelectAlterationsIntoArray", "selectAlterationsIntoArray", "extractNeededSecondaryUrls", "extractSdkParameters", "metadataProcessed", "getVariantsCyclesPhases", "getMetaData", "getSequenceNumber", "getCheckinUrls", "getAppKey", "getEtag", "setEtag", "setSecondaryValues", "getSecondaryValues", "getDisabledVersions", "hxSerialize", "serializeV1", "hxUnserialize"]
    _hx_statics = ["loadFromString"]

    def __init__(self):
        self._secondaryValues = None
        self._etag = None
        self._hotfixes = None
        self._seedGroups = None
        self._jsonData = None
        self._alterationCache = apptimize_util_ABTLRUCache(apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.ALTERATION_CACHE_SIZE_KEY))

    def makeEnvironment(self,params):
        valueLists = self._secondaryValues
        _g = haxe_ds_StringMap()
        value = self.getGroupsUrlTemplate()
        _g.h["groupsApiUrl"] = value
        templates = _g
        return apptimize_filter_ABTFilterEnvironment(params,templates,valueLists,self.getSequenceNumber())

    def getGroupsUrlTemplate(self):
        groupsBaseUrl = apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY)
        groupsFullUrl = (("null" if groupsBaseUrl is None else groupsBaseUrl) + "/api/pilot-groups/?appKey={lapp_key}&pilotTargetingId={lpilot_targeting_id}")
        return groupsFullUrl

    def _load_data(self,content):
        self._alterationCache = apptimize_util_ABTLRUCache(apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.ALTERATION_CACHE_SIZE_KEY))
        self._jsonData = python_lib_Json.loads(content,**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'object_hook': python_Lib.dictToAnon})))
        self.reprocessJson()

    def reprocessJson(self):
        if (self._jsonData is None):
            raise haxe_Exception.thrown("Unable to process metadata")
        self._seedGroups = list()
        if (self._jsonData.seedGroups is not None):
            _g = 0
            _g1 = self._jsonData.seedGroups
            while (_g < len(_g1)):
                sg = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _this = self._seedGroups
                x = apptimize_models_ABTSeedGroup(sg)
                _this.append(x)
        self._hotfixes = list()
        if (self._jsonData.hotfixes is not None):
            _g = 0
            _g1 = self._jsonData.hotfixes
            while (_g < len(_g1)):
                hf = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _this = self._hotfixes
                x = apptimize_models_ABTHotfixVariant(hf)
                _this.append(x)

    def uncachedSelectAlterationsIntoArray(self,env,checkCache = None):
        if (checkCache is None):
            checkCache = True
        alterations = list()
        _g = 0
        _g1 = self._seedGroups
        while (_g < len(_g1)):
            seedgroup = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            seedgroup.selectAlterationsIntoArray(env,alterations,False)
        _g = 0
        _g1 = self._hotfixes
        while (_g < len(_g1)):
            hotfix = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            hotfix.selectAlterationsIntoArray(env,alterations,False)
        return alterations

    def selectAlterationsIntoArray(self,env):
        alterations = self.uncachedSelectAlterationsIntoArray(env,False)
        self.metadataProcessed(env,alterations)
        return alterations

    def extractNeededSecondaryUrls(self,env):
        keys = list()
        _g = 0
        _g1 = self._seedGroups
        while (_g < len(_g1)):
            seedgroup = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            keys = (keys + seedgroup.getUrlKeys())
        _g = 0
        _g1 = self._hotfixes
        while (_g < len(_g1)):
            hotfix = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            keys = (keys + hotfix.getUrlKeys())
        ret = list()
        _hx_map = haxe_ds_StringMap()
        _g = 0
        while (_g < len(keys)):
            key = (keys[_g] if _g >= 0 and _g < len(keys) else None)
            _g = (_g + 1)
            if (not (key in _hx_map.h)):
                value = env.secondaryUrlForKey(key)
                _hx_map.h[key] = value
                if (value is not None):
                    ret.append(value)
        return ret

    def extractSdkParameters(self,env):
        ret = apptimize_models_ABTSdkParameters(None)
        if (self._seedGroups is not None):
            _g = 0
            _g1 = self._seedGroups
            while (_g < len(_g1)):
                seedGroup = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                seedGroup.applySdkParameters(ret,env)
        return ret

    def metadataProcessed(self,env,alterations):
        metadataProcessedEntry = apptimize_models_results_ABTResultEntryMetadataProcessed(env,self.getSequenceNumber(),self.getVariantsCyclesPhases(alterations))
        apptimize_ABTDataStore.sharedInstance().addResultLogEntry(env,metadataProcessedEntry)

    def getVariantsCyclesPhases(self,alterations):
        variantsCyclesPhases = haxe_ds_IntMap()
        _g = 0
        while (_g < len(alterations)):
            alteration = (alterations[_g] if _g >= 0 and _g < len(alterations) else None)
            _g = (_g + 1)
            variant = alteration.getVariant()
            phase = variant.getPhase()
            variantStickyString = ((("v" + Std.string(variant.getVariantID())) + "_") + Std.string(variant.getCycle()))
            if ((Type.getClass(variant) != apptimize_models_ABTHotfixVariant) and (not (variant.getVariantID() in variantsCyclesPhases.h))):
                k = variant.getVariantID()
                v = _hx_AnonObject({'v': variant.getVariantID(), 'c': variant.getCycle(), 'p': phase})
                variantsCyclesPhases.set(k,v)
        return Lambda.array(variantsCyclesPhases)

    def getMetaData(self):
        return self._jsonData

    def getSequenceNumber(self):
        return self._jsonData.sequenceNumber

    def getCheckinUrls(self):
        return self._jsonData.checkinUrls

    def getAppKey(self):
        return self._jsonData.appKey

    def getEtag(self):
        return self._etag

    def setEtag(self,etag):
        self._etag = etag

    def setSecondaryValues(self,values):
        self._secondaryValues = values

    def getSecondaryValues(self):
        return self._secondaryValues

    def getDisabledVersions(self):
        disableAll = Reflect.field(self._jsonData,"disableAllVersions")
        disableVersions = Reflect.field(self._jsonData,"disabledCrossPlatformVersions")
        ret = list()
        if disableAll:
            x = apptimize_Apptimize.getApptimizeSDKVersion()
            ret.append(x)
        if (disableVersions is not None):
            ret = (ret + self._jsonData.disabledCrossPlatformVersions)
        return ret

    def hxSerialize(self,s):
        self.serializeV1(s)
        s.serialize(self._secondaryValues)

    def serializeV1(self,s):
        s.serialize(haxe_format_JsonPrinter.print(self._jsonData,None,None))
        s.serialize(self._etag)

    def hxUnserialize(self,u):
        self._load_data(u.unserialize())
        self._etag = u.unserialize()
        try:
            self._secondaryValues = u.unserialize()
        except BaseException as _g:
            None
            self._secondaryValues = None

    @staticmethod
    def loadFromString(content):
        m = apptimize_models_ABTMetadata()
        m._load_data(content)
        return m

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._jsonData = None
        _hx_o._seedGroups = None
        _hx_o._hotfixes = None
        _hx_o._alterationCache = None
        _hx_o._etag = None
        _hx_o._secondaryValues = None
apptimize_models_ABTMetadata._hx_class = apptimize_models_ABTMetadata
_hx_classes["apptimize.models.ABTMetadata"] = apptimize_models_ABTMetadata


class apptimize_models_ABTRange:
    _hx_class_name = "apptimize.models.ABTRange"
    __slots__ = ("start", "end")
    _hx_fields = ["start", "end"]
    _hx_methods = ["fromJSON"]

    def __init__(self,json):
        self.end = None
        self.start = None
        self.fromJSON(json)

    def fromJSON(self,json):
        self.start = (json[0] if 0 < len(json) else None)
        self.end = (json[1] if 1 < len(json) else None)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.start = None
        _hx_o.end = None
apptimize_models_ABTRange._hx_class = apptimize_models_ABTRange
_hx_classes["apptimize.models.ABTRange"] = apptimize_models_ABTRange


class apptimize_models_ABTRangeGroup(apptimize_filter_ABTFilterableObject):
    _hx_class_name = "apptimize.models.ABTRangeGroup"
    __slots__ = ("ranges", "sdkParameters", "seedGroups", "variants")
    _hx_fields = ["ranges", "sdkParameters", "seedGroups", "variants"]
    _hx_methods = ["fromJSON", "selectAlterationsIntoArray", "isSelectedBySeed", "getUrlKeyProviders", "applySdkParameters"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilterableObject


    def __init__(self,group):
        self.variants = None
        self.seedGroups = None
        self.sdkParameters = None
        self.ranges = None
        super().__init__()
        self.fromJSON(group)

    def fromJSON(self,group):
        super().fromJSON(group)
        rangeGroup = group
        self.ranges = list()
        if (rangeGroup.ranges is not None):
            _g = 0
            _g1 = rangeGroup.ranges
            while (_g < len(_g1)):
                range = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _this = self.ranges
                x = apptimize_models_ABTRange(range)
                _this.append(x)
        self.seedGroups = list()
        if (rangeGroup.seedGroups is not None):
            _g = 0
            _g1 = rangeGroup.seedGroups
            while (_g < len(_g1)):
                sg = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _this = self.seedGroups
                x = apptimize_models_ABTSeedGroup(sg)
                _this.append(x)
        self.variants = list()
        if (rangeGroup.variants is not None):
            _g = 0
            _g1 = rangeGroup.variants
            while (_g < len(_g1)):
                variant = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _this = self.variants
                x = apptimize_models_ABTVariant(variant)
                _this.append(x)
        if python_Boot.hasField(group,"sdkParameters"):
            self.sdkParameters = apptimize_models_ABTSdkParameters(Reflect.field(group,"sdkParameters"))

    def selectAlterationsIntoArray(self,env,target,overrideOnly):
        match = self.performFilterMatchingWithEnvironment(env)
        if (match.result != apptimize_filter_ABTFilterResult.ABTFilterResultTrue):
            return
        newOverrideOnly = self.computeNewOverrideState(overrideOnly,match)
        _g = 0
        _g1 = self.variants
        while (_g < len(_g1)):
            variant = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            variant.selectAlterationsIntoArray(env,target,newOverrideOnly)
        _g = 0
        _g1 = self.seedGroups
        while (_g < len(_g1)):
            seedgroup = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            seedgroup.selectAlterationsIntoArray(env,target,newOverrideOnly)

    def isSelectedBySeed(self,seed):
        _g = 0
        _g1 = self.ranges
        while (_g < len(_g1)):
            range = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            if ((seed >= range.start) and ((seed < range.end))):
                return True
        return False

    def getUrlKeyProviders(self):
        return (self.asUrlProviders(self.seedGroups) + self.asUrlProviders(self.variants))

    def applySdkParameters(self,to,env):
        if (self.sdkParameters is not None):
            to.mergeOther(self.sdkParameters)
        _g = 0
        _g1 = self.seedGroups
        while (_g < len(_g1)):
            seedGroup = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            seedGroup.applySdkParameters(to,env)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.ranges = None
        _hx_o.sdkParameters = None
        _hx_o.seedGroups = None
        _hx_o.variants = None
apptimize_models_ABTRangeGroup._hx_class = apptimize_models_ABTRangeGroup
_hx_classes["apptimize.models.ABTRangeGroup"] = apptimize_models_ABTRangeGroup


class apptimize_models_ABTSdkParameters:
    _hx_class_name = "apptimize.models.ABTSdkParameters"
    __slots__ = ("minPostFrequencyMs",)
    _hx_fields = ["minPostFrequencyMs"]
    _hx_methods = ["fromJSON", "mergeOther"]

    def __init__(self,json):
        self.minPostFrequencyMs = None
        if (json is not None):
            self.fromJSON(json)

    def fromJSON(self,json):
        temp = Reflect.field(json,"minPostFrequencyMs")
        if (temp is not None):
            self.minPostFrequencyMs = temp

    def mergeOther(self,other):
        if (other.minPostFrequencyMs is not None):
            self.minPostFrequencyMs = other.minPostFrequencyMs

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.minPostFrequencyMs = None
apptimize_models_ABTSdkParameters._hx_class = apptimize_models_ABTSdkParameters
_hx_classes["apptimize.models.ABTSdkParameters"] = apptimize_models_ABTSdkParameters


class apptimize_models_ABTSeed:
    _hx_class_name = "apptimize.models.ABTSeed"
    __slots__ = ("type", "value")
    _hx_fields = ["type", "value"]
    _hx_methods = ["fromDef", "computedSeedMaterial"]

    def __init__(self,seed):
        self.value = None
        self.type = None
        self.fromDef(seed)

    def fromDef(self,seed):
        self.type = seed.type
        self.value = Reflect.field(seed,"value")

    def computedSeedMaterial(self,userID):
        if (self.type == "guid"):
            base = haxe_io_Bytes.ofString("0123456789abcdef")
            resultStr = StringTools.replace(userID,"-","").lower()
            try:
                if (len(resultStr) == 32):
                    return apptimize_util_ABTHash.Sha1(haxe_crypto_BaseCode(base).decodeBytes(haxe_io_Bytes.ofString(resultStr)))
            except BaseException as _g:
                None
                if Std.isOfType(haxe_Exception.caught(_g).unwrap(),str):
                    apptimize_ABTLogger.w("Invalid GUID supplied - treating as string user ID.",_hx_AnonObject({'fileName': "src/apptimize/models/ABTSeed.hx", 'lineNumber': 33, 'className': "apptimize.models.ABTSeed", 'methodName': "computedSeedMaterial"}))
                else:
                    raise _g
            return apptimize_util_ABTHash.Sha1(haxe_io_Bytes.ofString(userID))
        elif (self.value is not None):
            return apptimize_util_ABTHash.Sha1(haxe_io_Bytes.ofString(self.value))
        else:
            apptimize_ABTLogger.e((("Unable to calculate seed for supplied user ID of type: " + HxOverrides.stringOrNull(self.type)) + "."),_hx_AnonObject({'fileName': "src/apptimize/models/ABTSeed.hx", 'lineNumber': 41, 'className': "apptimize.models.ABTSeed", 'methodName': "computedSeedMaterial"}))
            return None

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.type = None
        _hx_o.value = None
apptimize_models_ABTSeed._hx_class = apptimize_models_ABTSeed
_hx_classes["apptimize.models.ABTSeed"] = apptimize_models_ABTSeed


class apptimize_models_ABTSeedGroup(apptimize_filter_ABTFilterableObject):
    _hx_class_name = "apptimize.models.ABTSeedGroup"
    __slots__ = ("rangeGroups", "seeds")
    _hx_fields = ["rangeGroups", "seeds"]
    _hx_methods = ["fromJSON", "computedSeedMaterial", "seed", "selectAlterationsIntoArray", "getUrlKeyProviders", "applySdkParameters"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilterableObject


    def __init__(self,group):
        self.seeds = None
        self.rangeGroups = None
        super().__init__()
        self.fromJSON(group)

    def fromJSON(self,group):
        super().fromJSON(group)
        jsonSeedGroup = group
        self.rangeGroups = list()
        if (jsonSeedGroup.rangeGroups is not None):
            _g = 0
            _g1 = jsonSeedGroup.rangeGroups
            while (_g < len(_g1)):
                range = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _this = self.rangeGroups
                x = apptimize_models_ABTRangeGroup(range)
                _this.append(x)
        self.seeds = list()
        if (jsonSeedGroup.seeds is not None):
            _g = 0
            _g1 = jsonSeedGroup.seeds
            while (_g < len(_g1)):
                seed = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _this = self.seeds
                x = apptimize_models_ABTSeed(seed)
                _this.append(x)

    def computedSeedMaterial(self,userID):
        buffer = haxe_io_BytesBuffer()
        _g = 0
        _g1 = self.seeds
        while (_g < len(_g1)):
            seed = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            b = seed.computedSeedMaterial(userID)
            _hx_len = b.length
            if ((_hx_len < 0) or ((_hx_len > b.length))):
                raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
            buffer.b.extend(b.b[0:_hx_len])
        return apptimize_util_ABTHash.Sha1(buffer.getBytes())

    def seed(self,userID):
        data = self.computedSeedMaterial(userID)
        _hx_len = data.length
        if (_hx_len < 4):
            apptimize_ABTLogger.e((("User ID length too short for seed: " + Std.string(_hx_len)) + "."),_hx_AnonObject({'fileName': "src/apptimize/models/ABTSeedGroup.hx", 'lineNumber': 64, 'className': "apptimize.models.ABTSeedGroup", 'methodName': "seed"}))
            return 0
        l = (_hx_len - 4)
        seed = (((data.b[(l + 3)] | ((data.b[(l + 2)] << 8))) | ((data.b[(l + 1)] << 16))) | ((data.b[l] << 24)))
        seed = (seed & 1073741823)
        return seed

    def selectAlterationsIntoArray(self,env,target,overrideOnly):
        match = self.performFilterMatchingWithEnvironment(env)
        if (match.result != apptimize_filter_ABTFilterResult.ABTFilterResultTrue):
            return
        newOverrideOnly = self.computeNewOverrideState(overrideOnly,match)
        seed = self.seed(env.getUserOrAnonID())
        apptimize_ABTLogger.v((((("Calculated seed for user " + HxOverrides.stringOrNull(env.getUserOrAnonID())) + ": ") + Std.string(seed)) + "."),_hx_AnonObject({'fileName': "src/apptimize/models/ABTSeedGroup.hx", 'lineNumber': 89, 'className': "apptimize.models.ABTSeedGroup", 'methodName': "selectAlterationsIntoArray"}))
        _g = 0
        _g1 = self.rangeGroups
        while (_g < len(_g1)):
            rangeGroup = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            if rangeGroup.isSelectedBySeed(seed):
                rangeGroup.selectAlterationsIntoArray(env,target,newOverrideOnly)
            else:
                rangeGroup.selectAlterationsIntoArray(env,target,True)

    def getUrlKeyProviders(self):
        return self.asUrlProviders(self.rangeGroups)

    def applySdkParameters(self,to,env):
        match = self.performFilterMatchingWithEnvironment(env)
        if (match.result == apptimize_filter_ABTFilterResult.ABTFilterResultTrue):
            seed = self.seed(env.getUserOrAnonID())
            _g = 0
            _g1 = self.rangeGroups
            while (_g < len(_g1)):
                rangeGroup = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                if rangeGroup.isSelectedBySeed(seed):
                    rangeGroup.applySdkParameters(to,env)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.rangeGroups = None
        _hx_o.seeds = None
apptimize_models_ABTSeedGroup._hx_class = apptimize_models_ABTSeedGroup
_hx_classes["apptimize.models.ABTSeedGroup"] = apptimize_models_ABTSeedGroup


class apptimize_models_ABTVariant(apptimize_filter_ABTFilterableObject):
    _hx_class_name = "apptimize.models.ABTVariant"
    __slots__ = ("alterations", "alterations2", "codeBlockName", "experimentId", "experimentName", "experimentType", "startTime", "variantId", "variantName", "cycle", "phase")
    _hx_fields = ["alterations", "alterations2", "codeBlockName", "experimentId", "experimentName", "experimentType", "startTime", "variantId", "variantName", "cycle", "phase"]
    _hx_methods = ["fromJSON", "selectAlterationsIntoArray", "getVariantID", "getVariantName", "getExperimentID", "getExperimentName", "getExperimentType", "getCodeBlockName", "getPhase", "getCycle", "getUrlKeyProviders"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_filter_ABTFilterableObject


    def __init__(self,variant):
        self.phase = None
        self.cycle = None
        self.variantName = None
        self.variantId = None
        self.startTime = None
        self.experimentType = None
        self.experimentName = None
        self.experimentId = None
        self.codeBlockName = None
        self.alterations2 = None
        self.alterations = None
        super().__init__()
        self.fromJSON(variant)

    def fromJSON(self,obj):
        super().fromJSON(obj)
        variant = obj
        self.alterations = list()
        self.alterations2 = list()
        _g = 0
        _g1 = variant.alterations
        while (_g < len(_g1)):
            alteration = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            _this = self.alterations
            x = apptimize_models_ABTAlteration.alterationFromJSON(alteration,self)
            _this.append(x)
        self.codeBlockName = variant.codeBlockName
        if (Type.getClass(self) != apptimize_models_ABTHotfixVariant):
            self.experimentId = variant.experimentId
            self.experimentName = variant.experimentName
            self.experimentType = variant.experimentType
            self.startTime = variant.startTime
            self.variantName = variant.variantName
            self.variantId = variant.variantId
            self.cycle = variant.cycle
            self.phase = variant.phase
        if (python_Boot.hasField(variant,"alterations2") and ((variant.alterations2 is not None))):
            _g = 0
            _g1 = variant.alterations2
            while (_g < len(_g1)):
                alteration = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _this = self.alterations2
                x = apptimize_models_ABTAlteration.alterationFromJSON(alteration,self)
                _this.append(x)
            self.alterations = (self.alterations + self.alterations2)

    def selectAlterationsIntoArray(self,env,target,overrideOnly):
        match = self.performFilterMatchingWithEnvironment(env)
        if (match.result != apptimize_filter_ABTFilterResult.ABTFilterResultTrue):
            return
        newOverrideOnly = self.computeNewOverrideState(overrideOnly,match)
        _g = 0
        _g1 = self.alterations
        while (_g < len(_g1)):
            alteration = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            alteration.selectAlterationsIntoArray(env,target,newOverrideOnly)

    def getVariantID(self):
        return self.variantId

    def getVariantName(self):
        return self.variantName

    def getExperimentID(self):
        return self.experimentId

    def getExperimentName(self):
        return self.experimentName

    def getExperimentType(self):
        return self.experimentType

    def getCodeBlockName(self):
        return self.codeBlockName

    def getPhase(self):
        return self.phase

    def getCycle(self):
        return self.cycle

    def getUrlKeyProviders(self):
        return self.asUrlProviders(self.alterations)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.alterations = None
        _hx_o.alterations2 = None
        _hx_o.codeBlockName = None
        _hx_o.experimentId = None
        _hx_o.experimentName = None
        _hx_o.experimentType = None
        _hx_o.startTime = None
        _hx_o.variantId = None
        _hx_o.variantName = None
        _hx_o.cycle = None
        _hx_o.phase = None
apptimize_models_ABTVariant._hx_class = apptimize_models_ABTVariant
_hx_classes["apptimize.models.ABTVariant"] = apptimize_models_ABTVariant


class apptimize_models_ABTHotfixVariant(apptimize_models_ABTVariant):
    _hx_class_name = "apptimize.models.ABTHotfixVariant"
    __slots__ = ("hotfixName",)
    _hx_fields = ["hotfixName"]
    _hx_methods = ["fromJSON"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_ABTVariant


    def __init__(self,variant):
        self.hotfixName = None
        super().__init__(variant)

    def fromJSON(self,obj):
        super().fromJSON(obj)
        variant = obj
        self.hotfixName = variant.hotfixName

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.hotfixName = None
apptimize_models_ABTHotfixVariant._hx_class = apptimize_models_ABTHotfixVariant
_hx_classes["apptimize.models.ABTHotfixVariant"] = apptimize_models_ABTHotfixVariant


class apptimize_models_results_ABTResultEntry(apptimize_models_ABTJSONObject):
    _hx_class_name = "apptimize.models.results.ABTResultEntry"
    __slots__ = ("_id", "_monotonicTimestamp", "_deviceTimestamp", "_userAttributes", "_prefixedAttributes")
    _hx_fields = ["_id", "_monotonicTimestamp", "_deviceTimestamp", "_userAttributes", "_prefixedAttributes"]
    _hx_methods = ["_getNextSequenceNumber", "_getMonotonicTimestamp", "JSONRepresentation", "hxSerialize", "hxUnserialize"]
    _hx_statics = ["RESULT_ENTRY_CREATION_LOCK"]
    _hx_interfaces = []
    _hx_super = apptimize_models_ABTJSONObject


    def __init__(self,env):
        self._prefixedAttributes = None
        self._userAttributes = None
        self._deviceTimestamp = None
        self._monotonicTimestamp = None
        self._id = None
        apptimize_models_results_ABTResultEntry.RESULT_ENTRY_CREATION_LOCK.acquire()
        try:
            self._id = self._getNextSequenceNumber()
            self._deviceTimestamp = haxe_Int64Helper.fromFloat((Date.now().date.timestamp() * 1000))
            self._monotonicTimestamp = self._getMonotonicTimestamp(self._deviceTimestamp)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_models_results_ABTResultEntry.RESULT_ENTRY_CREATION_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_models_results_ABTResultEntry.RESULT_ENTRY_CREATION_LOCK.release()
        self._prefixedAttributes = haxe_ds_StringMap()
        if ((env is not None) and ((env.customProperties.availableProperties is not None))):
            env.customProperties.addJSONProperties(self._prefixedAttributes)
        apptimize_support_properties_ABTInternalProperties.sharedInstance().addJSONProperties(self._prefixedAttributes)
        env.applicationProperties.addJSONProperties(self._prefixedAttributes)

    def _getNextSequenceNumber(self):
        sequenceString = apptimize_support_persistence_ABTPersistence.loadString(apptimize_support_persistence_ABTPersistence.kResultEntrySequenceKey)
        this1 = haxe__Int64____Int64(0,0)
        sequence = this1
        if (sequenceString is not None):
            sequence = haxe_Int64Helper.parseString(sequenceString)
        ret = sequence
        this1 = haxe__Int64____Int64(sequence.high,sequence.low)
        sequence = this1
        def _hx_local_2():
            _hx_local_0 = sequence
            _hx_local_1 = _hx_local_0.low
            _hx_local_0.low = (_hx_local_1 + 1)
            return _hx_local_1
        ret = _hx_local_2()
        sequence.low = ((sequence.low + (2 ** 31)) % (2 ** 32) - (2 ** 31))
        if (sequence.low == 0):
            def _hx_local_5():
                _hx_local_3 = sequence
                _hx_local_4 = _hx_local_3.high
                _hx_local_3.high = (_hx_local_4 + 1)
                return _hx_local_4
            ret = _hx_local_5()
            sequence.high = ((sequence.high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
        apptimize_support_persistence_ABTPersistence.saveString(apptimize_support_persistence_ABTPersistence.kResultEntrySequenceKey,haxe__Int64_Int64_Impl_.toString(sequence))
        return sequence

    def _getMonotonicTimestamp(self,deviceTime):
        timestamp = deviceTime
        this1 = haxe__Int64____Int64(0,0)
        lastTimestamp = this1
        lastTimestampString = apptimize_support_persistence_ABTPersistence.loadString(apptimize_support_persistence_ABTPersistence.kResultEntryTimestampKey)
        if (lastTimestampString is not None):
            lastTimestamp = haxe_Int64Helper.parseString(lastTimestampString)
        v = (((lastTimestamp.high - deviceTime.high) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
        if (v == 0):
            v = haxe__Int32_Int32_Impl_.ucompare(lastTimestamp.low,deviceTime.low)
        if ((((v if ((deviceTime.high < 0)) else -1) if ((lastTimestamp.high < 0)) else (v if ((deviceTime.high >= 0)) else 1))) >= 0):
            b_high = 0
            b_low = 1
            high = (((lastTimestamp.high + b_high) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            low = (((lastTimestamp.low + b_low) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            if (haxe__Int32_Int32_Impl_.ucompare(low,lastTimestamp.low) < 0):
                ret = high
                high = (high + 1)
                high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            this1 = haxe__Int64____Int64(high,low)
            timestamp = this1
        apptimize_support_persistence_ABTPersistence.saveString(apptimize_support_persistence_ABTPersistence.kResultEntryTimestampKey,haxe__Int64_Int64_Impl_.toString(timestamp))
        return timestamp

    def JSONRepresentation(self):
        _g = haxe_ds_StringMap()
        value = apptimize_util_ABTInt64Utils.toPreprocessedString(self._id)
        _g.h["ei"] = value
        value = apptimize_util_ABTInt64Utils.toPreprocessedString(self._monotonicTimestamp)
        _g.h["mt"] = value
        value = apptimize_util_ABTInt64Utils.toPreprocessedString(self._deviceTimestamp)
        _g.h["dt"] = value
        value = apptimize_util_ABTUtilDictionary.filterNullValues(self._prefixedAttributes)
        _g.h["pa"] = value
        jsonDict = _g
        if (self._userAttributes is not None):
            v = apptimize_util_ABTUtilDictionary.filterNullValues(self._userAttributes)
            jsonDict.h["ua"] = v
        return jsonDict

    def hxSerialize(self,s):
        apptimize_util_ABTInt64Utils._serializeInt64(self._id,s)
        apptimize_util_ABTInt64Utils._serializeInt64(self._monotonicTimestamp,s)
        apptimize_util_ABTInt64Utils._serializeInt64(self._deviceTimestamp,s)
        s.serialize(self._userAttributes)
        s.serialize(self._prefixedAttributes)

    def hxUnserialize(self,u):
        self._id = apptimize_util_ABTInt64Utils._deserializeInt64(u)
        self._monotonicTimestamp = apptimize_util_ABTInt64Utils._deserializeInt64(u)
        self._deviceTimestamp = apptimize_util_ABTInt64Utils._deserializeInt64(u)
        self._userAttributes = u.unserialize()
        self._prefixedAttributes = u.unserialize()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._id = None
        _hx_o._monotonicTimestamp = None
        _hx_o._deviceTimestamp = None
        _hx_o._userAttributes = None
        _hx_o._prefixedAttributes = None
apptimize_models_results_ABTResultEntry._hx_class = apptimize_models_results_ABTResultEntry
_hx_classes["apptimize.models.results.ABTResultEntry"] = apptimize_models_results_ABTResultEntry


class apptimize_models_results_ABTResultEntryVariantShown(apptimize_models_results_ABTResultEntry):
    _hx_class_name = "apptimize.models.results.ABTResultEntryVariantShown"
    __slots__ = ("_type", "_variantID", "_cycle", "_phase")
    _hx_fields = ["_type", "_variantID", "_cycle", "_phase"]
    _hx_methods = ["JSONRepresentation", "hxSerialize", "hxUnserialize"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_results_ABTResultEntry


    def __init__(self,env,variantID,cycle,phase):
        self._phase = None
        self._cycle = None
        self._variantID = None
        self._type = "v"
        super().__init__(env)
        self._variantID = variantID
        self._cycle = cycle
        self._phase = phase

    def JSONRepresentation(self):
        jsonDict = super().JSONRepresentation()
        v = self._type
        jsonDict.h["ty"] = v
        v = self._variantID
        jsonDict.h["v"] = v
        _g = haxe_ds_StringMap()
        _g.h["v"] = self._variantID
        _g.h["c"] = self._cycle
        _g.h["p"] = self._phase
        v = _g
        jsonDict.h["vp"] = v
        return jsonDict

    def hxSerialize(self,s):
        super().hxSerialize(s)
        s.serialize(self._type)
        s.serialize(self._variantID)
        s.serialize(self._cycle)
        s.serialize(self._phase)

    def hxUnserialize(self,u):
        super().hxUnserialize(u)
        self._type = u.unserialize()
        self._variantID = u.unserialize()
        self._cycle = u.unserialize()
        self._phase = u.unserialize()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._type = None
        _hx_o._variantID = None
        _hx_o._cycle = None
        _hx_o._phase = None
apptimize_models_results_ABTResultEntryVariantShown._hx_class = apptimize_models_results_ABTResultEntryVariantShown
_hx_classes["apptimize.models.results.ABTResultEntryVariantShown"] = apptimize_models_results_ABTResultEntryVariantShown


class apptimize_models_results_ABTResultEntryEvent(apptimize_models_results_ABTResultEntry):
    _hx_class_name = "apptimize.models.results.ABTResultEntryEvent"
    __slots__ = ("_type", "_name", "_source", "_attributes")
    _hx_fields = ["_type", "_name", "_source", "_attributes"]
    _hx_methods = ["JSONRepresentation", "hxSerialize", "hxUnserialize"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_results_ABTResultEntry


    def __init__(self,env,name,source,attributes):
        self._attributes = None
        self._source = None
        self._name = None
        self._type = "ee"
        super().__init__(env)
        self._name = name
        self._source = source
        self._attributes = attributes

    def JSONRepresentation(self):
        jsonDict = super().JSONRepresentation()
        v = self._type
        jsonDict.h["ty"] = v
        v = self._name
        jsonDict.h["n"] = v
        v = self._source
        jsonDict.h["s"] = v
        v = self._attributes
        jsonDict.h["a"] = v
        return jsonDict

    def hxSerialize(self,s):
        super().hxSerialize(s)
        s.serialize(self._type)
        s.serialize(self._name)
        s.serialize(self._source)
        s.serialize(self._attributes)

    def hxUnserialize(self,u):
        super().hxUnserialize(u)
        self._type = u.unserialize()
        self._name = u.unserialize()
        self._source = u.unserialize()
        self._attributes = u.unserialize()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._type = None
        _hx_o._name = None
        _hx_o._source = None
        _hx_o._attributes = None
apptimize_models_results_ABTResultEntryEvent._hx_class = apptimize_models_results_ABTResultEntryEvent
_hx_classes["apptimize.models.results.ABTResultEntryEvent"] = apptimize_models_results_ABTResultEntryEvent


class apptimize_models_results_ABTResultEntryMetadataProcessed(apptimize_models_results_ABTResultEntry):
    _hx_class_name = "apptimize.models.results.ABTResultEntryMetadataProcessed"
    __slots__ = ("_type", "_metadataSequenceNumber", "_enrolledVariantsCyclesPhases", "_enrolledVariantIDs")
    _hx_fields = ["_type", "_metadataSequenceNumber", "_enrolledVariantsCyclesPhases", "_enrolledVariantIDs"]
    _hx_methods = ["JSONRepresentation", "hxSerialize", "hxUnserialize"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_results_ABTResultEntry


    def __init__(self,env,sequence,enrolledVariantsCyclesPhases):
        self._enrolledVariantIDs = None
        self._enrolledVariantsCyclesPhases = None
        self._metadataSequenceNumber = None
        self._type = "md"
        super().__init__(env)
        self._metadataSequenceNumber = sequence
        self._enrolledVariantsCyclesPhases = enrolledVariantsCyclesPhases
        self._enrolledVariantIDs = list()
        _g = 0
        _g1 = self._enrolledVariantsCyclesPhases
        while (_g < len(_g1)):
            variantCyclePhase = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            _this = self._enrolledVariantIDs
            x = variantCyclePhase.v
            _this.append(x)

    def JSONRepresentation(self):
        jsonDict = super().JSONRepresentation()
        if (len(self._enrolledVariantsCyclesPhases) > 0):
            v = self._enrolledVariantsCyclesPhases
            jsonDict.h["vp"] = v
        v = self._enrolledVariantIDs
        jsonDict.h["v"] = v
        v = self._metadataSequenceNumber
        jsonDict.h["s"] = v
        v = self._type
        jsonDict.h["ty"] = v
        return jsonDict

    def hxSerialize(self,s):
        super().hxSerialize(s)
        s.serialize(self._type)
        s.serialize(self._metadataSequenceNumber)
        s.serialize(self._enrolledVariantIDs)
        s.serialize(self._enrolledVariantsCyclesPhases)

    def hxUnserialize(self,u):
        super().hxUnserialize(u)
        self._type = u.unserialize()
        self._metadataSequenceNumber = u.unserialize()
        self._enrolledVariantIDs = u.unserialize()
        self._enrolledVariantsCyclesPhases = u.unserialize()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._type = None
        _hx_o._metadataSequenceNumber = None
        _hx_o._enrolledVariantsCyclesPhases = None
        _hx_o._enrolledVariantIDs = None
apptimize_models_results_ABTResultEntryMetadataProcessed._hx_class = apptimize_models_results_ABTResultEntryMetadataProcessed
_hx_classes["apptimize.models.results.ABTResultEntryMetadataProcessed"] = apptimize_models_results_ABTResultEntryMetadataProcessed


class apptimize_models_results_ABTResultEntryAttributesChanged(apptimize_models_results_ABTResultEntry):
    _hx_class_name = "apptimize.models.results.ABTResultEntryAttributesChanged"
    __slots__ = ("_type", "_enrolledVariantsCyclesPhases", "_enrolledVariantIDs")
    _hx_fields = ["_type", "_enrolledVariantsCyclesPhases", "_enrolledVariantIDs"]
    _hx_methods = ["JSONRepresentation", "hxSerialize", "hxUnserialize"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_results_ABTResultEntry


    def __init__(self,env,enrolledVariantsCyclesPhases):
        self._enrolledVariantIDs = None
        self._enrolledVariantsCyclesPhases = None
        self._type = "ac"
        super().__init__(env)
        self._enrolledVariantsCyclesPhases = enrolledVariantsCyclesPhases
        self._enrolledVariantIDs = list()
        _g = 0
        _g1 = self._enrolledVariantsCyclesPhases
        while (_g < len(_g1)):
            variantCyclePhase = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            _this = self._enrolledVariantIDs
            x = variantCyclePhase.v
            _this.append(x)

    def JSONRepresentation(self):
        jsonDict = super().JSONRepresentation()
        v = self._type
        jsonDict.h["ty"] = v
        v = self._enrolledVariantIDs
        jsonDict.h["v"] = v
        if (len(self._enrolledVariantsCyclesPhases) > 0):
            v = self._enrolledVariantsCyclesPhases
            jsonDict.h["vp"] = v
        return jsonDict

    def hxSerialize(self,s):
        super().hxSerialize(s)
        s.serialize(self._type)
        s.serialize(self._enrolledVariantIDs)
        s.serialize(self._enrolledVariantsCyclesPhases)

    def hxUnserialize(self,u):
        super().hxUnserialize(u)
        self._type = u.unserialize()
        self._enrolledVariantIDs = u.unserialize()
        self._enrolledVariantsCyclesPhases = u.unserialize()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._type = None
        _hx_o._enrolledVariantsCyclesPhases = None
        _hx_o._enrolledVariantIDs = None
apptimize_models_results_ABTResultEntryAttributesChanged._hx_class = apptimize_models_results_ABTResultEntryAttributesChanged
_hx_classes["apptimize.models.results.ABTResultEntryAttributesChanged"] = apptimize_models_results_ABTResultEntryAttributesChanged


class apptimize_models_results_ABTResultEntryUserEnd(apptimize_models_results_ABTResultEntry):
    _hx_class_name = "apptimize.models.results.ABTResultEntryUserEnd"
    __slots__ = ("_type", "_nextUserID")
    _hx_fields = ["_type", "_nextUserID"]
    _hx_methods = ["JSONRepresentation", "hxSerialize", "hxUnserialize"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_results_ABTResultEntry


    def __init__(self,env,nextUserID):
        self._nextUserID = None
        self._type = "ue"
        super().__init__(env)
        self._nextUserID = nextUserID

    def JSONRepresentation(self):
        jsonDict = super().JSONRepresentation()
        v = self._type
        jsonDict.h["ty"] = v
        v = self._nextUserID
        jsonDict.h["n"] = v
        return jsonDict

    def hxSerialize(self,s):
        super().hxSerialize(s)
        s.serialize(self._type)
        s.serialize(self._nextUserID)

    def hxUnserialize(self,u):
        super().hxUnserialize(u)
        self._type = u.unserialize()
        self._nextUserID = u.unserialize()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._type = None
        _hx_o._nextUserID = None
apptimize_models_results_ABTResultEntryUserEnd._hx_class = apptimize_models_results_ABTResultEntryUserEnd
_hx_classes["apptimize.models.results.ABTResultEntryUserEnd"] = apptimize_models_results_ABTResultEntryUserEnd


class apptimize_models_results_ABTResultEntryUserStart(apptimize_models_results_ABTResultEntry):
    _hx_class_name = "apptimize.models.results.ABTResultEntryUserStart"
    __slots__ = ("_type", "_previousUserID")
    _hx_fields = ["_type", "_previousUserID"]
    _hx_methods = ["JSONRepresentation", "hxSerialize", "hxUnserialize"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_results_ABTResultEntry


    def __init__(self,env,previousUserID):
        self._previousUserID = None
        self._type = "us"
        super().__init__(env)
        self._previousUserID = previousUserID

    def JSONRepresentation(self):
        jsonDict = super().JSONRepresentation()
        v = self._type
        jsonDict.h["ty"] = v
        v = self._previousUserID
        jsonDict.h["p"] = v
        return jsonDict

    def hxSerialize(self,s):
        super().hxSerialize(s)
        s.serialize(self._type)
        s.serialize(self._previousUserID)

    def hxUnserialize(self,u):
        super().hxUnserialize(u)
        self._type = u.unserialize()
        self._previousUserID = u.unserialize()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._type = None
        _hx_o._previousUserID = None
apptimize_models_results_ABTResultEntryUserStart._hx_class = apptimize_models_results_ABTResultEntryUserStart
_hx_classes["apptimize.models.results.ABTResultEntryUserStart"] = apptimize_models_results_ABTResultEntryUserStart


class apptimize_models_results_ABTResultEntrySuccessfullyPosted(apptimize_models_results_ABTResultEntry):
    _hx_class_name = "apptimize.models.results.ABTResultEntrySuccessfullyPosted"
    __slots__ = ("_type", "_timestampFromServer", "_firstEntryID", "_lastEntryID")
    _hx_fields = ["_type", "_timestampFromServer", "_firstEntryID", "_lastEntryID"]
    _hx_methods = ["JSONRepresentation", "hxSerialize", "hxUnserialize"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_results_ABTResultEntry


    def __init__(self,timestampFromServer,firstEntryID,lastEntryID):
        self._lastEntryID = haxe__Int64____Int64(0,0)
        self._firstEntryID = haxe__Int64____Int64(0,0)
        self._timestampFromServer = haxe__Int64____Int64(0,0)
        self._type = "sp"
        super().__init__(None)
        self._timestampFromServer = timestampFromServer
        self._firstEntryID = firstEntryID
        self._lastEntryID = lastEntryID

    def JSONRepresentation(self):
        jsonDict = super().JSONRepresentation()
        v = self._type
        jsonDict.h["ty"] = v
        v = apptimize_util_ABTInt64Utils.toPreprocessedString(self._timestampFromServer)
        jsonDict.h["t"] = v
        v = apptimize_util_ABTInt64Utils.toPreprocessedString(self._firstEntryID)
        jsonDict.h["f"] = v
        v = apptimize_util_ABTInt64Utils.toPreprocessedString(self._lastEntryID)
        jsonDict.h["l"] = v
        return jsonDict

    def hxSerialize(self,s):
        super().hxSerialize(s)
        s.serialize(self._type)
        apptimize_util_ABTInt64Utils._serializeInt64(self._timestampFromServer,s)
        apptimize_util_ABTInt64Utils._serializeInt64(self._firstEntryID,s)
        apptimize_util_ABTInt64Utils._serializeInt64(self._lastEntryID,s)

    def hxUnserialize(self,u):
        super().hxUnserialize(u)
        self._type = u.unserialize()
        self._timestampFromServer = apptimize_util_ABTInt64Utils._deserializeInt64(u)
        self._firstEntryID = apptimize_util_ABTInt64Utils._deserializeInt64(u)
        self._lastEntryID = apptimize_util_ABTInt64Utils._deserializeInt64(u)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._type = None
        _hx_o._timestampFromServer = None
        _hx_o._firstEntryID = None
        _hx_o._lastEntryID = None
apptimize_models_results_ABTResultEntrySuccessfullyPosted._hx_class = apptimize_models_results_ABTResultEntrySuccessfullyPosted
_hx_classes["apptimize.models.results.ABTResultEntrySuccessfullyPosted"] = apptimize_models_results_ABTResultEntrySuccessfullyPosted


class apptimize_models_results_ABTResultEntryDataTypeLimitReached(apptimize_models_results_ABTResultEntry):
    _hx_class_name = "apptimize.models.results.ABTResultEntryDataTypeLimitReached"
    __slots__ = ("_type", "_currentEntryCount")
    _hx_fields = ["_type", "_currentEntryCount"]
    _hx_methods = ["JSONRepresentation", "hxSerialize", "hxUnserialize"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_models_results_ABTResultEntry


    def __init__(self,currentEntryCount):
        self._currentEntryCount = haxe__Int64____Int64(0,0)
        self._type = "dl"
        super().__init__(None)
        self._currentEntryCount = currentEntryCount

    def JSONRepresentation(self):
        jsonDict = super().JSONRepresentation()
        v = self._type
        jsonDict.h["ty"] = v
        v = apptimize_util_ABTInt64Utils.toPreprocessedString(self._currentEntryCount)
        jsonDict.h["c"] = v
        return jsonDict

    def hxSerialize(self,s):
        super().hxSerialize(s)
        s.serialize(self._type)
        apptimize_util_ABTInt64Utils._serializeInt64(self._currentEntryCount,s)

    def hxUnserialize(self,u):
        super().hxUnserialize(u)
        self._type = u.unserialize()
        self._currentEntryCount = apptimize_util_ABTInt64Utils._deserializeInt64(u)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._type = None
        _hx_o._currentEntryCount = None
apptimize_models_results_ABTResultEntryDataTypeLimitReached._hx_class = apptimize_models_results_ABTResultEntryDataTypeLimitReached
_hx_classes["apptimize.models.results.ABTResultEntryDataTypeLimitReached"] = apptimize_models_results_ABTResultEntryDataTypeLimitReached


class apptimize_models_results_ABTResultLog:
    _hx_class_name = "apptimize.models.results.ABTResultLog"
    __slots__ = ("entries", "userID", "anonID", "appkey", "uniqueID")
    _hx_fields = ["entries", "userID", "anonID", "appkey", "uniqueID"]
    _hx_methods = ["logEntry", "entryCount", "getAppKey", "getUniqueUserKey", "toJSON"]

    def __init__(self,env):
        self.uniqueID = None
        self.appkey = None
        self.anonID = None
        self.userID = None
        if (env is not None):
            self.userID = env.userID
            self.anonID = env.anonID
            self.appkey = env.appkey
            self.uniqueID = env.getUniqueUserID()
        self.entries = list()

    def logEntry(self,entry):
        _this = self.entries
        _this.append(entry)

    def entryCount(self):
        return len(self.entries)

    def getAppKey(self):
        return self.appkey

    def getUniqueUserKey(self):
        return self.uniqueID

    def toJSON(self):
        json = haxe_ds_StringMap()
        jsonEntries = list()
        _g = 0
        _g1 = self.entries
        while (_g < len(_g1)):
            entry = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            x = entry.JSONRepresentation()
            jsonEntries.append(x)
        v = "v4"
        json.h["type"] = v
        v = self.getAppKey()
        json.h["a"] = v
        v = apptimize_ABTDataStore.getServerGUID()
        json.h["g"] = v
        currentDate = Date.now()
        nowMs = haxe_Int64Helper.fromFloat((Date.now().date.timestamp() * 1000))
        v = apptimize_util_ABTInt64Utils.toPreprocessedString(nowMs)
        json.h["c"] = v
        v = jsonEntries
        json.h["e"] = v
        v = ("Cross Platform " + HxOverrides.stringOrNull(apptimize_Apptimize.getApptimizeSDKVersion()))
        json.h["v"] = v
        if (self.userID is not None):
            v = self.userID
            json.h["u"] = v
        return apptimize_util_ABTJSONUtils.stringify(json)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.entries = None
        _hx_o.userID = None
        _hx_o.anonID = None
        _hx_o.appkey = None
        _hx_o.uniqueID = None
apptimize_models_results_ABTResultLog._hx_class = apptimize_models_results_ABTResultLog
_hx_classes["apptimize.models.results.ABTResultLog"] = apptimize_models_results_ABTResultLog


class apptimize_support_initialize_ABTPlatformInitialize:
    _hx_class_name = "apptimize.support.initialize.ABTPlatformInitialize"
    __slots__ = ()
    _hx_statics = ["_isThreadingEnabled", "initialize", "hookShutdown", "shutdownPlatform", "shutdownHook"]
    _isThreadingEnabled = None

    @staticmethod
    def initialize():
        apptimize_support_persistence_ABTPersistence.saveString(apptimize_support_persistence_ABTPersistence.kApptimizeVersionKey,apptimize_Apptimize.getApptimizeSDKVersion())
        apptimize_support_initialize_ABTPlatformInitialize._isThreadingEnabled = apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.THREADING_ENABLED_KEY)
        if (not apptimize_support_initialize_ABTPlatformInitialize._isThreadingEnabled):
            apptimize_ABTLogger.w("Metadata update timers are disabled when threading is disabled.",_hx_AnonObject({'fileName': "src/apptimize/support/initialize/ABTPlatformInitialize.hx", 'lineNumber': 104, 'className': "apptimize.support.initialize.ABTPlatformInitialize", 'methodName': "initialize"}))
        apptimize_api_ABTMetadataPoller.startPolling()
        apptimize_support_initialize_ABTPlatformInitialize.hookShutdown(apptimize_support_initialize_ABTPlatformInitialize._isThreadingEnabled)

    @staticmethod
    def hookShutdown(isThreaded):
        if (not apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.AUTOMATIC_SHUTDOWN_HOOK)):
            apptimize_ABTLogger.v("Process exits will not be handled to persist Apptimize library state across server restarts.",_hx_AnonObject({'fileName': "src/apptimize/support/initialize/ABTPlatformInitialize.hx", 'lineNumber': 119, 'className': "apptimize.support.initialize.ABTPlatformInitialize", 'methodName': "hookShutdown"}))
            return
        if isThreaded:
            apptimize_native_python_AtExit.register(apptimize_support_initialize_ABTPlatformInitialize.shutdownHook)

    @staticmethod
    def shutdownPlatform():
        apptimize_api_ABTMetadataPoller.stopPolling()

    @staticmethod
    def shutdownHook():
        apptimize_ApptimizeInternal.shutdown()
apptimize_support_initialize_ABTPlatformInitialize._hx_class = apptimize_support_initialize_ABTPlatformInitialize
_hx_classes["apptimize.support.initialize.ABTPlatformInitialize"] = apptimize_support_initialize_ABTPlatformInitialize


class apptimize_support_persistence_ABTPersistentInterface:
    _hx_class_name = "apptimize.support.persistence.ABTPersistentInterface"
    __slots__ = ()
    _hx_methods = ["save", "load", "clear", "saveObject", "loadObject", "sync", "hasDidUnserialize"]

    def save(self,key,value,latency = None,compress = None):
        if (latency is None):
            latency = 0
        if (compress is None):
            compress = False
        raise haxe_Exception.thrown("ABTPersistentInterface.save not implemented")

    def load(self,key,latency = None,callback = None):
        if (latency is None):
            latency = 0
        raise haxe_Exception.thrown("ABTPersistentInterface.load not implemented")

    def clear(self,latency = None):
        if (latency is None):
            latency = 2

    def saveObject(self,key,value,latency = None,compress = None):
        if (latency is None):
            latency = 0
        if (compress is None):
            compress = False
        serializer = haxe_Serializer()
        serializer.serialize(value)
        serializer.serialize(apptimize_Apptimize.getApptimizeSDKVersion())
        self.save(key,serializer.toString(),latency,compress)

    def loadObject(self,key,latency = None,callback = None):
        if (latency is None):
            latency = 0
        _gthis = self
        result = None
        def _hx_local_0(key,serializedObject):
            nonlocal result
            if (serializedObject is not None):
                try:
                    unserializer = haxe_Unserializer(serializedObject)
                    result = unserializer.unserialize()
                    if ((result is not None) and _gthis.hasDidUnserialize(result)):
                        Reflect.field(result,"didUnserialize")()
                except BaseException as _g:
                    None
                    unknown = haxe_Exception.caught(_g).unwrap()
                    apptimize_ABTLogger.e(((("Error deserializing \"" + ("null" if key is None else key)) + "\" from persistent storage. Error: ") + Std.string(unknown)),_hx_AnonObject({'fileName': "src/apptimize/support/persistence/ABTPersistence.hx", 'lineNumber': 50, 'className': "apptimize.support.persistence.ABTPersistentInterface", 'methodName': "loadObject"}))
                if (callback is not None):
                    callback(key,result)
                    return result
            if (callback is not None):
                callback(key,None)
            return result
        processObject = _hx_local_0
        if (callback is not None):
            return self.load(key,latency,processObject)
        else:
            serializedObject = self.load(key,latency,callback)
            return processObject(key,serializedObject)

    def sync(self,key,fromLatency,toLatency,callback = None):
        def _hx_local_0(key,value):
            if (callback is not None):
                callback(key,value)
        onCallback = _hx_local_0
        self.loadObject(key,fromLatency,onCallback)

    def hasDidUnserialize(self,obj):
        return python_Boot.hasField(obj,"didUnserialize")

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_support_persistence_ABTPersistentInterface._hx_class = apptimize_support_persistence_ABTPersistentInterface
_hx_classes["apptimize.support.persistence.ABTPersistentInterface"] = apptimize_support_persistence_ABTPersistentInterface


class apptimize_support_persistence_ABTPICacheStorage(apptimize_support_persistence_ABTPersistentInterface):
    _hx_class_name = "apptimize.support.persistence.ABTPICacheStorage"
    __slots__ = ("cacheMap",)
    _hx_fields = ["cacheMap"]
    _hx_methods = ["save", "saveObject", "loadObject", "load", "clear", "sync"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_support_persistence_ABTPersistentInterface


    def __init__(self):
        self.cacheMap = haxe_ds_StringMap()

    def save(self,key,value,latency = None,compress = None):
        if (latency is None):
            latency = 0
        if (compress is None):
            compress = False
        if (value is not None):
            self.cacheMap.h[key] = value
        else:
            self.cacheMap.remove(key)

    def saveObject(self,key,value,latency = None,compress = None):
        if (latency is None):
            latency = 0
        if (compress is None):
            compress = False
        if (value is not None):
            self.cacheMap.h[key] = value
        else:
            self.cacheMap.remove(key)

    def loadObject(self,key,latency = None,callback = None):
        if (latency is None):
            latency = 0
        value = self.cacheMap.h.get(key,None)
        if (callback is not None):
            callback(key,value)
        return value

    def load(self,key,latency = None,callback = None):
        if (latency is None):
            latency = 0
        value = self.cacheMap.h.get(key,None)
        if (callback is not None):
            callback(key,value)
        return value

    def clear(self,latency = None):
        if (latency is None):
            latency = 0
        self.cacheMap = haxe_ds_StringMap()

    def sync(self,key,fromLatency,toLatency,callback = None):
        if (callback is not None):
            callback(key,self.load(key))

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.cacheMap = None
apptimize_support_persistence_ABTPICacheStorage._hx_class = apptimize_support_persistence_ABTPICacheStorage
_hx_classes["apptimize.support.persistence.ABTPICacheStorage"] = apptimize_support_persistence_ABTPICacheStorage


class apptimize_support_persistence_ABTPIDiskStorage(apptimize_support_persistence_ABTPersistentInterface):
    _hx_class_name = "apptimize.support.persistence.ABTPIDiskStorage"
    __slots__ = ("_localStoragePath", "_extension", "_keys")
    _hx_fields = ["_localStoragePath", "_extension", "_keys"]
    _hx_methods = ["_dataFromDisk", "_deleteFile", "save", "load", "clear"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_support_persistence_ABTPersistentInterface


    def __init__(self):
        self._keys = None
        self._extension = ".data"
        self._localStoragePath = "data/apptimize/"
        self._localStoragePath = apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.LOCAL_DISK_STORAGE_PATH_KEY)
        if (not sys_FileSystem.exists(self._localStoragePath)):
            sys_FileSystem.createDirectory(self._localStoragePath)
        self._keys = list()

    def _dataFromDisk(self,path,localPath = None):
        if (localPath is None):
            localPath = ""
        filePath = ((("null" if localPath is None else localPath) + ("null" if path is None else path)) + HxOverrides.stringOrNull(self._extension))
        if sys_FileSystem.exists(filePath):
            content = sys_io_File.getContent(filePath)
            return content
        else:
            apptimize_ABTLogger.v((("File not found: " + ("null" if filePath is None else filePath)) + ". Unable to load data from disk."),_hx_AnonObject({'fileName': "src/apptimize/support/persistence/ABTPIDiskStorage.hx", 'lineNumber': 30, 'className': "apptimize.support.persistence.ABTPIDiskStorage", 'methodName': "_dataFromDisk"}))
        return None

    def _deleteFile(self,key,localPath = None):
        if (localPath is None):
            localPath = ""
        if sys_FileSystem.exists(((("null" if localPath is None else localPath) + ("null" if key is None else key)) + HxOverrides.stringOrNull(self._extension))):
            sys_FileSystem.deleteFile(((("null" if localPath is None else localPath) + ("null" if key is None else key)) + HxOverrides.stringOrNull(self._extension)))

    def save(self,key,value,latency = None,compress = None):
        if (latency is None):
            latency = 0
        if (compress is None):
            compress = False
        filePath = ((HxOverrides.stringOrNull(self._localStoragePath) + ("null" if key is None else key)) + HxOverrides.stringOrNull(self._extension))
        if (value is not None):
            sys_io_File.saveContent(filePath,value)
            _this = self._keys
            _this.append(key)
        else:
            self._deleteFile(key,self._localStoragePath)
            python_internal_ArrayImpl.remove(self._keys,key)

    def load(self,key,latency = None,callback = None):
        if (latency is None):
            latency = 0
        result = self._dataFromDisk(key,self._localStoragePath)
        if (callback is not None):
            callback(key,result)
        return result

    def clear(self,latency = None):
        if (latency is None):
            latency = 2
        _g = 0
        _g1 = self._keys
        while (_g < len(_g1)):
            key = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            self._deleteFile(key,self._localStoragePath)
        self._keys = list()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._localStoragePath = None
        _hx_o._extension = None
        _hx_o._keys = None
apptimize_support_persistence_ABTPIDiskStorage._hx_class = apptimize_support_persistence_ABTPIDiskStorage
_hx_classes["apptimize.support.persistence.ABTPIDiskStorage"] = apptimize_support_persistence_ABTPIDiskStorage


class apptimize_support_persistence_ABTPISmartStorage(apptimize_support_persistence_ABTPersistentInterface):
    _hx_class_name = "apptimize.support.persistence.ABTPISmartStorage"
    __slots__ = ("_lowLatencyStorage", "_highLatencyStorage")
    _hx_fields = ["_lowLatencyStorage", "_highLatencyStorage"]
    _hx_methods = ["save", "load", "saveObject", "loadObject", "storageForLatency", "clear", "sync", "deleteHighLatencyOnSync"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_support_persistence_ABTPersistentInterface


    def __init__(self,lowLatencyStorage,highLatencyStorage):
        self._lowLatencyStorage = lowLatencyStorage
        self._highLatencyStorage = highLatencyStorage

    def save(self,key,value,latency = None,compress = None):
        if (latency is None):
            latency = 0
        if (compress is None):
            compress = False
        self.storageForLatency(latency).save(key,value,latency)

    def load(self,key,latency = None,callback = None):
        if (latency is None):
            latency = 0
        return self.storageForLatency(latency).load(key,latency,callback)

    def saveObject(self,key,value,latency = None,compress = None):
        if (latency is None):
            latency = 0
        if (compress is None):
            compress = False
        self.storageForLatency(latency).saveObject(key,value,latency)

    def loadObject(self,key,latency = None,callback = None):
        if (latency is None):
            latency = 0
        return self.storageForLatency(latency).loadObject(key,latency,callback)

    def storageForLatency(self,latency):
        if (latency == apptimize_support_persistence_ABTPersistence.LOW_LATENCY):
            return self._lowLatencyStorage
        return self._highLatencyStorage

    def clear(self,latency = None):
        if (latency is None):
            latency = 2
        if ((latency == apptimize_support_persistence_ABTPersistence.LOW_LATENCY) or ((latency == apptimize_support_persistence_ABTPersistence.ALL_LATENCY))):
            self._lowLatencyStorage.clear(latency)
        if ((latency == apptimize_support_persistence_ABTPersistence.HIGH_LATENCY) or ((latency == apptimize_support_persistence_ABTPersistence.ALL_LATENCY))):
            self._highLatencyStorage.clear(latency)

    def sync(self,key,fromLatency,toLatency,callback = None):
        _gthis = self
        def _hx_local_0(key,value):
            _gthis.saveObject(key,value,toLatency)
            if ((fromLatency == apptimize_support_persistence_ABTPersistence.HIGH_LATENCY) and _gthis.deleteHighLatencyOnSync()):
                _gthis.save(key,None,fromLatency)
            if (callback is not None):
                callback(key,value)
        onCallback = _hx_local_0
        self.loadObject(key,fromLatency,onCallback)

    def deleteHighLatencyOnSync(self):
        return True

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._lowLatencyStorage = None
        _hx_o._highLatencyStorage = None
apptimize_support_persistence_ABTPISmartStorage._hx_class = apptimize_support_persistence_ABTPISmartStorage
_hx_classes["apptimize.support.persistence.ABTPISmartStorage"] = apptimize_support_persistence_ABTPISmartStorage


class apptimize_support_persistence_ABTPersistence:
    _hx_class_name = "apptimize.support.persistence.ABTPersistence"
    __slots__ = ()
    _hx_statics = ["LOW_LATENCY", "HIGH_LATENCY", "ALL_LATENCY", "kMetadataKey", "kUserIDKey", "kAnonymousGuidKey", "kCustomPropertiesKey", "kInternalPropertiesKey", "kResultLogsKey", "kResultPostsKey", "kResultPostsListKey", "kResultEntrySequenceKey", "kResultEntryTimestampKey", "kApptimizeVersionKey", "kLockAccessKey", "kPostManagementKey", "kResultLastSubmitTimeKey", "kMetadataLastCheckTimeKey", "kDisabledVersions", "_persistentInterface", "getPersistentInterface", "shutdown", "loadFromHighLatency", "saveToHighLatency", "clear", "saveString", "saveObject", "loadString", "loadObject"]
    _persistentInterface = None

    @staticmethod
    def getPersistentInterface():
        if (apptimize_support_persistence_ABTPersistence._persistentInterface is None):
            if apptimize_support_properties_ABTConfigProperties.sharedInstance().isPropertyAvailable(apptimize_support_properties_ABTConfigProperties.STORAGE_TYPE_KEY):
                if (apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.STORAGE_TYPE_KEY) == "memory"):
                    apptimize_support_persistence_ABTPersistence._persistentInterface = apptimize_support_persistence_ABTPICacheStorage()
                    return apptimize_support_persistence_ABTPersistence._persistentInterface
            apptimize_support_persistence_ABTPersistence._persistentInterface = apptimize_support_persistence_ABTPISmartStorage(apptimize_support_persistence_ABTPICacheStorage(),apptimize_support_persistence_ABTPIDiskStorage())
        return apptimize_support_persistence_ABTPersistence._persistentInterface

    @staticmethod
    def shutdown():
        apptimize_support_persistence_ABTPersistence._persistentInterface = None

    @staticmethod
    def loadFromHighLatency(callback):
        keys = [apptimize_support_persistence_ABTPersistence.kMetadataKey, apptimize_support_persistence_ABTPersistence.kUserIDKey, apptimize_support_persistence_ABTPersistence.kAnonymousGuidKey, apptimize_support_persistence_ABTPersistence.kCustomPropertiesKey, apptimize_support_persistence_ABTPersistence.kInternalPropertiesKey, apptimize_support_persistence_ABTPersistence.kResultLogsKey, apptimize_support_persistence_ABTPersistence.kResultPostsKey, apptimize_support_persistence_ABTPersistence.kResultEntrySequenceKey, apptimize_support_persistence_ABTPersistence.kResultEntryTimestampKey, apptimize_support_persistence_ABTPersistence.kApptimizeVersionKey, apptimize_support_persistence_ABTPersistence.kLockAccessKey, apptimize_support_persistence_ABTPersistence.kPostManagementKey, apptimize_support_persistence_ABTPersistence.kResultLastSubmitTimeKey, apptimize_support_persistence_ABTPersistence.kMetadataLastCheckTimeKey, apptimize_support_persistence_ABTPersistence.kResultPostsListKey]
        syncedKeys = list(keys)
        def _hx_local_0(key,value):
            python_internal_ArrayImpl.remove(syncedKeys,key)
            if (len(syncedKeys) == 0):
                callback()
        onSync = _hx_local_0
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.acquire()
        try:
            _g = 0
            while (_g < len(keys)):
                key = (keys[_g] if _g >= 0 and _g < len(keys) else None)
                _g = (_g + 1)
                apptimize_support_persistence_ABTPersistence.getPersistentInterface().sync(key,apptimize_support_persistence_ABTPersistence.HIGH_LATENCY,apptimize_support_persistence_ABTPersistence.LOW_LATENCY,onSync)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()

    @staticmethod
    def saveToHighLatency():
        keys = [apptimize_support_persistence_ABTPersistence.kMetadataKey, apptimize_support_persistence_ABTPersistence.kUserIDKey, apptimize_support_persistence_ABTPersistence.kAnonymousGuidKey, apptimize_support_persistence_ABTPersistence.kCustomPropertiesKey, apptimize_support_persistence_ABTPersistence.kInternalPropertiesKey, apptimize_support_persistence_ABTPersistence.kResultLogsKey, apptimize_support_persistence_ABTPersistence.kResultPostsKey, apptimize_support_persistence_ABTPersistence.kResultEntrySequenceKey, apptimize_support_persistence_ABTPersistence.kResultEntryTimestampKey, apptimize_support_persistence_ABTPersistence.kApptimizeVersionKey, apptimize_support_persistence_ABTPersistence.kLockAccessKey, apptimize_support_persistence_ABTPersistence.kPostManagementKey, apptimize_support_persistence_ABTPersistence.kResultLastSubmitTimeKey, apptimize_support_persistence_ABTPersistence.kMetadataLastCheckTimeKey, apptimize_support_persistence_ABTPersistence.kResultPostsListKey]
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.acquire()
        try:
            _g = 0
            while (_g < len(keys)):
                key = (keys[_g] if _g >= 0 and _g < len(keys) else None)
                _g = (_g + 1)
                apptimize_support_persistence_ABTPersistence.getPersistentInterface().sync(key,apptimize_support_persistence_ABTPersistence.LOW_LATENCY,apptimize_support_persistence_ABTPersistence.HIGH_LATENCY)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()

    @staticmethod
    def clear():
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.acquire()
        try:
            apptimize_support_persistence_ABTPersistence.getPersistentInterface().clear(apptimize_support_persistence_ABTPersistence.ALL_LATENCY)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()

    @staticmethod
    def saveString(key,value,latency = None,compress = None):
        if (latency is None):
            latency = 0
        if (compress is None):
            compress = False
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.acquire()
        try:
            try:
                apptimize_support_persistence_ABTPersistence.getPersistentInterface().save(key,value,latency,compress)
            except BaseException as _g:
                None
                unknown = haxe_Exception.caught(_g).unwrap()
                apptimize_ABTLogger.e(((("Unable to store \"" + ("null" if key is None else key)) + "\" to persistent storage. Submitting all pending results data. Error: ") + Std.string(unknown)),_hx_AnonObject({'fileName': "src/apptimize/support/persistence/ABTPersistence.hx", 'lineNumber': 213, 'className': "apptimize.support.persistence.ABTPersistence", 'methodName': "saveString"}))
                apptimize_Apptimize.flushTracking()
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()

    @staticmethod
    def saveObject(key,value,latency = None,compress = None):
        if (latency is None):
            latency = 0
        if (compress is None):
            compress = False
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.acquire()
        try:
            try:
                apptimize_support_persistence_ABTPersistence.getPersistentInterface().saveObject(key,value,latency,compress)
            except BaseException as _g:
                None
                unknown = haxe_Exception.caught(_g).unwrap()
                apptimize_ABTLogger.e(((("Unable to store \"" + ("null" if key is None else key)) + "\" to persistent storage. Submitting all pending results data. Error: ") + Std.string(unknown)),_hx_AnonObject({'fileName': "src/apptimize/support/persistence/ABTPersistence.hx", 'lineNumber': 224, 'className': "apptimize.support.persistence.ABTPersistence", 'methodName': "saveObject"}))
                apptimize_Apptimize.flushTracking()
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()

    @staticmethod
    def loadString(key,latency = None):
        if (latency is None):
            latency = 0
        result = None
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.acquire()
        try:
            try:
                result = apptimize_support_persistence_ABTPersistence.getPersistentInterface().load(key,latency)
            except BaseException as _g:
                None
                unknown = haxe_Exception.caught(_g).unwrap()
                apptimize_ABTLogger.e(((("Unable to retrieve \"" + ("null" if key is None else key)) + "\" from persistent storage. Error: ") + Std.string(unknown)),_hx_AnonObject({'fileName': "src/apptimize/support/persistence/ABTPersistence.hx", 'lineNumber': 240, 'className': "apptimize.support.persistence.ABTPersistence", 'methodName': "loadString"}))
                return None
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()
        return result

    @staticmethod
    def loadObject(key,latency = None):
        if (latency is None):
            latency = 0
        obj = None
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.acquire()
        try:
            try:
                obj = apptimize_support_persistence_ABTPersistence.getPersistentInterface().loadObject(key,latency,None)
            except BaseException as _g:
                None
                unknown = haxe_Exception.caught(_g).unwrap()
                apptimize_ABTLogger.e(((("Unable to retrieve \"" + ("null" if key is None else key)) + "\" from persistent storage. Error: ") + Std.string(unknown)),_hx_AnonObject({'fileName': "src/apptimize/support/persistence/ABTPersistence.hx", 'lineNumber': 253, 'className': "apptimize.support.persistence.ABTPersistence", 'methodName': "loadObject"}))
                return None
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()
            raise haxe_Exception.thrown(e)
        apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK.release()
        return obj
apptimize_support_persistence_ABTPersistence._hx_class = apptimize_support_persistence_ABTPersistence
_hx_classes["apptimize.support.persistence.ABTPersistence"] = apptimize_support_persistence_ABTPersistence


class apptimize_support_properties_ABTProperties:
    _hx_class_name = "apptimize.support.properties.ABTProperties"
    __slots__ = ("availableProperties", "PROPERTYLOCK")
    _hx_fields = ["availableProperties", "PROPERTYLOCK"]
    _hx_methods = ["setPropertyDefaults", "isPropertyAvailable", "valueForProperty", "setProperty", "setProperties"]

    def __init__(self):
        self.PROPERTYLOCK = apptimize_util_ABTDataLock.getNewLock("property_lock")
        self.availableProperties = haxe_ds_StringMap()
        self.PROPERTYLOCK.acquire()
        try:
            self.availableProperties = haxe_ds_StringMap()
            self.setPropertyDefaults()
        except BaseException as _g:
            e = haxe_Exception.caught(_g).unwrap()
            self.PROPERTYLOCK.release()
            raise haxe_Exception.thrown(e)
        self.PROPERTYLOCK.release()

    def setPropertyDefaults(self):
        pass

    def isPropertyAvailable(self,propertyName):
        property = None
        self.PROPERTYLOCK.acquire()
        try:
            property = self.availableProperties.h.get(propertyName,None)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            self.PROPERTYLOCK.release()
            raise haxe_Exception.thrown(e)
        self.PROPERTYLOCK.release()
        return (property is not None)

    def valueForProperty(self,propertyName):
        property = None
        self.PROPERTYLOCK.acquire()
        try:
            property = self.availableProperties.h.get(propertyName,None)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            self.PROPERTYLOCK.release()
            raise haxe_Exception.thrown(e)
        self.PROPERTYLOCK.release()
        return property

    def setProperty(self,key,value):
        self.PROPERTYLOCK.acquire()
        try:
            self.availableProperties.h[key] = value
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            self.PROPERTYLOCK.release()
            raise haxe_Exception.thrown(e)
        self.PROPERTYLOCK.release()

    def setProperties(self,stringMap):
        key = stringMap.keys()
        while key.hasNext():
            key1 = key.next()
            self.setProperty(key1,stringMap.h.get(key1,None))

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.availableProperties = None
        _hx_o.PROPERTYLOCK = None
apptimize_support_properties_ABTProperties._hx_class = apptimize_support_properties_ABTProperties
_hx_classes["apptimize.support.properties.ABTProperties"] = apptimize_support_properties_ABTProperties


class apptimize_support_properties_ABTApplicationProperties(apptimize_support_properties_ABTProperties):
    _hx_class_name = "apptimize.support.properties.ABTApplicationProperties"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["setPropertyDefaults", "addJSONProperties"]
    _hx_statics = ["_instance", "_sigilForApplicationNamespace", "sharedInstance", "getPlatformVersion", "formatPlatformVersion"]
    _hx_interfaces = []
    _hx_super = apptimize_support_properties_ABTProperties


    def __init__(self):
        super().__init__()

    def setPropertyDefaults(self):
        this1 = self.availableProperties
        v = apptimize_Apptimize.getApptimizeSDKVersion()
        this1.h["apptimize_version"] = v
        this1 = self.availableProperties
        v = apptimize_Apptimize.getApptimizeSDKPlatform()
        this1.h["apptimize_platform"] = v
        v = None
        self.availableProperties.h["app_version"] = v
        v = None
        self.availableProperties.h["app_name"] = v
        this1 = self.availableProperties
        v = apptimize_support_properties_ABTApplicationProperties.getPlatformVersion()
        this1.h["system_version"] = v

    def addJSONProperties(self,jsonProperties):
        key = self.availableProperties.keys()
        while key.hasNext():
            key1 = key.next()
            k = (HxOverrides.stringOrNull(apptimize_support_properties_ABTApplicationProperties._sigilForApplicationNamespace) + ("null" if key1 is None else key1))
            v = self.availableProperties.h.get(key1,None)
            jsonProperties.h[k] = v
    _instance = None

    @staticmethod
    def sharedInstance():
        if (apptimize_support_properties_ABTApplicationProperties._instance is None):
            apptimize_support_properties_ABTApplicationProperties._instance = apptimize_support_properties_ABTApplicationProperties()
        return apptimize_support_properties_ABTApplicationProperties._instance

    @staticmethod
    def getPlatformVersion():
        return apptimize_support_properties_ABTApplicationProperties.formatPlatformVersion(python_lib_Sys.version_info)

    @staticmethod
    def formatPlatformVersion(systemVersion):
        return ((((Std.string(Reflect.field(systemVersion,"major")) + ".") + Std.string(Reflect.field(systemVersion,"minor"))) + ".") + Std.string(Reflect.field(systemVersion,"micro")))

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_support_properties_ABTApplicationProperties._hx_class = apptimize_support_properties_ABTApplicationProperties
_hx_classes["apptimize.support.properties.ABTApplicationProperties"] = apptimize_support_properties_ABTApplicationProperties


class apptimize_support_properties_ABTConfigProperties(apptimize_support_properties_ABTProperties):
    _hx_class_name = "apptimize.support.properties.ABTConfigProperties"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["setPropertyDefaults"]
    _hx_statics = ["META_DATA_URL_KEY", "META_DATA_URL_LL_KEY", "META_DATA_URL_HL_KEY", "LOG_LEVEL_KEY", "FOREGROUND_PERIOD_MS_KEY", "RESULT_POST_DELAY_MS_KEY", "THREADING_ENABLED_KEY", "RESULT_POST_THREAD_POOL_SIZE_KEY", "ALTERATION_CACHE_SIZE_KEY", "RESULTS_CACHE_SIZE_KEY", "MAXIMUM_RESULT_ENTRIES_KEY", "MAXIMUM_PENDING_RESULTS_KEY", "METADATA_POLLING_INTERVAL_MS_KEY", "METADATA_POLLING_BACKGROUND_INTERVAL_MS_KEY", "EXCEPTIONS_ENABLED_KEY", "MAXIMUM_RESULT_POST_FAILURE_KEY", "MAXIMUM_RESULT_POST_SENDER_TIMEOUT_MS_KEY", "STORAGE_TYPE_KEY", "AUTOMATIC_SHUTDOWN_HOOK", "APPTIMIZE_ENVIRONMENT_KEY", "APPTIMIZE_REGION_KEY", "COMPRESS_PERSISTENCE_STORE_KEY", "GROUPS_BASE_URL_KEY", "REACT_NATIVE_STORAGE_KEY", "LOCAL_DISK_STORAGE_PATH_KEY", "_instance", "sharedInstance"]
    _hx_interfaces = []
    _hx_super = apptimize_support_properties_ABTProperties


    def __init__(self):
        super().__init__()

    def setPropertyDefaults(self):
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.META_DATA_URL_LL_KEY] = "https://md-ll.apptimize.com/api/metadata/v4/"
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.META_DATA_URL_HL_KEY] = "https://md-hl.apptimize.com/api/metadata/v4/"
        v = None
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY] = v
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.LOG_LEVEL_KEY] = "LOG_LEVEL_WARN"
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.FOREGROUND_PERIOD_MS_KEY] = 10000
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.RESULT_POST_DELAY_MS_KEY] = 60000
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.ALTERATION_CACHE_SIZE_KEY] = 10
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.RESULTS_CACHE_SIZE_KEY] = 10
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.MAXIMUM_RESULT_ENTRIES_KEY] = 1000
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.MAXIMUM_PENDING_RESULTS_KEY] = 1000
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.METADATA_POLLING_INTERVAL_MS_KEY] = 600000
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.MAXIMUM_RESULT_POST_FAILURE_KEY] = 3
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.MAXIMUM_RESULT_POST_SENDER_TIMEOUT_MS_KEY] = 3000
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.METADATA_POLLING_BACKGROUND_INTERVAL_MS_KEY] = 86400000
        v = None
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.STORAGE_TYPE_KEY] = v
        v = None
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.APPTIMIZE_ENVIRONMENT_KEY] = v
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.AUTOMATIC_SHUTDOWN_HOOK] = True
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY] = "https://mapi.apptimize.com"
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.LOCAL_DISK_STORAGE_PATH_KEY] = "data/apptimize/"
        v = None
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.REACT_NATIVE_STORAGE_KEY] = v
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.THREADING_ENABLED_KEY] = True
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.RESULT_POST_THREAD_POOL_SIZE_KEY] = 20
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.EXCEPTIONS_ENABLED_KEY] = True
        self.availableProperties.h[apptimize_support_properties_ABTConfigProperties.COMPRESS_PERSISTENCE_STORE_KEY] = False
    _instance = None

    @staticmethod
    def sharedInstance():
        if (apptimize_support_properties_ABTConfigProperties._instance is None):
            apptimize_support_properties_ABTConfigProperties._instance = apptimize_support_properties_ABTConfigProperties()
        return apptimize_support_properties_ABTConfigProperties._instance

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_support_properties_ABTConfigProperties._hx_class = apptimize_support_properties_ABTConfigProperties
_hx_classes["apptimize.support.properties.ABTConfigProperties"] = apptimize_support_properties_ABTConfigProperties

class apptimize_support_properties_CustomPropertyNamespace(Enum):
    __slots__ = ()
    _hx_class_name = "apptimize.support.properties.CustomPropertyNamespace"
    _hx_constructs = ["UserAttribute", "ApptimizeLocal", "ApptimizeInternal"]
apptimize_support_properties_CustomPropertyNamespace.UserAttribute = apptimize_support_properties_CustomPropertyNamespace("UserAttribute", 0, ())
apptimize_support_properties_CustomPropertyNamespace.ApptimizeLocal = apptimize_support_properties_CustomPropertyNamespace("ApptimizeLocal", 1, ())
apptimize_support_properties_CustomPropertyNamespace.ApptimizeInternal = apptimize_support_properties_CustomPropertyNamespace("ApptimizeInternal", 2, ())
apptimize_support_properties_CustomPropertyNamespace._hx_class = apptimize_support_properties_CustomPropertyNamespace
_hx_classes["apptimize.support.properties.CustomPropertyNamespace"] = apptimize_support_properties_CustomPropertyNamespace


class apptimize_support_properties_ABTCustomProperties(apptimize_support_properties_ABTProperties):
    _hx_class_name = "apptimize.support.properties.ABTCustomProperties"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["setPropertyDefaults", "setProperty", "setPropertyForNamespace", "sigilForNamespace", "valueForNamespacedProperty", "addJSONProperties"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = apptimize_support_properties_ABTProperties


    def __init__(self):
        super().__init__()

    def setPropertyDefaults(self):
        pass

    def setProperty(self,key,value):
        self.setPropertyForNamespace(key,value,apptimize_support_properties_CustomPropertyNamespace.UserAttribute)

    def setPropertyForNamespace(self,key,value,namespace):
        super().setProperty((HxOverrides.stringOrNull(self.sigilForNamespace(namespace)) + ("null" if key is None else key)),value)

    def sigilForNamespace(self,namespace):
        tmp = namespace.index
        if (tmp == 0):
            return "%"
        elif (tmp == 1):
            return "l"
        elif (tmp == 2):
            return "^"
        else:
            pass

    def valueForNamespacedProperty(self,propertyName,namespace):
        return super().valueForProperty((HxOverrides.stringOrNull(self.sigilForNamespace(namespace)) + ("null" if propertyName is None else propertyName)))

    def addJSONProperties(self,jsonProperties):
        key = self.availableProperties.keys()
        while key.hasNext():
            key1 = key.next()
            if ((("" if ((0 >= len(key1))) else key1[0])) != self.sigilForNamespace(apptimize_support_properties_CustomPropertyNamespace.ApptimizeLocal)):
                v = self.availableProperties.h.get(key1,None)
                jsonProperties.h[key1] = v

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_support_properties_ABTCustomProperties._hx_class = apptimize_support_properties_ABTCustomProperties
_hx_classes["apptimize.support.properties.ABTCustomProperties"] = apptimize_support_properties_ABTCustomProperties


class apptimize_support_properties_ABTInternalProperties(apptimize_support_properties_ABTCustomProperties):
    _hx_class_name = "apptimize.support.properties.ABTInternalProperties"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["isPropertyAvailable", "valueForProperty", "setProperty", "_loadProperties", "_saveProperties", "setPropertyForNamespace", "valueForNamespacedProperty"]
    _hx_statics = ["_instance", "sharedInstance"]
    _hx_interfaces = []
    _hx_super = apptimize_support_properties_ABTCustomProperties


    def __init__(self):
        super().__init__()

    def isPropertyAvailable(self,propertyName):
        self._loadProperties()
        return super().isPropertyAvailable(propertyName)

    def valueForProperty(self,propertyName):
        self._loadProperties()
        return self.availableProperties.h.get(propertyName,None)

    def setProperty(self,key,value):
        self.setPropertyForNamespace(key,value,apptimize_support_properties_CustomPropertyNamespace.ApptimizeInternal)

    def _loadProperties(self):
        self.availableProperties = apptimize_support_persistence_ABTPersistence.loadObject(apptimize_support_persistence_ABTPersistence.kInternalPropertiesKey)
        if (self.availableProperties is None):
            self.availableProperties = haxe_ds_StringMap()

    def _saveProperties(self):
        apptimize_support_persistence_ABTPersistence.saveObject(apptimize_support_persistence_ABTPersistence.kInternalPropertiesKey,self.availableProperties)

    def setPropertyForNamespace(self,key,value,namespace):
        self._loadProperties()
        super().setPropertyForNamespace(key,value,namespace)
        self._saveProperties()

    def valueForNamespacedProperty(self,propertyName,namespace):
        self._loadProperties()
        return super().valueForNamespacedProperty(propertyName,namespace)
    _instance = None

    @staticmethod
    def sharedInstance():
        if (apptimize_support_properties_ABTInternalProperties._instance is None):
            apptimize_support_properties_ABTInternalProperties._instance = apptimize_support_properties_ABTInternalProperties()
        return apptimize_support_properties_ABTInternalProperties._instance

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_support_properties_ABTInternalProperties._hx_class = apptimize_support_properties_ABTInternalProperties
_hx_classes["apptimize.support.properties.ABTInternalProperties"] = apptimize_support_properties_ABTInternalProperties


class apptimize_util_DefaultPlatformLock:
    _hx_class_name = "apptimize.util.DefaultPlatformLock"
    __slots__ = ()
    _hx_methods = ["acquire", "release", "hxUnserialize"]
    _hx_interfaces = [apptimize_util_PlatformLock]

    def __init__(self):
        pass

    def acquire(self):
        return True

    def release(self):
        return

    def hxUnserialize(self,u):
        pass

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
apptimize_util_DefaultPlatformLock._hx_class = apptimize_util_DefaultPlatformLock
_hx_classes["apptimize.util.DefaultPlatformLock"] = apptimize_util_DefaultPlatformLock


class apptimize_util_ABTDispatchTask:
    _hx_class_name = "apptimize.util.ABTDispatchTask"
    __slots__ = ("task", "startTimestampMs")
    _hx_fields = ["task", "startTimestampMs"]

    def __init__(self,task,delay):
        self.task = task
        self.startTimestampMs = ((Date.now().date.timestamp() * 1000) + delay)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.task = None
        _hx_o.startTimestampMs = None
apptimize_util_ABTDispatchTask._hx_class = apptimize_util_ABTDispatchTask
_hx_classes["apptimize.util.ABTDispatchTask"] = apptimize_util_ABTDispatchTask


class apptimize_util_ABTException:
    _hx_class_name = "apptimize.util.ABTException"
    __slots__ = ()
    _hx_statics = ["throwException"]

    @staticmethod
    def throwException(message):
        if apptimize_support_properties_ABTConfigProperties.sharedInstance().valueForProperty(apptimize_support_properties_ABTConfigProperties.EXCEPTIONS_ENABLED_KEY):
            raise haxe_Exception.thrown(message)
apptimize_util_ABTException._hx_class = apptimize_util_ABTException
_hx_classes["apptimize.util.ABTException"] = apptimize_util_ABTException


class apptimize_util_ABTHash:
    _hx_class_name = "apptimize.util.ABTHash"
    __slots__ = ()
    _hx_statics = ["Sha1"]

    @staticmethod
    def Sha1(obj):
        return haxe_crypto_Sha1.make(obj)
apptimize_util_ABTHash._hx_class = apptimize_util_ABTHash
_hx_classes["apptimize.util.ABTHash"] = apptimize_util_ABTHash


class apptimize_util_ABTInt64Utils:
    _hx_class_name = "apptimize.util.ABTInt64Utils"
    __slots__ = ()
    _hx_statics = ["toPreprocessedString", "_serializeInt64", "_deserializeInt64"]

    @staticmethod
    def toPreprocessedString(number):
        return (("wideInt_" + HxOverrides.stringOrNull(haxe__Int64_Int64_Impl_.toString(number))) + "_wideInt")

    @staticmethod
    def _serializeInt64(value,s):
        s.serialize(value.high)
        s.serialize(value.low)

    @staticmethod
    def _deserializeInt64(u):
        this1 = haxe__Int64____Int64(u.unserialize(),u.unserialize())
        return this1
apptimize_util_ABTInt64Utils._hx_class = apptimize_util_ABTInt64Utils
_hx_classes["apptimize.util.ABTInt64Utils"] = apptimize_util_ABTInt64Utils


class apptimize_util_ABTJSONUtils:
    _hx_class_name = "apptimize.util.ABTJSONUtils"
    __slots__ = ()
    _hx_statics = ["stringify"]

    @staticmethod
    def stringify(json):
        jsonString = haxe_format_JsonPrinter.print(json,None,None)
        jsonString = StringTools.replace(jsonString,"\"wideInt_","")
        jsonString = StringTools.replace(jsonString,"_wideInt\"","")
        return jsonString
apptimize_util_ABTJSONUtils._hx_class = apptimize_util_ABTJSONUtils
_hx_classes["apptimize.util.ABTJSONUtils"] = apptimize_util_ABTJSONUtils


class apptimize_util_ABTLRUCache:
    _hx_class_name = "apptimize.util.ABTLRUCache"
    __slots__ = ("_cacheSize", "_list", "_map", "cacheLock")
    _hx_fields = ["_cacheSize", "_list", "_map", "cacheLock"]
    _hx_methods = ["clear", "hasKey", "getValue", "remove", "insert", "hxSerialize", "hxUnserialize", "didUnserialize", "initMissingFields"]

    def __init__(self,cacheSize):
        self._map = None
        self._list = None
        self.cacheLock = apptimize_util_ABTDataLock.getNewLock("ABTLRUCache_lock")
        self._cacheSize = cacheSize
        self.clear()

    def clear(self,callback = None,dispatchQueue = None):
        self.cacheLock.acquire()
        try:
            if (callback is not None):
                _g = 0
                _g1 = self._list
                while (_g < len(_g1)):
                    id = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                    _g = (_g + 1)
                    value = [self._map.h.get(id,None)]
                    def _hx_local_2(value):
                        def _hx_local_1():
                            callback((value[0] if 0 < len(value) else None))
                        return _hx_local_1
                    task = _hx_local_2(value)
                    if (dispatchQueue is not None):
                        dispatchQueue.dispatch(task,0)
                    else:
                        apptimize_util_ABTDispatch.dispatchImmediately(task)
            self._list = list()
            self._map = haxe_ds_StringMap()
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            self.cacheLock.release()
            raise haxe_Exception.thrown(e)
        self.cacheLock.release()

    def hasKey(self,key):
        result = False
        self.cacheLock.acquire()
        try:
            result = (self._map.h.get(key,None) is not None)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            self.cacheLock.release()
            raise haxe_Exception.thrown(e)
        self.cacheLock.release()
        return result

    def getValue(self,key):
        result = None
        self.cacheLock.acquire()
        try:
            if self.hasKey(key):
                result = self._map.h.get(key,None)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            self.cacheLock.release()
            raise haxe_Exception.thrown(e)
        self.cacheLock.release()
        return result

    def remove(self,key,callback = None,dispatchQueue = None):
        self.cacheLock.acquire()
        try:
            if (not self.hasKey(key)):
                return
            if (callback is not None):
                value = self._map.h.get(key,None)
                def _hx_local_0():
                    callback(value)
                task = _hx_local_0
                if (dispatchQueue is not None):
                    dispatchQueue.dispatch(task,0)
                else:
                    apptimize_util_ABTDispatch.dispatchImmediately(task)
            python_internal_ArrayImpl.remove(self._list,key)
            self._map.remove(key)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            self.cacheLock.release()
            raise haxe_Exception.thrown(e)
        self.cacheLock.release()

    def insert(self,key,value,callback = None,dispatchQueue = None):
        self.cacheLock.acquire()
        try:
            if self.hasKey(key):
                self._map.h[key] = value
                python_internal_ArrayImpl.remove(self._list,key)
                _this = self._list
                _this.append(key)
            else:
                self._map.h[key] = value
                _this = self._list
                _this.append(key)
                if (len(self._list) > self._cacheSize):
                    _this = self._list
                    id = (None if ((len(_this) == 0)) else _this.pop(0))
                    if (callback is not None):
                        value = self._map.h.get(id,None)
                        def _hx_local_0():
                            callback(value)
                        task = _hx_local_0
                        if (dispatchQueue is not None):
                            dispatchQueue.dispatch(task,0)
                        else:
                            apptimize_util_ABTDispatch.dispatchImmediately(task)
                    self._map.remove(id)
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            self.cacheLock.release()
            raise haxe_Exception.thrown(e)
        self.cacheLock.release()

    def hxSerialize(self,s):
        _g = haxe_ds_StringMap()
        _g.h["_cacheSize"] = self._cacheSize
        _g.h["_list"] = self._list
        _g.h["_map"] = self._map
        values = _g
        s.serialize(values)

    def hxUnserialize(self,u):
        deserialized = u.unserialize()
        self._cacheSize = deserialized.h.get("_cacheSize",None)
        self._list = deserialized.h.get("_list",None)
        self._map = deserialized.h.get("_map",None)
        self.initMissingFields()

    def didUnserialize(self):
        self.initMissingFields()

    def initMissingFields(self):
        if (self.cacheLock is None):
            self.cacheLock = apptimize_util_ABTDataLock.getNewLock("ABTLRUCache_lock")

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._cacheSize = None
        _hx_o._list = None
        _hx_o._map = None
        _hx_o.cacheLock = None
apptimize_util_ABTLRUCache._hx_class = apptimize_util_ABTLRUCache
_hx_classes["apptimize.util.ABTLRUCache"] = apptimize_util_ABTLRUCache


class apptimize_util_ABTTimer:
    _hx_class_name = "apptimize.util.ABTTimer"
    _hx_fields = ["thread", "interval", "startTime", "event"]
    _hx_methods = ["stop", "run"]

    def __init__(self,time_ms):
        self.startTime = None
        self.interval = None
        self.thread = None
        self.event = apptimize_native_python_Event()
        _gthis = self
        def _hx_local_2():
            while (not _gthis.event.is_set()):
                _gthis1 = _gthis
                def _hx_local_1():
                    _gthis1.startTime = (_gthis1.startTime + _gthis.interval)
                    return _gthis1.startTime
                next = ((_hx_local_1()) - python_lib_Time.time())
                if (not _gthis.event.wait(next)):
                    localRun = _gthis.run
                    if (localRun is not None):
                        localRun()
        worker = _hx_local_2
        self.interval = (time_ms / 1000.0)
        self.thread = python_lib_threading_Thread(**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'target': worker})))
        self.thread.daemon = True
        _hx_local_3 = self.thread
        _hx_local_4 = _hx_local_3.name
        _hx_local_3.name = (("null" if _hx_local_4 is None else _hx_local_4) + " ~ Apptimize Timer Thread")
        _hx_local_3.name
        self.startTime = python_lib_Time.time()
        self.thread.start()

    def stop(self):
        self.run = None
        self.event.set()

    def run(self):
        pass

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.thread = None
        _hx_o.interval = None
        _hx_o.startTime = None
        _hx_o.event = None
apptimize_util_ABTTimer._hx_class = apptimize_util_ABTTimer
_hx_classes["apptimize.util.ABTTimer"] = apptimize_util_ABTTimer


class apptimize_util_ABTTypes:
    _hx_class_name = "apptimize.util.ABTTypes"
    __slots__ = ()
    _hx_statics = ["isString", "isNullOrString"]

    @staticmethod
    def isString(string):
        _g = Type.typeof(string)
        if (_g.index == 6):
            c = _g.params[0]
            if (Type.getClassName(c) == "String"):
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def isNullOrString(string):
        if (string is not None):
            return apptimize_util_ABTTypes.isString(string)
        else:
            return True
apptimize_util_ABTTypes._hx_class = apptimize_util_ABTTypes
_hx_classes["apptimize.util.ABTTypes"] = apptimize_util_ABTTypes

class apptimize_util_ArrayType(Enum):
    __slots__ = ()
    _hx_class_name = "apptimize.util.ArrayType"
    _hx_constructs = ["Int", "Bool", "Double", "String", "VariantInfo"]
apptimize_util_ArrayType.Int = apptimize_util_ArrayType("Int", 0, ())
apptimize_util_ArrayType.Bool = apptimize_util_ArrayType("Bool", 1, ())
apptimize_util_ArrayType.Double = apptimize_util_ArrayType("Double", 2, ())
apptimize_util_ArrayType.String = apptimize_util_ArrayType("String", 3, ())
apptimize_util_ArrayType.VariantInfo = apptimize_util_ArrayType("VariantInfo", 4, ())
apptimize_util_ArrayType._hx_class = apptimize_util_ArrayType
_hx_classes["apptimize.util.ArrayType"] = apptimize_util_ArrayType


class apptimize_util_ABTUtilArray:
    _hx_class_name = "apptimize.util.ABTUtilArray"
    __slots__ = ()
    _hx_statics = ["toNativeArray"]

    @staticmethod
    def toNativeArray(haxeArray,_hx_type):
        return haxeArray
apptimize_util_ABTUtilArray._hx_class = apptimize_util_ABTUtilArray
_hx_classes["apptimize.util.ABTUtilArray"] = apptimize_util_ABTUtilArray


class apptimize_util_ABTUtilDictionary:
    _hx_class_name = "apptimize.util.ABTUtilDictionary"
    __slots__ = ()
    _hx_statics = ["dynamicToNativeDictionary", "stringMapToNativeDictionary", "nativeObjectToStringMap", "nativeDictionaryToStringMap", "dynamicObjectToStringMap", "filterNullValues"]

    @staticmethod
    def dynamicToNativeDictionary(dynamicMap):
        pythonDict = dict()
        _hx_dict = dynamicMap
        if (_hx_dict is not None):
            _g = 0
            _g1 = python_Boot.fields(_hx_dict)
            while (_g < len(_g1)):
                key = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                k = key
                pythonDict[k] = Reflect.field(_hx_dict,key)
        return pythonDict

    @staticmethod
    def stringMapToNativeDictionary(stringMap):
        pythonDict = dict()
        if (stringMap is not None):
            key = stringMap.keys()
            while key.hasNext():
                key1 = key.next()
                k = key1
                pythonDict[k] = stringMap.h.get(key1,None)
        return pythonDict

    @staticmethod
    def nativeObjectToStringMap(nativeMap):
        if (Type.typeof(nativeMap) == ValueType.TObject):
            return apptimize_util_ABTUtilDictionary.dynamicObjectToStringMap(nativeMap)
        if (Type.getClass(nativeMap) == haxe_ds_StringMap):
            return nativeMap
        return apptimize_util_ABTUtilDictionary.nativeDictionaryToStringMap(nativeMap)

    @staticmethod
    def nativeDictionaryToStringMap(nativeMap):
        pythonDict = nativeMap
        _hx_map = haxe_ds_StringMap()
        if (pythonDict is not None):
            key = python_HaxeIterator(iter(pythonDict.keys()))
            while key.hasNext():
                key1 = key.next()
                value = pythonDict.get(key1)
                _hx_map.h[key1] = value
        return _hx_map

    @staticmethod
    def dynamicObjectToStringMap(object):
        _hx_map = haxe_ds_StringMap()
        fields = python_Boot.fields(object)
        _g = 0
        while (_g < len(fields)):
            field = (fields[_g] if _g >= 0 and _g < len(fields) else None)
            _g = (_g + 1)
            value = Reflect.getProperty(object,field)
            _hx_map.h[field] = value
        return _hx_map

    @staticmethod
    def filterNullValues(_hx_map):
        result = haxe_ds_StringMap()
        key = _hx_map.keys()
        while key.hasNext():
            key1 = key.next()
            value = _hx_map.h.get(key1,None)
            if (value is not None):
                result.h[key1] = value
        return result
apptimize_util_ABTUtilDictionary._hx_class = apptimize_util_ABTUtilDictionary
_hx_classes["apptimize.util.ABTUtilDictionary"] = apptimize_util_ABTUtilDictionary


class apptimize_util_ABTUtilGzip:
    _hx_class_name = "apptimize.util.ABTUtilGzip"
    __slots__ = ()
    _hx_statics = ["jsonSignatureLength", "decompressBytes", "decompress"]

    @staticmethod
    def jsonSignatureLength(_hx_bytes):
        b = haxe_io_Bytes.ofData(_hx_bytes)
        _hx_len = ((b.b[0] << 8) | b.b[1])
        return _hx_len

    @staticmethod
    def decompressBytes(_hx_bytes):
        arrayBuffer = haxe_io__UInt8Array_UInt8Array_Impl_.fromBytes(_hx_bytes)
        inflator = pako_Inflate()
        inflator.push(arrayBuffer,True)
        if (inflator.err != 0):
            apptimize_ABTLogger.e("Error decompressing data. ${inflator.err}): ${inflator.msg}",_hx_AnonObject({'fileName': "src/apptimize/util/ABTUtilGzip.hx", 'lineNumber': 58, 'className': "apptimize.util.ABTUtilGzip", 'methodName': "decompressBytes"}))
            return None
        return inflator.result.bytes

    @staticmethod
    def decompress(_hx_bytes):
        bds = haxe_io_Bytes.ofData(_hx_bytes)
        _hx_len = apptimize_util_ABTUtilGzip.jsonSignatureLength(_hx_bytes)
        dataLength = bds.length
        sigLength = (_hx_len + 2)
        zippedLength = (dataLength - sigLength)
        orig = haxe_io_Bytes.ofData(_hx_bytes)
        bd = orig.sub(sigLength,zippedLength)
        return apptimize_util_ABTUtilGzip.decompressBytes(bd)
apptimize_util_ABTUtilGzip._hx_class = apptimize_util_ABTUtilGzip
_hx_classes["apptimize.util.ABTUtilGzip"] = apptimize_util_ABTUtilGzip

class haxe_StackItem(Enum):
    __slots__ = ()
    _hx_class_name = "haxe.StackItem"
    _hx_constructs = ["CFunction", "Module", "FilePos", "Method", "LocalFunction"]

    @staticmethod
    def Module(m):
        return haxe_StackItem("Module", 1, (m,))

    @staticmethod
    def FilePos(s,file,line,column = None):
        return haxe_StackItem("FilePos", 2, (s,file,line,column))

    @staticmethod
    def Method(classname,method):
        return haxe_StackItem("Method", 3, (classname,method))

    @staticmethod
    def LocalFunction(v = None):
        return haxe_StackItem("LocalFunction", 4, (v,))
haxe_StackItem.CFunction = haxe_StackItem("CFunction", 0, ())
haxe_StackItem._hx_class = haxe_StackItem
_hx_classes["haxe.StackItem"] = haxe_StackItem


class haxe__CallStack_CallStack_Impl_:
    _hx_class_name = "haxe._CallStack.CallStack_Impl_"
    __slots__ = ()
    _hx_statics = ["callStack", "exceptionStack", "toString", "subtract", "equalItems", "itemToString"]

    @staticmethod
    def callStack():
        infos = python_lib_Traceback.extract_stack()
        if (len(infos) != 0):
            infos.pop()
        infos.reverse()
        return haxe_NativeStackTrace.toHaxe(infos)

    @staticmethod
    def exceptionStack(fullStack = None):
        if (fullStack is None):
            fullStack = False
        eStack = haxe_NativeStackTrace.toHaxe(haxe_NativeStackTrace.exceptionStack())
        return (eStack if fullStack else haxe__CallStack_CallStack_Impl_.subtract(eStack,haxe__CallStack_CallStack_Impl_.callStack()))

    @staticmethod
    def toString(stack):
        b = StringBuf()
        _g = 0
        _g1 = stack
        while (_g < len(_g1)):
            s = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            b.b.write("\nCalled from ")
            haxe__CallStack_CallStack_Impl_.itemToString(b,s)
        return b.b.getvalue()

    @staticmethod
    def subtract(this1,stack):
        startIndex = -1
        i = -1
        while True:
            i = (i + 1)
            tmp = i
            if (not ((tmp < len(this1)))):
                break
            _g = 0
            _g1 = len(stack)
            while (_g < _g1):
                j = _g
                _g = (_g + 1)
                if haxe__CallStack_CallStack_Impl_.equalItems((this1[i] if i >= 0 and i < len(this1) else None),python_internal_ArrayImpl._get(stack, j)):
                    if (startIndex < 0):
                        startIndex = i
                    i = (i + 1)
                    if (i >= len(this1)):
                        break
                else:
                    startIndex = -1
            if (startIndex >= 0):
                break
        if (startIndex >= 0):
            return this1[0:startIndex]
        else:
            return this1

    @staticmethod
    def equalItems(item1,item2):
        if (item1 is None):
            if (item2 is None):
                return True
            else:
                return False
        else:
            tmp = item1.index
            if (tmp == 0):
                if (item2 is None):
                    return False
                elif (item2.index == 0):
                    return True
                else:
                    return False
            elif (tmp == 1):
                if (item2 is None):
                    return False
                elif (item2.index == 1):
                    m2 = item2.params[0]
                    m1 = item1.params[0]
                    return (m1 == m2)
                else:
                    return False
            elif (tmp == 2):
                if (item2 is None):
                    return False
                elif (item2.index == 2):
                    item21 = item2.params[0]
                    file2 = item2.params[1]
                    line2 = item2.params[2]
                    col2 = item2.params[3]
                    col1 = item1.params[3]
                    line1 = item1.params[2]
                    file1 = item1.params[1]
                    item11 = item1.params[0]
                    if (((file1 == file2) and ((line1 == line2))) and ((col1 == col2))):
                        return haxe__CallStack_CallStack_Impl_.equalItems(item11,item21)
                    else:
                        return False
                else:
                    return False
            elif (tmp == 3):
                if (item2 is None):
                    return False
                elif (item2.index == 3):
                    class2 = item2.params[0]
                    method2 = item2.params[1]
                    method1 = item1.params[1]
                    class1 = item1.params[0]
                    if (class1 == class2):
                        return (method1 == method2)
                    else:
                        return False
                else:
                    return False
            elif (tmp == 4):
                if (item2 is None):
                    return False
                elif (item2.index == 4):
                    v2 = item2.params[0]
                    v1 = item1.params[0]
                    return (v1 == v2)
                else:
                    return False
            else:
                pass

    @staticmethod
    def itemToString(b,s):
        tmp = s.index
        if (tmp == 0):
            b.b.write("a C function")
        elif (tmp == 1):
            m = s.params[0]
            b.b.write("module ")
            s1 = Std.string(m)
            b.b.write(s1)
        elif (tmp == 2):
            s1 = s.params[0]
            file = s.params[1]
            line = s.params[2]
            col = s.params[3]
            if (s1 is not None):
                haxe__CallStack_CallStack_Impl_.itemToString(b,s1)
                b.b.write(" (")
            s2 = Std.string(file)
            b.b.write(s2)
            b.b.write(" line ")
            s2 = Std.string(line)
            b.b.write(s2)
            if (col is not None):
                b.b.write(" column ")
                s2 = Std.string(col)
                b.b.write(s2)
            if (s1 is not None):
                b.b.write(")")
        elif (tmp == 3):
            cname = s.params[0]
            meth = s.params[1]
            s1 = Std.string(("<unknown>" if ((cname is None)) else cname))
            b.b.write(s1)
            b.b.write(".")
            s1 = Std.string(meth)
            b.b.write(s1)
        elif (tmp == 4):
            n = s.params[0]
            b.b.write("local function #")
            s = Std.string(n)
            b.b.write(s)
        else:
            pass
haxe__CallStack_CallStack_Impl_._hx_class = haxe__CallStack_CallStack_Impl_
_hx_classes["haxe._CallStack.CallStack_Impl_"] = haxe__CallStack_CallStack_Impl_


class haxe_Exception(Exception):
    _hx_class_name = "haxe.Exception"
    __slots__ = ("_hx___nativeStack", "_hx___skipStack", "_hx___nativeException", "_hx___previousException")
    _hx_fields = ["__nativeStack", "__skipStack", "__nativeException", "__previousException"]
    _hx_methods = ["unwrap", "toString", "get_message", "get_native"]
    _hx_statics = ["caught", "thrown"]
    _hx_interfaces = []
    _hx_super = Exception


    def __init__(self,message,previous = None,native = None):
        self._hx___previousException = None
        self._hx___nativeException = None
        self._hx___nativeStack = None
        self._hx___skipStack = 0
        super().__init__(message)
        self._hx___previousException = previous
        if ((native is not None) and Std.isOfType(native,BaseException)):
            self._hx___nativeException = native
            self._hx___nativeStack = haxe_NativeStackTrace.exceptionStack()
        else:
            self._hx___nativeException = self
            infos = python_lib_Traceback.extract_stack()
            if (len(infos) != 0):
                infos.pop()
            infos.reverse()
            self._hx___nativeStack = infos

    def unwrap(self):
        return self._hx___nativeException

    def toString(self):
        return self.get_message()

    def get_message(self):
        return str(self)

    def get_native(self):
        return self._hx___nativeException

    @staticmethod
    def caught(value):
        if Std.isOfType(value,haxe_Exception):
            return value
        elif Std.isOfType(value,BaseException):
            return haxe_Exception(str(value),None,value)
        else:
            return haxe_ValueException(value,None,value)

    @staticmethod
    def thrown(value):
        if Std.isOfType(value,haxe_Exception):
            return value.get_native()
        elif Std.isOfType(value,BaseException):
            return value
        else:
            e = haxe_ValueException(value)
            e._hx___skipStack = (e._hx___skipStack + 1)
            return e

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._hx___nativeStack = None
        _hx_o._hx___skipStack = None
        _hx_o._hx___nativeException = None
        _hx_o._hx___previousException = None
haxe_Exception._hx_class = haxe_Exception
_hx_classes["haxe.Exception"] = haxe_Exception


class haxe__Int32_Int32_Impl_:
    _hx_class_name = "haxe._Int32.Int32_Impl_"
    __slots__ = ()
    _hx_statics = ["mul", "ucompare"]

    @staticmethod
    def mul(a,b):
        return ((((a * ((b & 65535))) + ((((((a * (HxOverrides.rshift(b, 16))) << 16)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)))) + (2 ** 31)) % (2 ** 32) - (2 ** 31))

    @staticmethod
    def ucompare(a,b):
        if (a < 0):
            if (b < 0):
                return (((((~b + (2 ** 31)) % (2 ** 32) - (2 ** 31)) - (((~a + (2 ** 31)) % (2 ** 32) - (2 ** 31)))) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            else:
                return 1
        if (b < 0):
            return -1
        else:
            return (((a - b) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
haxe__Int32_Int32_Impl_._hx_class = haxe__Int32_Int32_Impl_
_hx_classes["haxe._Int32.Int32_Impl_"] = haxe__Int32_Int32_Impl_


class haxe__Int64_Int64_Impl_:
    _hx_class_name = "haxe._Int64.Int64_Impl_"
    __slots__ = ()
    _hx_statics = ["toString", "divMod"]

    @staticmethod
    def toString(this1):
        i = this1
        b_high = 0
        b_low = 0
        if ((i.high == b_high) and ((i.low == b_low))):
            return "0"
        _hx_str = ""
        neg = False
        if (i.high < 0):
            neg = True
        this1 = haxe__Int64____Int64(0,10)
        ten = this1
        while True:
            b_high = 0
            b_low = 0
            if (not (((i.high != b_high) or ((i.low != b_low))))):
                break
            r = haxe__Int64_Int64_Impl_.divMod(i,ten)
            if (r.modulus.high < 0):
                x = r.modulus
                high = ((~x.high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                low = (((~x.low + 1) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                if (low == 0):
                    ret = high
                    high = (high + 1)
                    high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                this_high = high
                this_low = low
                _hx_str = (Std.string(this_low) + ("null" if _hx_str is None else _hx_str))
                x1 = r.quotient
                high1 = ((~x1.high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                low1 = (((~x1.low + 1) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                if (low1 == 0):
                    ret1 = high1
                    high1 = (high1 + 1)
                    high1 = ((high1 + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                this1 = haxe__Int64____Int64(high1,low1)
                i = this1
            else:
                _hx_str = (Std.string(r.modulus.low) + ("null" if _hx_str is None else _hx_str))
                i = r.quotient
        if neg:
            _hx_str = ("-" + ("null" if _hx_str is None else _hx_str))
        return _hx_str

    @staticmethod
    def divMod(dividend,divisor):
        if (divisor.high == 0):
            _g = divisor.low
            if (_g == 0):
                raise haxe_Exception.thrown("divide by zero")
            elif (_g == 1):
                this1 = haxe__Int64____Int64(dividend.high,dividend.low)
                this2 = haxe__Int64____Int64(0,0)
                return _hx_AnonObject({'quotient': this1, 'modulus': this2})
            else:
                pass
        divSign = ((dividend.high < 0) != ((divisor.high < 0)))
        modulus = None
        if (dividend.high < 0):
            high = ((~dividend.high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            low = (((~dividend.low + 1) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            if (low == 0):
                ret = high
                high = (high + 1)
                high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            this1 = haxe__Int64____Int64(high,low)
            modulus = this1
        else:
            this1 = haxe__Int64____Int64(dividend.high,dividend.low)
            modulus = this1
        if (divisor.high < 0):
            high = ((~divisor.high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            low = (((~divisor.low + 1) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            if (low == 0):
                ret = high
                high = (high + 1)
                high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            this1 = haxe__Int64____Int64(high,low)
            divisor = this1
        this1 = haxe__Int64____Int64(0,0)
        quotient = this1
        this1 = haxe__Int64____Int64(0,1)
        mask = this1
        while (not ((divisor.high < 0))):
            v = haxe__Int32_Int32_Impl_.ucompare(divisor.high,modulus.high)
            cmp = (v if ((v != 0)) else haxe__Int32_Int32_Impl_.ucompare(divisor.low,modulus.low))
            b = 1
            b = (b & 63)
            if (b == 0):
                this1 = haxe__Int64____Int64(divisor.high,divisor.low)
                divisor = this1
            elif (b < 32):
                this2 = haxe__Int64____Int64(((((((((divisor.high << b)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)) | HxOverrides.rshift(divisor.low, ((32 - b))))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)),((((divisor.low << b)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)))
                divisor = this2
            else:
                this3 = haxe__Int64____Int64(((((divisor.low << ((b - 32)))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)),0)
                divisor = this3
            b1 = 1
            b1 = (b1 & 63)
            if (b1 == 0):
                this4 = haxe__Int64____Int64(mask.high,mask.low)
                mask = this4
            elif (b1 < 32):
                this5 = haxe__Int64____Int64(((((((((mask.high << b1)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)) | HxOverrides.rshift(mask.low, ((32 - b1))))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)),((((mask.low << b1)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)))
                mask = this5
            else:
                this6 = haxe__Int64____Int64(((((mask.low << ((b1 - 32)))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)),0)
                mask = this6
            if (cmp >= 0):
                break
        while True:
            b_high = 0
            b_low = 0
            if (not (((mask.high != b_high) or ((mask.low != b_low))))):
                break
            v = haxe__Int32_Int32_Impl_.ucompare(modulus.high,divisor.high)
            if (((v if ((v != 0)) else haxe__Int32_Int32_Impl_.ucompare(modulus.low,divisor.low))) >= 0):
                this1 = haxe__Int64____Int64(((((quotient.high | mask.high)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)),((((quotient.low | mask.low)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)))
                quotient = this1
                high = (((modulus.high - divisor.high) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                low = (((modulus.low - divisor.low) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                if (haxe__Int32_Int32_Impl_.ucompare(modulus.low,divisor.low) < 0):
                    ret = high
                    high = (high - 1)
                    high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                this2 = haxe__Int64____Int64(high,low)
                modulus = this2
            b = 1
            b = (b & 63)
            if (b == 0):
                this3 = haxe__Int64____Int64(mask.high,mask.low)
                mask = this3
            elif (b < 32):
                this4 = haxe__Int64____Int64(HxOverrides.rshift(mask.high, b),((((((((mask.high << ((32 - b)))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)) | HxOverrides.rshift(mask.low, b))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)))
                mask = this4
            else:
                this5 = haxe__Int64____Int64(0,HxOverrides.rshift(mask.high, ((b - 32))))
                mask = this5
            b1 = 1
            b1 = (b1 & 63)
            if (b1 == 0):
                this6 = haxe__Int64____Int64(divisor.high,divisor.low)
                divisor = this6
            elif (b1 < 32):
                this7 = haxe__Int64____Int64(HxOverrides.rshift(divisor.high, b1),((((((((divisor.high << ((32 - b1)))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)) | HxOverrides.rshift(divisor.low, b1))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)))
                divisor = this7
            else:
                this8 = haxe__Int64____Int64(0,HxOverrides.rshift(divisor.high, ((b1 - 32))))
                divisor = this8
        if divSign:
            high = ((~quotient.high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            low = (((~quotient.low + 1) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            if (low == 0):
                ret = high
                high = (high + 1)
                high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            this1 = haxe__Int64____Int64(high,low)
            quotient = this1
        if (dividend.high < 0):
            high = ((~modulus.high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            low = (((~modulus.low + 1) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            if (low == 0):
                ret = high
                high = (high + 1)
                high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            this1 = haxe__Int64____Int64(high,low)
            modulus = this1
        return _hx_AnonObject({'quotient': quotient, 'modulus': modulus})
haxe__Int64_Int64_Impl_._hx_class = haxe__Int64_Int64_Impl_
_hx_classes["haxe._Int64.Int64_Impl_"] = haxe__Int64_Int64_Impl_


class haxe__Int64____Int64:
    _hx_class_name = "haxe._Int64.___Int64"
    __slots__ = ("high", "low")
    _hx_fields = ["high", "low"]

    def __init__(self,high,low):
        self.high = high
        self.low = low

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.high = None
        _hx_o.low = None
haxe__Int64____Int64._hx_class = haxe__Int64____Int64
_hx_classes["haxe._Int64.___Int64"] = haxe__Int64____Int64


class haxe_Int64Helper:
    _hx_class_name = "haxe.Int64Helper"
    __slots__ = ()
    _hx_statics = ["parseString", "fromFloat"]

    @staticmethod
    def parseString(sParam):
        base_high = 0
        base_low = 10
        this1 = haxe__Int64____Int64(0,0)
        current = this1
        this1 = haxe__Int64____Int64(0,1)
        multiplier = this1
        sIsNegative = False
        s = StringTools.trim(sParam)
        if ((("" if ((0 >= len(s))) else s[0])) == "-"):
            sIsNegative = True
            s = HxString.substring(s,1,len(s))
        _hx_len = len(s)
        _g = 0
        _g1 = _hx_len
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            digitInt = (HxString.charCodeAt(s,((_hx_len - 1) - i)) - 48)
            if ((digitInt < 0) or ((digitInt > 9))):
                raise haxe_Exception.thrown("NumberFormatError")
            if (digitInt != 0):
                digit_high = (digitInt >> 31)
                digit_low = digitInt
                if sIsNegative:
                    mask = 65535
                    al = (multiplier.low & mask)
                    ah = HxOverrides.rshift(multiplier.low, 16)
                    bl = (digit_low & mask)
                    bh = HxOverrides.rshift(digit_low, 16)
                    p00 = haxe__Int32_Int32_Impl_.mul(al,bl)
                    p10 = haxe__Int32_Int32_Impl_.mul(ah,bl)
                    p01 = haxe__Int32_Int32_Impl_.mul(al,bh)
                    p11 = haxe__Int32_Int32_Impl_.mul(ah,bh)
                    low = p00
                    high = ((((((p11 + (HxOverrides.rshift(p01, 16))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)) + (HxOverrides.rshift(p10, 16))) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    p01 = ((((p01 << 16)) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    low = (((low + p01) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    if (haxe__Int32_Int32_Impl_.ucompare(low,p01) < 0):
                        ret = high
                        high = (high + 1)
                        high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    p10 = ((((p10 << 16)) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    low = (((low + p10) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    if (haxe__Int32_Int32_Impl_.ucompare(low,p10) < 0):
                        ret1 = high
                        high = (high + 1)
                        high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    high = (((high + ((((haxe__Int32_Int32_Impl_.mul(multiplier.low,digit_high) + haxe__Int32_Int32_Impl_.mul(multiplier.high,digit_low)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)))) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    b_high = high
                    b_low = low
                    high1 = (((current.high - b_high) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    low1 = (((current.low - b_low) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    if (haxe__Int32_Int32_Impl_.ucompare(current.low,b_low) < 0):
                        ret2 = high1
                        high1 = (high1 - 1)
                        high1 = ((high1 + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    this1 = haxe__Int64____Int64(high1,low1)
                    current = this1
                    if (not ((current.high < 0))):
                        raise haxe_Exception.thrown("NumberFormatError: Underflow")
                else:
                    mask1 = 65535
                    al1 = (multiplier.low & mask1)
                    ah1 = HxOverrides.rshift(multiplier.low, 16)
                    bl1 = (digit_low & mask1)
                    bh1 = HxOverrides.rshift(digit_low, 16)
                    p001 = haxe__Int32_Int32_Impl_.mul(al1,bl1)
                    p101 = haxe__Int32_Int32_Impl_.mul(ah1,bl1)
                    p011 = haxe__Int32_Int32_Impl_.mul(al1,bh1)
                    p111 = haxe__Int32_Int32_Impl_.mul(ah1,bh1)
                    low2 = p001
                    high2 = ((((((p111 + (HxOverrides.rshift(p011, 16))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)) + (HxOverrides.rshift(p101, 16))) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    p011 = ((((p011 << 16)) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    low2 = (((low2 + p011) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    if (haxe__Int32_Int32_Impl_.ucompare(low2,p011) < 0):
                        ret3 = high2
                        high2 = (high2 + 1)
                        high2 = ((high2 + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    p101 = ((((p101 << 16)) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    low2 = (((low2 + p101) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    if (haxe__Int32_Int32_Impl_.ucompare(low2,p101) < 0):
                        ret4 = high2
                        high2 = (high2 + 1)
                        high2 = ((high2 + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    high2 = (((high2 + ((((haxe__Int32_Int32_Impl_.mul(multiplier.low,digit_high) + haxe__Int32_Int32_Impl_.mul(multiplier.high,digit_low)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)))) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    b_high1 = high2
                    b_low1 = low2
                    high3 = (((current.high + b_high1) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    low3 = (((current.low + b_low1) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    if (haxe__Int32_Int32_Impl_.ucompare(low3,current.low) < 0):
                        ret5 = high3
                        high3 = (high3 + 1)
                        high3 = ((high3 + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    this2 = haxe__Int64____Int64(high3,low3)
                    current = this2
                    if (current.high < 0):
                        raise haxe_Exception.thrown("NumberFormatError: Overflow")
            mask2 = 65535
            al2 = (multiplier.low & mask2)
            ah2 = HxOverrides.rshift(multiplier.low, 16)
            bl2 = (base_low & mask2)
            bh2 = HxOverrides.rshift(base_low, 16)
            p002 = haxe__Int32_Int32_Impl_.mul(al2,bl2)
            p102 = haxe__Int32_Int32_Impl_.mul(ah2,bl2)
            p012 = haxe__Int32_Int32_Impl_.mul(al2,bh2)
            p112 = haxe__Int32_Int32_Impl_.mul(ah2,bh2)
            low4 = p002
            high4 = ((((((p112 + (HxOverrides.rshift(p012, 16))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)) + (HxOverrides.rshift(p102, 16))) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            p012 = ((((p012 << 16)) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            low4 = (((low4 + p012) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            if (haxe__Int32_Int32_Impl_.ucompare(low4,p012) < 0):
                ret6 = high4
                high4 = (high4 + 1)
                high4 = ((high4 + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            p102 = ((((p102 << 16)) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            low4 = (((low4 + p102) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            if (haxe__Int32_Int32_Impl_.ucompare(low4,p102) < 0):
                ret7 = high4
                high4 = (high4 + 1)
                high4 = ((high4 + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            high4 = (((high4 + ((((haxe__Int32_Int32_Impl_.mul(multiplier.low,base_high) + haxe__Int32_Int32_Impl_.mul(multiplier.high,base_low)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)))) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            this3 = haxe__Int64____Int64(high4,low4)
            multiplier = this3
        return current

    @staticmethod
    def fromFloat(f):
        if (python_lib_Math.isnan(f) or (not ((((f != Math.POSITIVE_INFINITY) and ((f != Math.NEGATIVE_INFINITY))) and (not python_lib_Math.isnan(f)))))):
            raise haxe_Exception.thrown("Number is NaN or Infinite")
        noFractions = (f - (HxOverrides.modf(f, 1)))
        if (noFractions > 9007199254740991):
            raise haxe_Exception.thrown("Conversion overflow")
        if (noFractions < -9007199254740991):
            raise haxe_Exception.thrown("Conversion underflow")
        this1 = haxe__Int64____Int64(0,0)
        result = this1
        neg = (noFractions < 0)
        rest = (-noFractions if neg else noFractions)
        i = 0
        while (rest >= 1):
            curr = HxOverrides.modf(rest, 2)
            rest = (rest / 2)
            if (curr >= 1):
                a_high = 0
                a_low = 1
                b = i
                b = (b & 63)
                b1 = None
                if (b == 0):
                    this1 = haxe__Int64____Int64(a_high,a_low)
                    b1 = this1
                elif (b < 32):
                    this2 = haxe__Int64____Int64(((((((((a_high << b)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)) | HxOverrides.rshift(a_low, ((32 - b))))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)),((((a_low << b)) + (2 ** 31)) % (2 ** 32) - (2 ** 31)))
                    b1 = this2
                else:
                    this3 = haxe__Int64____Int64(((((a_low << ((b - 32)))) + (2 ** 31)) % (2 ** 32) - (2 ** 31)),0)
                    b1 = this3
                high = (((result.high + b1.high) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                low = (((result.low + b1.low) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                if (haxe__Int32_Int32_Impl_.ucompare(low,result.low) < 0):
                    ret = high
                    high = (high + 1)
                    high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                this4 = haxe__Int64____Int64(high,low)
                result = this4
            i = (i + 1)
        if neg:
            high = ((~result.high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            low = (((~result.low + 1) + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            if (low == 0):
                ret = high
                high = (high + 1)
                high = ((high + (2 ** 31)) % (2 ** 32) - (2 ** 31))
            this1 = haxe__Int64____Int64(high,low)
            result = this1
        return result
haxe_Int64Helper._hx_class = haxe_Int64Helper
_hx_classes["haxe.Int64Helper"] = haxe_Int64Helper


class haxe_Log:
    _hx_class_name = "haxe.Log"
    __slots__ = ()
    _hx_statics = ["formatOutput", "trace"]

    @staticmethod
    def formatOutput(v,infos):
        _hx_str = Std.string(v)
        if (infos is None):
            return _hx_str
        pstr = ((HxOverrides.stringOrNull(infos.fileName) + ":") + Std.string(infos.lineNumber))
        if (Reflect.field(infos,"customParams") is not None):
            _g = 0
            _g1 = Reflect.field(infos,"customParams")
            while (_g < len(_g1)):
                v = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _hx_str = (("null" if _hx_str is None else _hx_str) + ((", " + Std.string(v))))
        return ((("null" if pstr is None else pstr) + ": ") + ("null" if _hx_str is None else _hx_str))

    @staticmethod
    def trace(v,infos = None):
        _hx_str = haxe_Log.formatOutput(v,infos)
        str1 = Std.string(_hx_str)
        python_Lib.printString((("" + ("null" if str1 is None else str1)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
haxe_Log._hx_class = haxe_Log
_hx_classes["haxe.Log"] = haxe_Log


class haxe_NativeStackTrace:
    _hx_class_name = "haxe.NativeStackTrace"
    __slots__ = ()
    _hx_statics = ["saveStack", "exceptionStack", "toHaxe"]

    @staticmethod
    def saveStack(exception):
        pass

    @staticmethod
    def exceptionStack():
        exc = python_lib_Sys.exc_info()
        if (exc[2] is not None):
            infos = python_lib_Traceback.extract_tb(exc[2])
            infos.reverse()
            return infos
        else:
            return []

    @staticmethod
    def toHaxe(native,skip = None):
        if (skip is None):
            skip = 0
        stack = []
        _g = 0
        _g1 = len(native)
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            if (skip > i):
                continue
            elem = (native[i] if i >= 0 and i < len(native) else None)
            x = haxe_StackItem.FilePos(haxe_StackItem.Method(None,elem[2]),elem[0],elem[1])
            stack.append(x)
        return stack
haxe_NativeStackTrace._hx_class = haxe_NativeStackTrace
_hx_classes["haxe.NativeStackTrace"] = haxe_NativeStackTrace


class haxe_Serializer:
    _hx_class_name = "haxe.Serializer"
    __slots__ = ("buf", "cache", "shash", "scount", "useCache", "useEnumIndex")
    _hx_fields = ["buf", "cache", "shash", "scount", "useCache", "useEnumIndex"]
    _hx_methods = ["toString", "serializeString", "serializeRef", "serializeFields", "serialize"]
    _hx_statics = ["USE_CACHE", "USE_ENUM_INDEX", "BASE64", "BASE64_CODES"]

    def __init__(self):
        self.buf = StringBuf()
        self.cache = list()
        self.useCache = haxe_Serializer.USE_CACHE
        self.useEnumIndex = haxe_Serializer.USE_ENUM_INDEX
        self.shash = haxe_ds_StringMap()
        self.scount = 0

    def toString(self):
        return self.buf.b.getvalue()

    def serializeString(self,s):
        x = self.shash.h.get(s,None)
        if (x is not None):
            self.buf.b.write("R")
            _this = self.buf
            s1 = Std.string(x)
            _this.b.write(s1)
            return
        value = self.scount
        self.scount = (self.scount + 1)
        self.shash.h[s] = value
        self.buf.b.write("y")
        s = python_lib_urllib_Parse.quote(s,"")
        _this = self.buf
        s1 = Std.string(len(s))
        _this.b.write(s1)
        self.buf.b.write(":")
        _this = self.buf
        s1 = Std.string(s)
        _this.b.write(s1)

    def serializeRef(self,v):
        _g = 0
        _g1 = len(self.cache)
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            if HxOverrides.eq((self.cache[i] if i >= 0 and i < len(self.cache) else None),v):
                self.buf.b.write("r")
                _this = self.buf
                s = Std.string(i)
                _this.b.write(s)
                return True
        _this = self.cache
        _this.append(v)
        return False

    def serializeFields(self,v):
        _g = 0
        _g1 = python_Boot.fields(v)
        while (_g < len(_g1)):
            f = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            self.serializeString(f)
            self.serialize(Reflect.field(v,f))
        self.buf.b.write("g")

    def serialize(self,v):
        _g = Type.typeof(v)
        tmp = _g.index
        if (tmp == 0):
            self.buf.b.write("n")
        elif (tmp == 1):
            v1 = v
            if (v1 == 0):
                self.buf.b.write("z")
                return
            self.buf.b.write("i")
            _this = self.buf
            s = Std.string(v1)
            _this.b.write(s)
        elif (tmp == 2):
            v1 = v
            if python_lib_Math.isnan(v1):
                self.buf.b.write("k")
            elif (not ((((v1 != Math.POSITIVE_INFINITY) and ((v1 != Math.NEGATIVE_INFINITY))) and (not python_lib_Math.isnan(v1))))):
                self.buf.b.write(("m" if ((v1 < 0)) else "p"))
            else:
                self.buf.b.write("d")
                _this = self.buf
                s = Std.string(v1)
                _this.b.write(s)
        elif (tmp == 3):
            self.buf.b.write(("t" if v else "f"))
        elif (tmp == 4):
            if Std.isOfType(v,Class):
                className = Type.getClassName(v)
                self.buf.b.write("A")
                self.serializeString(className)
            elif Std.isOfType(v,Enum):
                self.buf.b.write("B")
                self.serializeString(Type.getEnumName(v))
            else:
                if (self.useCache and self.serializeRef(v)):
                    return
                self.buf.b.write("o")
                self.serializeFields(v)
        elif (tmp == 5):
            raise haxe_Exception.thrown("Cannot serialize function")
        elif (tmp == 6):
            c = _g.params[0]
            if (c == str):
                self.serializeString(v)
                return
            if (self.useCache and self.serializeRef(v)):
                return
            _g1 = Type.getClassName(c)
            _hx_local_0 = len(_g1)
            if (_hx_local_0 == 17):
                if (_g1 == "haxe.ds.ObjectMap"):
                    self.buf.b.write("M")
                    v1 = v
                    k = v1.keys()
                    while k.hasNext():
                        k1 = k.next()
                        self.serialize(k1)
                        self.serialize(v1.h.get(k1,None))
                    self.buf.b.write("h")
                elif (_g1 == "haxe.ds.StringMap"):
                    self.buf.b.write("b")
                    v1 = v
                    k = v1.keys()
                    while k.hasNext():
                        k1 = k.next()
                        self.serializeString(k1)
                        self.serialize(v1.h.get(k1,None))
                    self.buf.b.write("h")
                else:
                    if self.useCache:
                        _this = self.cache
                        if (len(_this) != 0):
                            _this.pop()
                    if python_Boot.hasField(v,"hxSerialize"):
                        self.buf.b.write("C")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        Reflect.field(v,"hxSerialize")(self)
                        self.buf.b.write("g")
                    else:
                        self.buf.b.write("c")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        self.serializeFields(v)
            elif (_hx_local_0 == 5):
                if (_g1 == "Array"):
                    ucount = 0
                    self.buf.b.write("a")
                    v1 = v
                    l = len(v1)
                    _g1 = 0
                    _g2 = l
                    while (_g1 < _g2):
                        i = _g1
                        _g1 = (_g1 + 1)
                        if ((v1[i] if i >= 0 and i < len(v1) else None) is None):
                            ucount = (ucount + 1)
                        else:
                            if (ucount > 0):
                                if (ucount == 1):
                                    self.buf.b.write("n")
                                else:
                                    self.buf.b.write("u")
                                    _this = self.buf
                                    s = Std.string(ucount)
                                    _this.b.write(s)
                                ucount = 0
                            self.serialize((v1[i] if i >= 0 and i < len(v1) else None))
                    if (ucount > 0):
                        if (ucount == 1):
                            self.buf.b.write("n")
                        else:
                            self.buf.b.write("u")
                            _this = self.buf
                            s = Std.string(ucount)
                            _this.b.write(s)
                    self.buf.b.write("h")
                else:
                    if self.useCache:
                        _this = self.cache
                        if (len(_this) != 0):
                            _this.pop()
                    if python_Boot.hasField(v,"hxSerialize"):
                        self.buf.b.write("C")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        Reflect.field(v,"hxSerialize")(self)
                        self.buf.b.write("g")
                    else:
                        self.buf.b.write("c")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        self.serializeFields(v)
            elif (_hx_local_0 == 4):
                if (_g1 == "Date"):
                    d = v
                    self.buf.b.write("v")
                    _this = self.buf
                    s = Std.string((d.date.timestamp() * 1000))
                    _this.b.write(s)
                else:
                    if self.useCache:
                        _this = self.cache
                        if (len(_this) != 0):
                            _this.pop()
                    if python_Boot.hasField(v,"hxSerialize"):
                        self.buf.b.write("C")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        Reflect.field(v,"hxSerialize")(self)
                        self.buf.b.write("g")
                    else:
                        self.buf.b.write("c")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        self.serializeFields(v)
            elif (_hx_local_0 == 12):
                if (_g1 == "haxe.ds.List"):
                    self.buf.b.write("l")
                    v1 = v
                    _g_head = v1.h
                    while (_g_head is not None):
                        val = _g_head.item
                        _g_head = _g_head.next
                        i = val
                        self.serialize(i)
                    self.buf.b.write("h")
                else:
                    if self.useCache:
                        _this = self.cache
                        if (len(_this) != 0):
                            _this.pop()
                    if python_Boot.hasField(v,"hxSerialize"):
                        self.buf.b.write("C")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        Reflect.field(v,"hxSerialize")(self)
                        self.buf.b.write("g")
                    else:
                        self.buf.b.write("c")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        self.serializeFields(v)
            elif (_hx_local_0 == 13):
                if (_g1 == "haxe.io.Bytes"):
                    v1 = v
                    self.buf.b.write("s")
                    _this = self.buf
                    s = Std.string(Math.ceil(((v1.length * 8) / 6)))
                    _this.b.write(s)
                    self.buf.b.write(":")
                    i = 0
                    _hx_max = (v1.length - 2)
                    b64 = haxe_Serializer.BASE64_CODES
                    if (b64 is None):
                        this1 = [None]*len(haxe_Serializer.BASE64)
                        b64 = this1
                        _g1 = 0
                        _g2 = len(haxe_Serializer.BASE64)
                        while (_g1 < _g2):
                            i1 = _g1
                            _g1 = (_g1 + 1)
                            val = HxString.charCodeAt(haxe_Serializer.BASE64,i1)
                            b64[i1] = val
                        haxe_Serializer.BASE64_CODES = b64
                    while (i < _hx_max):
                        pos = i
                        i = (i + 1)
                        b1 = v1.b[pos]
                        pos1 = i
                        i = (i + 1)
                        b2 = v1.b[pos1]
                        pos2 = i
                        i = (i + 1)
                        b3 = v1.b[pos2]
                        _this = self.buf
                        c1 = b64[(b1 >> 2)]
                        s = "".join(map(chr,[c1]))
                        _this.b.write(s)
                        _this1 = self.buf
                        c2 = b64[((((b1 << 4) | ((b2 >> 4)))) & 63)]
                        s1 = "".join(map(chr,[c2]))
                        _this1.b.write(s1)
                        _this2 = self.buf
                        c3 = b64[((((b2 << 2) | ((b3 >> 6)))) & 63)]
                        s2 = "".join(map(chr,[c3]))
                        _this2.b.write(s2)
                        _this3 = self.buf
                        c4 = b64[(b3 & 63)]
                        s3 = "".join(map(chr,[c4]))
                        _this3.b.write(s3)
                    if (i == _hx_max):
                        pos = i
                        i = (i + 1)
                        b1 = v1.b[pos]
                        pos = i
                        i = (i + 1)
                        b2 = v1.b[pos]
                        _this = self.buf
                        c1 = b64[(b1 >> 2)]
                        s = "".join(map(chr,[c1]))
                        _this.b.write(s)
                        _this = self.buf
                        c1 = b64[((((b1 << 4) | ((b2 >> 4)))) & 63)]
                        s = "".join(map(chr,[c1]))
                        _this.b.write(s)
                        _this = self.buf
                        c1 = b64[((b2 << 2) & 63)]
                        s = "".join(map(chr,[c1]))
                        _this.b.write(s)
                    elif (i == ((_hx_max + 1))):
                        pos = i
                        i = (i + 1)
                        b1 = v1.b[pos]
                        _this = self.buf
                        c1 = b64[(b1 >> 2)]
                        s = "".join(map(chr,[c1]))
                        _this.b.write(s)
                        _this = self.buf
                        c1 = b64[((b1 << 4) & 63)]
                        s = "".join(map(chr,[c1]))
                        _this.b.write(s)
                else:
                    if self.useCache:
                        _this = self.cache
                        if (len(_this) != 0):
                            _this.pop()
                    if python_Boot.hasField(v,"hxSerialize"):
                        self.buf.b.write("C")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        Reflect.field(v,"hxSerialize")(self)
                        self.buf.b.write("g")
                    else:
                        self.buf.b.write("c")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        self.serializeFields(v)
            elif (_hx_local_0 == 14):
                if (_g1 == "haxe.ds.IntMap"):
                    self.buf.b.write("q")
                    v1 = v
                    k = v1.keys()
                    while k.hasNext():
                        k1 = k.next()
                        self.buf.b.write(":")
                        _this = self.buf
                        s = Std.string(k1)
                        _this.b.write(s)
                        self.serialize(v1.h.get(k1,None))
                    self.buf.b.write("h")
                else:
                    if self.useCache:
                        _this = self.cache
                        if (len(_this) != 0):
                            _this.pop()
                    if python_Boot.hasField(v,"hxSerialize"):
                        self.buf.b.write("C")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        Reflect.field(v,"hxSerialize")(self)
                        self.buf.b.write("g")
                    else:
                        self.buf.b.write("c")
                        self.serializeString(Type.getClassName(c))
                        if self.useCache:
                            _this = self.cache
                            _this.append(v)
                        self.serializeFields(v)
            else:
                if self.useCache:
                    _this = self.cache
                    if (len(_this) != 0):
                        _this.pop()
                if python_Boot.hasField(v,"hxSerialize"):
                    self.buf.b.write("C")
                    self.serializeString(Type.getClassName(c))
                    if self.useCache:
                        _this = self.cache
                        _this.append(v)
                    Reflect.field(v,"hxSerialize")(self)
                    self.buf.b.write("g")
                else:
                    self.buf.b.write("c")
                    self.serializeString(Type.getClassName(c))
                    if self.useCache:
                        _this = self.cache
                        _this.append(v)
                    self.serializeFields(v)
        elif (tmp == 7):
            e = _g.params[0]
            if self.useCache:
                if self.serializeRef(v):
                    return
                _this = self.cache
                if (len(_this) != 0):
                    _this.pop()
            _this = self.buf
            s = Std.string(("j" if (self.useEnumIndex) else "w"))
            _this.b.write(s)
            self.serializeString(Type.getEnumName(e))
            if self.useEnumIndex:
                self.buf.b.write(":")
                _this = self.buf
                s = Std.string(v.index)
                _this.b.write(s)
            else:
                self.serializeString(v.tag)
            self.buf.b.write(":")
            arr = list(v.params)
            if (arr is not None):
                _this = self.buf
                s = Std.string(len(arr))
                _this.b.write(s)
                _g = 0
                while (_g < len(arr)):
                    v1 = (arr[_g] if _g >= 0 and _g < len(arr) else None)
                    _g = (_g + 1)
                    self.serialize(v1)
            else:
                self.buf.b.write("0")
            if self.useCache:
                _this = self.cache
                _this.append(v)
        else:
            raise haxe_Exception.thrown(("Cannot serialize " + Std.string(v)))

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.buf = None
        _hx_o.cache = None
        _hx_o.shash = None
        _hx_o.scount = None
        _hx_o.useCache = None
        _hx_o.useEnumIndex = None
haxe_Serializer._hx_class = haxe_Serializer
_hx_classes["haxe.Serializer"] = haxe_Serializer


class haxe_Timer:
    _hx_class_name = "haxe.Timer"
    _hx_fields = ["thread", "eventHandler"]
    _hx_methods = ["stop", "run"]
    _hx_statics = ["delay"]

    def __init__(self,time_ms):
        self.eventHandler = None
        self.thread = None
        _gthis = self
        self.thread = sys_thread__Thread_HxThread.current()
        def _hx_local_0():
            _gthis.run()
        self.eventHandler = sys_thread__Thread_Thread_Impl_.get_events(self.thread).repeat(_hx_local_0,time_ms)

    def stop(self):
        sys_thread__Thread_Thread_Impl_.get_events(self.thread).cancel(self.eventHandler)

    def run(self):
        pass

    @staticmethod
    def delay(f,time_ms):
        t = haxe_Timer(time_ms)
        def _hx_local_0():
            t.stop()
            f()
        t.run = _hx_local_0
        return t

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.thread = None
        _hx_o.eventHandler = None
haxe_Timer._hx_class = haxe_Timer
_hx_classes["haxe.Timer"] = haxe_Timer


class haxe__Unserializer_DefaultResolver:
    _hx_class_name = "haxe._Unserializer.DefaultResolver"
    __slots__ = ()
    _hx_methods = ["resolveClass", "resolveEnum"]

    def __init__(self):
        pass

    def resolveClass(self,name):
        return Type.resolveClass(name)

    def resolveEnum(self,name):
        return Type.resolveEnum(name)

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
haxe__Unserializer_DefaultResolver._hx_class = haxe__Unserializer_DefaultResolver
_hx_classes["haxe._Unserializer.DefaultResolver"] = haxe__Unserializer_DefaultResolver


class haxe_Unserializer:
    _hx_class_name = "haxe.Unserializer"
    __slots__ = ("buf", "pos", "length", "cache", "scache", "resolver")
    _hx_fields = ["buf", "pos", "length", "cache", "scache", "resolver"]
    _hx_methods = ["readDigits", "readFloat", "unserializeObject", "unserializeEnum", "unserialize"]
    _hx_statics = ["DEFAULT_RESOLVER", "BASE64", "CODES", "initCodes"]

    def __init__(self,buf):
        self.resolver = None
        self.scache = None
        self.cache = None
        self.length = None
        self.pos = None
        self.buf = buf
        self.length = len(self.buf)
        self.pos = 0
        self.scache = list()
        self.cache = list()
        r = haxe_Unserializer.DEFAULT_RESOLVER
        if (r is None):
            r = haxe__Unserializer_DefaultResolver()
            haxe_Unserializer.DEFAULT_RESOLVER = r
        self.resolver = r

    def readDigits(self):
        k = 0
        s = False
        fpos = self.pos
        while True:
            p = self.pos
            s1 = self.buf
            c = (-1 if ((p >= len(s1))) else ord(s1[p]))
            if (c == -1):
                break
            if (c == 45):
                if (self.pos != fpos):
                    break
                s = True
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.pos
                _hx_local_0.pos = (_hx_local_1 + 1)
                _hx_local_1
                continue
            if ((c < 48) or ((c > 57))):
                break
            k = ((k * 10) + ((c - 48)))
            _hx_local_2 = self
            _hx_local_3 = _hx_local_2.pos
            _hx_local_2.pos = (_hx_local_3 + 1)
            _hx_local_3
        if s:
            k = (k * -1)
        return k

    def readFloat(self):
        p1 = self.pos
        while True:
            p = self.pos
            s = self.buf
            c = (-1 if ((p >= len(s))) else ord(s[p]))
            if (c == -1):
                break
            if ((((c >= 43) and ((c < 58))) or ((c == 101))) or ((c == 69))):
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.pos
                _hx_local_0.pos = (_hx_local_1 + 1)
                _hx_local_1
            else:
                break
        return Std.parseFloat(HxString.substr(self.buf,p1,(self.pos - p1)))

    def unserializeObject(self,o):
        while True:
            if (self.pos >= self.length):
                raise haxe_Exception.thrown("Invalid object")
            p = self.pos
            s = self.buf
            if (((-1 if ((p >= len(s))) else ord(s[p]))) == 103):
                break
            k = self.unserialize()
            if (not Std.isOfType(k,str)):
                raise haxe_Exception.thrown("Invalid object key")
            v = self.unserialize()
            field = k
            setattr(o,(("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field)),v)
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0.pos
        _hx_local_0.pos = (_hx_local_1 + 1)
        _hx_local_1

    def unserializeEnum(self,edecl,tag):
        p = self.pos
        self.pos = (self.pos + 1)
        s = self.buf
        if (((-1 if ((p >= len(s))) else ord(s[p]))) != 58):
            raise haxe_Exception.thrown("Invalid enum format")
        nargs = self.readDigits()
        if (nargs == 0):
            return Type.createEnum(edecl,tag)
        args = list()
        while True:
            tmp = nargs
            nargs = (nargs - 1)
            if (not ((tmp > 0))):
                break
            x = self.unserialize()
            args.append(x)
        return Type.createEnum(edecl,tag,args)

    def unserialize(self):
        p = self.pos
        self.pos = (self.pos + 1)
        s = self.buf
        _g = (-1 if ((p >= len(s))) else ord(s[p]))
        if (_g == 65):
            name = self.unserialize()
            cl = self.resolver.resolveClass(name)
            if (cl is None):
                raise haxe_Exception.thrown(("Class not found " + ("null" if name is None else name)))
            return cl
        elif (_g == 66):
            name = self.unserialize()
            e = self.resolver.resolveEnum(name)
            if (e is None):
                raise haxe_Exception.thrown(("Enum not found " + ("null" if name is None else name)))
            return e
        elif (_g == 67):
            name = self.unserialize()
            cl = self.resolver.resolveClass(name)
            if (cl is None):
                raise haxe_Exception.thrown(("Class not found " + ("null" if name is None else name)))
            o = Type.createEmptyInstance(cl)
            _this = self.cache
            _this.append(o)
            Reflect.field(o,"hxUnserialize")(self)
            p = self.pos
            self.pos = (self.pos + 1)
            s = self.buf
            if (((-1 if ((p >= len(s))) else ord(s[p]))) != 103):
                raise haxe_Exception.thrown("Invalid custom data")
            return o
        elif (_g == 77):
            h = haxe_ds_ObjectMap()
            _this = self.cache
            _this.append(h)
            buf = self.buf
            while True:
                p = self.pos
                s = self.buf
                if (not ((((-1 if ((p >= len(s))) else ord(s[p]))) != 104))):
                    break
                s1 = self.unserialize()
                h.set(s1,self.unserialize())
            _hx_local_0 = self
            _hx_local_1 = _hx_local_0.pos
            _hx_local_0.pos = (_hx_local_1 + 1)
            _hx_local_1
            return h
        elif (_g == 82):
            n = self.readDigits()
            if ((n < 0) or ((n >= len(self.scache)))):
                raise haxe_Exception.thrown("Invalid string reference")
            return (self.scache[n] if n >= 0 and n < len(self.scache) else None)
        elif (_g == 97):
            buf = self.buf
            a = list()
            _this = self.cache
            _this.append(a)
            while True:
                p = self.pos
                s = self.buf
                c = (-1 if ((p >= len(s))) else ord(s[p]))
                if (c == 104):
                    _hx_local_2 = self
                    _hx_local_3 = _hx_local_2.pos
                    _hx_local_2.pos = (_hx_local_3 + 1)
                    _hx_local_3
                    break
                if (c == 117):
                    _hx_local_4 = self
                    _hx_local_5 = _hx_local_4.pos
                    _hx_local_4.pos = (_hx_local_5 + 1)
                    _hx_local_5
                    n = self.readDigits()
                    python_internal_ArrayImpl._set(a, ((len(a) + n) - 1), None)
                else:
                    x = self.unserialize()
                    a.append(x)
            return a
        elif (_g == 98):
            h = haxe_ds_StringMap()
            _this = self.cache
            _this.append(h)
            buf = self.buf
            while True:
                p = self.pos
                s = self.buf
                if (not ((((-1 if ((p >= len(s))) else ord(s[p]))) != 104))):
                    break
                s1 = self.unserialize()
                value = self.unserialize()
                h.h[s1] = value
            _hx_local_6 = self
            _hx_local_7 = _hx_local_6.pos
            _hx_local_6.pos = (_hx_local_7 + 1)
            _hx_local_7
            return h
        elif (_g == 99):
            name = self.unserialize()
            cl = self.resolver.resolveClass(name)
            if (cl is None):
                raise haxe_Exception.thrown(("Class not found " + ("null" if name is None else name)))
            o = Type.createEmptyInstance(cl)
            _this = self.cache
            _this.append(o)
            self.unserializeObject(o)
            return o
        elif (_g == 100):
            return self.readFloat()
        elif (_g == 102):
            return False
        elif (_g == 105):
            return self.readDigits()
        elif (_g == 106):
            name = self.unserialize()
            edecl = self.resolver.resolveEnum(name)
            if (edecl is None):
                raise haxe_Exception.thrown(("Enum not found " + ("null" if name is None else name)))
            _hx_local_8 = self
            _hx_local_9 = _hx_local_8.pos
            _hx_local_8.pos = (_hx_local_9 + 1)
            _hx_local_9
            index = self.readDigits()
            tag = python_internal_ArrayImpl._get(Type.getEnumConstructs(edecl), index)
            if (tag is None):
                raise haxe_Exception.thrown(((("Unknown enum index " + ("null" if name is None else name)) + "@") + Std.string(index)))
            e = self.unserializeEnum(edecl,tag)
            _this = self.cache
            _this.append(e)
            return e
        elif (_g == 107):
            return Math.NaN
        elif (_g == 108):
            l = haxe_ds_List()
            _this = self.cache
            _this.append(l)
            buf = self.buf
            while True:
                p = self.pos
                s = self.buf
                if (not ((((-1 if ((p >= len(s))) else ord(s[p]))) != 104))):
                    break
                l.add(self.unserialize())
            _hx_local_10 = self
            _hx_local_11 = _hx_local_10.pos
            _hx_local_10.pos = (_hx_local_11 + 1)
            _hx_local_11
            return l
        elif (_g == 109):
            return Math.NEGATIVE_INFINITY
        elif (_g == 110):
            return None
        elif (_g == 111):
            o = _hx_AnonObject({})
            _this = self.cache
            _this.append(o)
            self.unserializeObject(o)
            return o
        elif (_g == 112):
            return Math.POSITIVE_INFINITY
        elif (_g == 113):
            h = haxe_ds_IntMap()
            _this = self.cache
            _this.append(h)
            buf = self.buf
            p = self.pos
            self.pos = (self.pos + 1)
            s = self.buf
            c = (-1 if ((p >= len(s))) else ord(s[p]))
            while (c == 58):
                i = self.readDigits()
                h.set(i,self.unserialize())
                p = self.pos
                self.pos = (self.pos + 1)
                s = self.buf
                c = (-1 if ((p >= len(s))) else ord(s[p]))
            if (c != 104):
                raise haxe_Exception.thrown("Invalid IntMap format")
            return h
        elif (_g == 114):
            n = self.readDigits()
            if ((n < 0) or ((n >= len(self.cache)))):
                raise haxe_Exception.thrown("Invalid reference")
            return (self.cache[n] if n >= 0 and n < len(self.cache) else None)
        elif (_g == 115):
            _hx_len = self.readDigits()
            buf = self.buf
            p = self.pos
            self.pos = (self.pos + 1)
            s = self.buf
            if ((((-1 if ((p >= len(s))) else ord(s[p]))) != 58) or (((self.length - self.pos) < _hx_len))):
                raise haxe_Exception.thrown("Invalid bytes length")
            codes = haxe_Unserializer.CODES
            if (codes is None):
                codes = haxe_Unserializer.initCodes()
                haxe_Unserializer.CODES = codes
            i = self.pos
            rest = (_hx_len & 3)
            size = ((((_hx_len >> 2)) * 3) + (((rest - 1) if ((rest >= 2)) else 0)))
            _hx_max = (i + ((_hx_len - rest)))
            _hx_bytes = haxe_io_Bytes.alloc(size)
            bpos = 0
            while (i < _hx_max):
                index = i
                i = (i + 1)
                c1 = python_internal_ArrayImpl._get(codes, (-1 if ((index >= len(buf))) else ord(buf[index])))
                index1 = i
                i = (i + 1)
                c2 = python_internal_ArrayImpl._get(codes, (-1 if ((index1 >= len(buf))) else ord(buf[index1])))
                pos = bpos
                bpos = (bpos + 1)
                _hx_bytes.b[pos] = ((((c1 << 2) | ((c2 >> 4)))) & 255)
                index2 = i
                i = (i + 1)
                c3 = python_internal_ArrayImpl._get(codes, (-1 if ((index2 >= len(buf))) else ord(buf[index2])))
                pos1 = bpos
                bpos = (bpos + 1)
                _hx_bytes.b[pos1] = ((((c2 << 4) | ((c3 >> 2)))) & 255)
                index3 = i
                i = (i + 1)
                c4 = python_internal_ArrayImpl._get(codes, (-1 if ((index3 >= len(buf))) else ord(buf[index3])))
                pos2 = bpos
                bpos = (bpos + 1)
                _hx_bytes.b[pos2] = ((((c3 << 6) | c4)) & 255)
            if (rest >= 2):
                index = i
                i = (i + 1)
                c1 = python_internal_ArrayImpl._get(codes, (-1 if ((index >= len(buf))) else ord(buf[index])))
                index = i
                i = (i + 1)
                c2 = python_internal_ArrayImpl._get(codes, (-1 if ((index >= len(buf))) else ord(buf[index])))
                pos = bpos
                bpos = (bpos + 1)
                _hx_bytes.b[pos] = ((((c1 << 2) | ((c2 >> 4)))) & 255)
                if (rest == 3):
                    index = i
                    i = (i + 1)
                    c3 = python_internal_ArrayImpl._get(codes, (-1 if ((index >= len(buf))) else ord(buf[index])))
                    pos = bpos
                    bpos = (bpos + 1)
                    _hx_bytes.b[pos] = ((((c2 << 4) | ((c3 >> 2)))) & 255)
            _hx_local_12 = self
            _hx_local_13 = _hx_local_12.pos
            _hx_local_12.pos = (_hx_local_13 + _hx_len)
            _hx_local_12.pos
            _this = self.cache
            _this.append(_hx_bytes)
            return _hx_bytes
        elif (_g == 116):
            return True
        elif (_g == 118):
            d = None
            tmp = None
            tmp1 = None
            tmp2 = None
            tmp3 = None
            tmp4 = None
            tmp5 = None
            tmp6 = None
            tmp7 = None
            p = self.pos
            s = self.buf
            if (((-1 if ((p >= len(s))) else ord(s[p]))) >= 48):
                p = self.pos
                s = self.buf
                tmp7 = (((-1 if ((p >= len(s))) else ord(s[p]))) <= 57)
            else:
                tmp7 = False
            if tmp7:
                p = (self.pos + 1)
                s = self.buf
                tmp6 = (((-1 if ((p >= len(s))) else ord(s[p]))) >= 48)
            else:
                tmp6 = False
            if tmp6:
                p = (self.pos + 1)
                s = self.buf
                tmp5 = (((-1 if ((p >= len(s))) else ord(s[p]))) <= 57)
            else:
                tmp5 = False
            if tmp5:
                p = (self.pos + 2)
                s = self.buf
                tmp4 = (((-1 if ((p >= len(s))) else ord(s[p]))) >= 48)
            else:
                tmp4 = False
            if tmp4:
                p = (self.pos + 2)
                s = self.buf
                tmp3 = (((-1 if ((p >= len(s))) else ord(s[p]))) <= 57)
            else:
                tmp3 = False
            if tmp3:
                p = (self.pos + 3)
                s = self.buf
                tmp2 = (((-1 if ((p >= len(s))) else ord(s[p]))) >= 48)
            else:
                tmp2 = False
            if tmp2:
                p = (self.pos + 3)
                s = self.buf
                tmp1 = (((-1 if ((p >= len(s))) else ord(s[p]))) <= 57)
            else:
                tmp1 = False
            if tmp1:
                p = (self.pos + 4)
                s = self.buf
                tmp = (((-1 if ((p >= len(s))) else ord(s[p]))) == 45)
            else:
                tmp = False
            if tmp:
                d = Date.fromString(HxString.substr(self.buf,self.pos,19))
                _hx_local_14 = self
                _hx_local_15 = _hx_local_14.pos
                _hx_local_14.pos = (_hx_local_15 + 19)
                _hx_local_14.pos
            else:
                d = Date.fromTime(self.readFloat())
            _this = self.cache
            _this.append(d)
            return d
        elif (_g == 119):
            name = self.unserialize()
            edecl = self.resolver.resolveEnum(name)
            if (edecl is None):
                raise haxe_Exception.thrown(("Enum not found " + ("null" if name is None else name)))
            e = self.unserializeEnum(edecl,self.unserialize())
            _this = self.cache
            _this.append(e)
            return e
        elif (_g == 120):
            raise haxe_Exception.thrown(self.unserialize())
        elif (_g == 121):
            _hx_len = self.readDigits()
            p = self.pos
            self.pos = (self.pos + 1)
            s = self.buf
            if ((((-1 if ((p >= len(s))) else ord(s[p]))) != 58) or (((self.length - self.pos) < _hx_len))):
                raise haxe_Exception.thrown("Invalid string length")
            s = HxString.substr(self.buf,self.pos,_hx_len)
            _hx_local_16 = self
            _hx_local_17 = _hx_local_16.pos
            _hx_local_16.pos = (_hx_local_17 + _hx_len)
            _hx_local_16.pos
            s = python_lib_urllib_Parse.unquote(s)
            _this = self.scache
            _this.append(s)
            return s
        elif (_g == 122):
            return 0
        else:
            pass
        _hx_local_18 = self
        _hx_local_19 = _hx_local_18.pos
        _hx_local_18.pos = (_hx_local_19 - 1)
        _hx_local_19
        s = self.buf
        pos = self.pos
        raise haxe_Exception.thrown(((("Invalid char " + HxOverrides.stringOrNull((("" if (((pos < 0) or ((pos >= len(s))))) else s[pos])))) + " at position ") + Std.string(self.pos)))

    @staticmethod
    def initCodes():
        codes = list()
        _g = 0
        _g1 = len(haxe_Unserializer.BASE64)
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            s = haxe_Unserializer.BASE64
            python_internal_ArrayImpl._set(codes, (-1 if ((i >= len(s))) else ord(s[i])), i)
        return codes

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.buf = None
        _hx_o.pos = None
        _hx_o.length = None
        _hx_o.cache = None
        _hx_o.scache = None
        _hx_o.resolver = None
haxe_Unserializer._hx_class = haxe_Unserializer
_hx_classes["haxe.Unserializer"] = haxe_Unserializer


class haxe_ValueException(haxe_Exception):
    _hx_class_name = "haxe.ValueException"
    __slots__ = ("value",)
    _hx_fields = ["value"]
    _hx_methods = ["unwrap"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_Exception


    def __init__(self,value,previous = None,native = None):
        self.value = None
        super().__init__(Std.string(value),previous,native)
        self.value = value

    def unwrap(self):
        return self.value

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.value = None
haxe_ValueException._hx_class = haxe_ValueException
_hx_classes["haxe.ValueException"] = haxe_ValueException


class haxe_io_Bytes:
    _hx_class_name = "haxe.io.Bytes"
    __slots__ = ("length", "b")
    _hx_fields = ["length", "b"]
    _hx_methods = ["blit", "sub", "getString", "toString"]
    _hx_statics = ["alloc", "ofString", "ofData"]

    def __init__(self,length,b):
        self.length = length
        self.b = b

    def blit(self,pos,src,srcpos,_hx_len):
        if (((((pos < 0) or ((srcpos < 0))) or ((_hx_len < 0))) or (((pos + _hx_len) > self.length))) or (((srcpos + _hx_len) > src.length))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        self.b[pos:pos+_hx_len] = src.b[srcpos:srcpos+_hx_len]

    def sub(self,pos,_hx_len):
        if (((pos < 0) or ((_hx_len < 0))) or (((pos + _hx_len) > self.length))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        return haxe_io_Bytes(_hx_len,self.b[pos:(pos + _hx_len)])

    def getString(self,pos,_hx_len,encoding = None):
        tmp = (encoding is None)
        if (((pos < 0) or ((_hx_len < 0))) or (((pos + _hx_len) > self.length))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        return self.b[pos:pos+_hx_len].decode('UTF-8','replace')

    def toString(self):
        return self.getString(0,self.length)

    @staticmethod
    def alloc(length):
        return haxe_io_Bytes(length,bytearray(length))

    @staticmethod
    def ofString(s,encoding = None):
        b = bytearray(s,"UTF-8")
        return haxe_io_Bytes(len(b),b)

    @staticmethod
    def ofData(b):
        return haxe_io_Bytes(len(b),b)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.length = None
        _hx_o.b = None
haxe_io_Bytes._hx_class = haxe_io_Bytes
_hx_classes["haxe.io.Bytes"] = haxe_io_Bytes


class haxe_crypto_BaseCode:
    _hx_class_name = "haxe.crypto.BaseCode"
    __slots__ = ("base", "nbits", "tbl")
    _hx_fields = ["base", "nbits", "tbl"]
    _hx_methods = ["initTable", "decodeBytes"]

    def __init__(self,base):
        self.tbl = None
        _hx_len = base.length
        nbits = 1
        while (_hx_len > ((1 << nbits))):
            nbits = (nbits + 1)
        if ((nbits > 8) or ((_hx_len != ((1 << nbits))))):
            raise haxe_Exception.thrown("BaseCode : base length must be a power of two.")
        self.base = base
        self.nbits = nbits

    def initTable(self):
        tbl = list()
        _g = 0
        while (_g < 256):
            i = _g
            _g = (_g + 1)
            python_internal_ArrayImpl._set(tbl, i, -1)
        _g = 0
        _g1 = self.base.length
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            python_internal_ArrayImpl._set(tbl, self.base.b[i], i)
        self.tbl = tbl

    def decodeBytes(self,b):
        nbits = self.nbits
        base = self.base
        if (self.tbl is None):
            self.initTable()
        tbl = self.tbl
        size = ((b.length * nbits) >> 3)
        out = haxe_io_Bytes.alloc(size)
        buf = 0
        curbits = 0
        pin = 0
        pout = 0
        while (pout < size):
            while (curbits < 8):
                curbits = (curbits + nbits)
                buf = (buf << nbits)
                pos = pin
                pin = (pin + 1)
                i = python_internal_ArrayImpl._get(tbl, b.b[pos])
                if (i == -1):
                    raise haxe_Exception.thrown("BaseCode : invalid encoded char")
                buf = (buf | i)
            curbits = (curbits - 8)
            pos1 = pout
            pout = (pout + 1)
            out.b[pos1] = (((buf >> curbits) & 255) & 255)
        return out

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.base = None
        _hx_o.nbits = None
        _hx_o.tbl = None
haxe_crypto_BaseCode._hx_class = haxe_crypto_BaseCode
_hx_classes["haxe.crypto.BaseCode"] = haxe_crypto_BaseCode


class haxe_crypto_Sha1:
    _hx_class_name = "haxe.crypto.Sha1"
    __slots__ = ()
    _hx_methods = ["doEncode", "ft", "kt"]
    _hx_statics = ["make", "bytes2blks"]

    def __init__(self):
        pass

    def doEncode(self,x):
        w = list()
        a = 1732584193
        b = -271733879
        c = -1732584194
        d = 271733878
        e = -1009589776
        i = 0
        while (i < len(x)):
            olda = a
            oldb = b
            oldc = c
            oldd = d
            olde = e
            j = 0
            while (j < 80):
                if (j < 16):
                    python_internal_ArrayImpl._set(w, j, python_internal_ArrayImpl._get(x, (i + j)))
                else:
                    num = (((python_internal_ArrayImpl._get(w, (j - 3)) ^ python_internal_ArrayImpl._get(w, (j - 8))) ^ python_internal_ArrayImpl._get(w, (j - 14))) ^ python_internal_ArrayImpl._get(w, (j - 16)))
                    python_internal_ArrayImpl._set(w, j, ((num << 1) | (HxOverrides.rshift(num, 31))))
                t = (((((((a << 5) | (HxOverrides.rshift(a, 27)))) + self.ft(j,b,c,d)) + e) + (w[j] if j >= 0 and j < len(w) else None)) + self.kt(j))
                e = d
                d = c
                c = ((b << 30) | (HxOverrides.rshift(b, 2)))
                b = a
                a = t
                j = (j + 1)
            a = (a + olda)
            b = (b + oldb)
            c = (c + oldc)
            d = (d + oldd)
            e = (e + olde)
            i = (i + 16)
        return [a, b, c, d, e]

    def ft(self,t,b,c,d):
        if (t < 20):
            return ((b & c) | ((~b & d)))
        if (t < 40):
            return ((b ^ c) ^ d)
        if (t < 60):
            return (((b & c) | ((b & d))) | ((c & d)))
        return ((b ^ c) ^ d)

    def kt(self,t):
        if (t < 20):
            return 1518500249
        if (t < 40):
            return 1859775393
        if (t < 60):
            return -1894007588
        return -899497514

    @staticmethod
    def make(b):
        h = haxe_crypto_Sha1().doEncode(haxe_crypto_Sha1.bytes2blks(b))
        out = haxe_io_Bytes.alloc(20)
        p = 0
        pos = p
        p = (p + 1)
        out.b[pos] = (HxOverrides.rshift((h[0] if 0 < len(h) else None), 24) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = ((((h[0] if 0 < len(h) else None) >> 16) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = ((((h[0] if 0 < len(h) else None) >> 8) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = (((h[0] if 0 < len(h) else None) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = (HxOverrides.rshift((h[1] if 1 < len(h) else None), 24) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = ((((h[1] if 1 < len(h) else None) >> 16) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = ((((h[1] if 1 < len(h) else None) >> 8) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = (((h[1] if 1 < len(h) else None) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = (HxOverrides.rshift((h[2] if 2 < len(h) else None), 24) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = ((((h[2] if 2 < len(h) else None) >> 16) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = ((((h[2] if 2 < len(h) else None) >> 8) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = (((h[2] if 2 < len(h) else None) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = (HxOverrides.rshift((h[3] if 3 < len(h) else None), 24) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = ((((h[3] if 3 < len(h) else None) >> 16) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = ((((h[3] if 3 < len(h) else None) >> 8) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = (((h[3] if 3 < len(h) else None) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = (HxOverrides.rshift((h[4] if 4 < len(h) else None), 24) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = ((((h[4] if 4 < len(h) else None) >> 16) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = ((((h[4] if 4 < len(h) else None) >> 8) & 255) & 255)
        pos = p
        p = (p + 1)
        out.b[pos] = (((h[4] if 4 < len(h) else None) & 255) & 255)
        return out

    @staticmethod
    def bytes2blks(b):
        nblk = ((((b.length + 8) >> 6)) + 1)
        blks = list()
        _g = 0
        _g1 = (nblk * 16)
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            python_internal_ArrayImpl._set(blks, i, 0)
        _g = 0
        _g1 = b.length
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            p = (i >> 2)
            python_internal_ArrayImpl._set(blks, p, ((blks[p] if p >= 0 and p < len(blks) else None) | ((b.b[i] << ((24 - ((((i & 3)) << 3))))))))
        i = b.length
        p = (i >> 2)
        python_internal_ArrayImpl._set(blks, p, ((blks[p] if p >= 0 and p < len(blks) else None) | ((128 << ((24 - ((((i & 3)) << 3))))))))
        python_internal_ArrayImpl._set(blks, ((nblk * 16) - 1), (b.length * 8))
        return blks

    @staticmethod
    def _hx_empty_init(_hx_o):        pass
haxe_crypto_Sha1._hx_class = haxe_crypto_Sha1
_hx_classes["haxe.crypto.Sha1"] = haxe_crypto_Sha1


class haxe_ds_IntMap:
    _hx_class_name = "haxe.ds.IntMap"
    __slots__ = ("h",)
    _hx_fields = ["h"]
    _hx_methods = ["set", "keys", "iterator"]
    _hx_interfaces = [haxe_IMap]

    def __init__(self):
        self.h = dict()

    def set(self,key,value):
        self.h[key] = value

    def keys(self):
        return python_HaxeIterator(iter(self.h.keys()))

    def iterator(self):
        return python_HaxeIterator(iter(self.h.values()))

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.h = None
haxe_ds_IntMap._hx_class = haxe_ds_IntMap
_hx_classes["haxe.ds.IntMap"] = haxe_ds_IntMap


class haxe_ds_List:
    _hx_class_name = "haxe.ds.List"
    __slots__ = ("h", "q", "length")
    _hx_fields = ["h", "q", "length"]
    _hx_methods = ["add", "pop", "isEmpty", "remove"]

    def __init__(self):
        self.q = None
        self.h = None
        self.length = 0

    def add(self,item):
        x = haxe_ds__List_ListNode(item,None)
        if (self.h is None):
            self.h = x
        else:
            self.q.next = x
        self.q = x
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0.length
        _hx_local_0.length = (_hx_local_1 + 1)
        _hx_local_1

    def pop(self):
        if (self.h is None):
            return None
        x = self.h.item
        self.h = self.h.next
        if (self.h is None):
            self.q = None
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0.length
        _hx_local_0.length = (_hx_local_1 - 1)
        _hx_local_1
        return x

    def isEmpty(self):
        return (self.h is None)

    def remove(self,v):
        prev = None
        l = self.h
        while (l is not None):
            if HxOverrides.eq(l.item,v):
                if (prev is None):
                    self.h = l.next
                else:
                    prev.next = l.next
                if (self.q == l):
                    self.q = prev
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.length
                _hx_local_0.length = (_hx_local_1 - 1)
                _hx_local_1
                return True
            prev = l
            l = l.next
        return False

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.h = None
        _hx_o.q = None
        _hx_o.length = None
haxe_ds_List._hx_class = haxe_ds_List
_hx_classes["haxe.ds.List"] = haxe_ds_List


class haxe_ds__List_ListNode:
    _hx_class_name = "haxe.ds._List.ListNode"
    __slots__ = ("item", "next")
    _hx_fields = ["item", "next"]

    def __init__(self,item,next):
        self.item = item
        self.next = next

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.item = None
        _hx_o.next = None
haxe_ds__List_ListNode._hx_class = haxe_ds__List_ListNode
_hx_classes["haxe.ds._List.ListNode"] = haxe_ds__List_ListNode


class haxe_ds__List_ListIterator:
    _hx_class_name = "haxe.ds._List.ListIterator"
    __slots__ = ("head",)
    _hx_fields = ["head"]
    _hx_methods = ["hasNext", "next"]

    def __init__(self,head):
        self.head = head

    def hasNext(self):
        return (self.head is not None)

    def next(self):
        val = self.head.item
        self.head = self.head.next
        return val

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.head = None
haxe_ds__List_ListIterator._hx_class = haxe_ds__List_ListIterator
_hx_classes["haxe.ds._List.ListIterator"] = haxe_ds__List_ListIterator


class haxe_ds_ObjectMap:
    _hx_class_name = "haxe.ds.ObjectMap"
    __slots__ = ("h",)
    _hx_fields = ["h"]
    _hx_methods = ["set", "keys"]
    _hx_interfaces = [haxe_IMap]

    def __init__(self):
        self.h = dict()

    def set(self,key,value):
        self.h[key] = value

    def keys(self):
        return python_HaxeIterator(iter(self.h.keys()))

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.h = None
haxe_ds_ObjectMap._hx_class = haxe_ds_ObjectMap
_hx_classes["haxe.ds.ObjectMap"] = haxe_ds_ObjectMap


class haxe_format_JsonPrinter:
    _hx_class_name = "haxe.format.JsonPrinter"
    __slots__ = ("buf", "replacer", "indent", "pretty", "nind")
    _hx_fields = ["buf", "replacer", "indent", "pretty", "nind"]
    _hx_methods = ["write", "classString", "fieldsString", "quote"]
    _hx_statics = ["print"]

    def __init__(self,replacer,space):
        self.replacer = replacer
        self.indent = space
        self.pretty = (space is not None)
        self.nind = 0
        self.buf = StringBuf()

    def write(self,k,v):
        if (self.replacer is not None):
            v = self.replacer(k,v)
        _g = Type.typeof(v)
        tmp = _g.index
        if (tmp == 0):
            self.buf.b.write("null")
        elif (tmp == 1):
            _this = self.buf
            s = Std.string(v)
            _this.b.write(s)
        elif (tmp == 2):
            f = v
            v1 = (Std.string(v) if ((((f != Math.POSITIVE_INFINITY) and ((f != Math.NEGATIVE_INFINITY))) and (not python_lib_Math.isnan(f)))) else "null")
            _this = self.buf
            s = Std.string(v1)
            _this.b.write(s)
        elif (tmp == 3):
            _this = self.buf
            s = Std.string(v)
            _this.b.write(s)
        elif (tmp == 4):
            self.fieldsString(v,python_Boot.fields(v))
        elif (tmp == 5):
            self.buf.b.write("\"<fun>\"")
        elif (tmp == 6):
            c = _g.params[0]
            if (c == str):
                self.quote(v)
            elif (c == list):
                v1 = v
                _this = self.buf
                s = "".join(map(chr,[91]))
                _this.b.write(s)
                _hx_len = len(v1)
                last = (_hx_len - 1)
                _g1 = 0
                _g2 = _hx_len
                while (_g1 < _g2):
                    i = _g1
                    _g1 = (_g1 + 1)
                    if (i > 0):
                        _this = self.buf
                        s = "".join(map(chr,[44]))
                        _this.b.write(s)
                    else:
                        _hx_local_0 = self
                        _hx_local_1 = _hx_local_0.nind
                        _hx_local_0.nind = (_hx_local_1 + 1)
                        _hx_local_1
                    if self.pretty:
                        _this1 = self.buf
                        s1 = "".join(map(chr,[10]))
                        _this1.b.write(s1)
                    if self.pretty:
                        v2 = StringTools.lpad("",self.indent,(self.nind * len(self.indent)))
                        _this2 = self.buf
                        s2 = Std.string(v2)
                        _this2.b.write(s2)
                    self.write(i,(v1[i] if i >= 0 and i < len(v1) else None))
                    if (i == last):
                        _hx_local_2 = self
                        _hx_local_3 = _hx_local_2.nind
                        _hx_local_2.nind = (_hx_local_3 - 1)
                        _hx_local_3
                        if self.pretty:
                            _this3 = self.buf
                            s3 = "".join(map(chr,[10]))
                            _this3.b.write(s3)
                        if self.pretty:
                            v3 = StringTools.lpad("",self.indent,(self.nind * len(self.indent)))
                            _this4 = self.buf
                            s4 = Std.string(v3)
                            _this4.b.write(s4)
                _this = self.buf
                s = "".join(map(chr,[93]))
                _this.b.write(s)
            elif (c == haxe_ds_StringMap):
                v1 = v
                o = _hx_AnonObject({})
                k = v1.keys()
                while k.hasNext():
                    k1 = k.next()
                    value = v1.h.get(k1,None)
                    setattr(o,(("_hx_" + k1) if ((k1 in python_Boot.keywords)) else (("_hx_" + k1) if (((((len(k1) > 2) and ((ord(k1[0]) == 95))) and ((ord(k1[1]) == 95))) and ((ord(k1[(len(k1) - 1)]) != 95)))) else k1)),value)
                v1 = o
                self.fieldsString(v1,python_Boot.fields(v1))
            elif (c == Date):
                v1 = v
                self.quote(v1.toString())
            else:
                self.classString(v)
        elif (tmp == 7):
            _g1 = _g.params[0]
            i = v.index
            _this = self.buf
            s = Std.string(i)
            _this.b.write(s)
        elif (tmp == 8):
            self.buf.b.write("\"???\"")
        else:
            pass

    def classString(self,v):
        self.fieldsString(v,python_Boot.getInstanceFields(Type.getClass(v)))

    def fieldsString(self,v,fields):
        _this = self.buf
        s = "".join(map(chr,[123]))
        _this.b.write(s)
        _hx_len = len(fields)
        last = (_hx_len - 1)
        first = True
        _g = 0
        _g1 = _hx_len
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            f = (fields[i] if i >= 0 and i < len(fields) else None)
            value = Reflect.field(v,f)
            if Reflect.isFunction(value):
                continue
            if first:
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.nind
                _hx_local_0.nind = (_hx_local_1 + 1)
                _hx_local_1
                first = False
            else:
                _this = self.buf
                s = "".join(map(chr,[44]))
                _this.b.write(s)
            if self.pretty:
                _this1 = self.buf
                s1 = "".join(map(chr,[10]))
                _this1.b.write(s1)
            if self.pretty:
                v1 = StringTools.lpad("",self.indent,(self.nind * len(self.indent)))
                _this2 = self.buf
                s2 = Std.string(v1)
                _this2.b.write(s2)
            self.quote(f)
            _this3 = self.buf
            s3 = "".join(map(chr,[58]))
            _this3.b.write(s3)
            if self.pretty:
                _this4 = self.buf
                s4 = "".join(map(chr,[32]))
                _this4.b.write(s4)
            self.write(f,value)
            if (i == last):
                _hx_local_2 = self
                _hx_local_3 = _hx_local_2.nind
                _hx_local_2.nind = (_hx_local_3 - 1)
                _hx_local_3
                if self.pretty:
                    _this5 = self.buf
                    s5 = "".join(map(chr,[10]))
                    _this5.b.write(s5)
                if self.pretty:
                    v2 = StringTools.lpad("",self.indent,(self.nind * len(self.indent)))
                    _this6 = self.buf
                    s6 = Std.string(v2)
                    _this6.b.write(s6)
        _this = self.buf
        s = "".join(map(chr,[125]))
        _this.b.write(s)

    def quote(self,s):
        _this = self.buf
        s1 = "".join(map(chr,[34]))
        _this.b.write(s1)
        i = 0
        length = len(s)
        while (i < length):
            index = i
            i = (i + 1)
            c = ord(s[index])
            c1 = c
            if (c1 == 8):
                self.buf.b.write("\\b")
            elif (c1 == 9):
                self.buf.b.write("\\t")
            elif (c1 == 10):
                self.buf.b.write("\\n")
            elif (c1 == 12):
                self.buf.b.write("\\f")
            elif (c1 == 13):
                self.buf.b.write("\\r")
            elif (c1 == 34):
                self.buf.b.write("\\\"")
            elif (c1 == 92):
                self.buf.b.write("\\\\")
            else:
                _this = self.buf
                s1 = "".join(map(chr,[c]))
                _this.b.write(s1)
        _this = self.buf
        s = "".join(map(chr,[34]))
        _this.b.write(s)

    @staticmethod
    def print(o,replacer = None,space = None):
        printer = haxe_format_JsonPrinter(replacer,space)
        printer.write("",o)
        return printer.buf.b.getvalue()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.buf = None
        _hx_o.replacer = None
        _hx_o.indent = None
        _hx_o.pretty = None
        _hx_o.nind = None
haxe_format_JsonPrinter._hx_class = haxe_format_JsonPrinter
_hx_classes["haxe.format.JsonPrinter"] = haxe_format_JsonPrinter


class haxe_io_ArrayBufferViewImpl:
    _hx_class_name = "haxe.io.ArrayBufferViewImpl"
    __slots__ = ("bytes", "byteOffset", "byteLength")
    _hx_fields = ["bytes", "byteOffset", "byteLength"]
    _hx_methods = ["sub", "subarray"]

    def __init__(self,_hx_bytes,pos,length):
        self.bytes = _hx_bytes
        self.byteOffset = pos
        self.byteLength = length

    def sub(self,begin,length = None):
        if (length is None):
            length = (self.byteLength - begin)
        if (((begin < 0) or ((length < 0))) or (((begin + length) > self.byteLength))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        return haxe_io_ArrayBufferViewImpl(self.bytes,(self.byteOffset + begin),length)

    def subarray(self,begin = None,end = None):
        if (begin is None):
            begin = 0
        if (end is None):
            end = (self.byteLength - begin)
        return self.sub(begin,(end - begin))

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.bytes = None
        _hx_o.byteOffset = None
        _hx_o.byteLength = None
haxe_io_ArrayBufferViewImpl._hx_class = haxe_io_ArrayBufferViewImpl
_hx_classes["haxe.io.ArrayBufferViewImpl"] = haxe_io_ArrayBufferViewImpl


class haxe_io__ArrayBufferView_ArrayBufferView_Impl_:
    _hx_class_name = "haxe.io._ArrayBufferView.ArrayBufferView_Impl_"
    __slots__ = ()
    _hx_statics = ["fromBytes"]

    @staticmethod
    def fromBytes(_hx_bytes,pos = None,length = None):
        if (pos is None):
            pos = 0
        if (length is None):
            length = (_hx_bytes.length - pos)
        if (((pos < 0) or ((length < 0))) or (((pos + length) > _hx_bytes.length))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        return haxe_io_ArrayBufferViewImpl(_hx_bytes,pos,length)
haxe_io__ArrayBufferView_ArrayBufferView_Impl_._hx_class = haxe_io__ArrayBufferView_ArrayBufferView_Impl_
_hx_classes["haxe.io._ArrayBufferView.ArrayBufferView_Impl_"] = haxe_io__ArrayBufferView_ArrayBufferView_Impl_


class haxe_io_BytesBuffer:
    _hx_class_name = "haxe.io.BytesBuffer"
    __slots__ = ("b",)
    _hx_fields = ["b"]
    _hx_methods = ["getBytes"]

    def __init__(self):
        self.b = bytearray()

    def getBytes(self):
        _hx_bytes = haxe_io_Bytes(len(self.b),self.b)
        self.b = None
        return _hx_bytes

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.b = None
haxe_io_BytesBuffer._hx_class = haxe_io_BytesBuffer
_hx_classes["haxe.io.BytesBuffer"] = haxe_io_BytesBuffer


class haxe_io_Input:
    _hx_class_name = "haxe.io.Input"
    __slots__ = ()
haxe_io_Input._hx_class = haxe_io_Input
_hx_classes["haxe.io.Input"] = haxe_io_Input


class haxe_io_Output:
    _hx_class_name = "haxe.io.Output"
    __slots__ = ()
haxe_io_Output._hx_class = haxe_io_Output
_hx_classes["haxe.io.Output"] = haxe_io_Output

class haxe_io_Encoding(Enum):
    __slots__ = ()
    _hx_class_name = "haxe.io.Encoding"
    _hx_constructs = ["UTF8", "RawNative"]
haxe_io_Encoding.UTF8 = haxe_io_Encoding("UTF8", 0, ())
haxe_io_Encoding.RawNative = haxe_io_Encoding("RawNative", 1, ())
haxe_io_Encoding._hx_class = haxe_io_Encoding
_hx_classes["haxe.io.Encoding"] = haxe_io_Encoding

class haxe_io_Error(Enum):
    __slots__ = ()
    _hx_class_name = "haxe.io.Error"
    _hx_constructs = ["Blocked", "Overflow", "OutsideBounds", "Custom"]

    @staticmethod
    def Custom(e):
        return haxe_io_Error("Custom", 3, (e,))
haxe_io_Error.Blocked = haxe_io_Error("Blocked", 0, ())
haxe_io_Error.Overflow = haxe_io_Error("Overflow", 1, ())
haxe_io_Error.OutsideBounds = haxe_io_Error("OutsideBounds", 2, ())
haxe_io_Error._hx_class = haxe_io_Error
_hx_classes["haxe.io.Error"] = haxe_io_Error


class haxe_io__UInt16Array_UInt16Array_Impl_:
    _hx_class_name = "haxe.io._UInt16Array.UInt16Array_Impl_"
    __slots__ = ()
    _hx_statics = ["fromArray"]

    @staticmethod
    def fromArray(a,pos = None,length = None):
        if (pos is None):
            pos = 0
        if (length is None):
            length = (len(a) - pos)
        if (((pos < 0) or ((length < 0))) or (((pos + length) > len(a)))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        size = (len(a) * 2)
        this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(size),0,size)
        this2 = this1
        i = this2
        _g = 0
        _g1 = length
        while (_g < _g1):
            idx = _g
            _g = (_g + 1)
            value = python_internal_ArrayImpl._get(a, (idx + pos))
            if ((idx >= 0) and ((idx < ((i.byteLength >> 1))))):
                _this = i.bytes
                pos1 = (((idx << 1)) + i.byteOffset)
                _this.b[pos1] = (value & 255)
                _this.b[(pos1 + 1)] = ((value >> 8) & 255)
        return i
haxe_io__UInt16Array_UInt16Array_Impl_._hx_class = haxe_io__UInt16Array_UInt16Array_Impl_
_hx_classes["haxe.io._UInt16Array.UInt16Array_Impl_"] = haxe_io__UInt16Array_UInt16Array_Impl_


class haxe_io__UInt8Array_UInt8Array_Impl_:
    _hx_class_name = "haxe.io._UInt8Array.UInt8Array_Impl_"
    __slots__ = ()
    _hx_statics = ["fromData", "fromBytes"]

    @staticmethod
    def fromData(d):
        return d

    @staticmethod
    def fromBytes(_hx_bytes,bytePos = None,length = None):
        if (bytePos is None):
            bytePos = 0
        return haxe_io__UInt8Array_UInt8Array_Impl_.fromData(haxe_io__ArrayBufferView_ArrayBufferView_Impl_.fromBytes(_hx_bytes,bytePos,length))
haxe_io__UInt8Array_UInt8Array_Impl_._hx_class = haxe_io__UInt8Array_UInt8Array_Impl_
_hx_classes["haxe.io._UInt8Array.UInt8Array_Impl_"] = haxe_io__UInt8Array_UInt8Array_Impl_


class haxe_iterators_ArrayIterator:
    _hx_class_name = "haxe.iterators.ArrayIterator"
    __slots__ = ("array", "current")
    _hx_fields = ["array", "current"]
    _hx_methods = ["hasNext", "next"]

    def __init__(self,array):
        self.current = 0
        self.array = array

    def hasNext(self):
        return (self.current < len(self.array))

    def next(self):
        def _hx_local_3():
            def _hx_local_2():
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.current
                _hx_local_0.current = (_hx_local_1 + 1)
                return _hx_local_1
            return python_internal_ArrayImpl._get(self.array, _hx_local_2())
        return _hx_local_3()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.array = None
        _hx_o.current = None
haxe_iterators_ArrayIterator._hx_class = haxe_iterators_ArrayIterator
_hx_classes["haxe.iterators.ArrayIterator"] = haxe_iterators_ArrayIterator


class haxe_iterators_ArrayKeyValueIterator:
    _hx_class_name = "haxe.iterators.ArrayKeyValueIterator"
    __slots__ = ("current", "array")
    _hx_fields = ["current", "array"]
    _hx_methods = ["hasNext", "next"]

    def __init__(self,array):
        self.current = 0
        self.array = array

    def hasNext(self):
        return (self.current < len(self.array))

    def next(self):
        def _hx_local_3():
            def _hx_local_2():
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.current
                _hx_local_0.current = (_hx_local_1 + 1)
                return _hx_local_1
            return _hx_AnonObject({'value': python_internal_ArrayImpl._get(self.array, self.current), 'key': _hx_local_2()})
        return _hx_local_3()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.current = None
        _hx_o.array = None
haxe_iterators_ArrayKeyValueIterator._hx_class = haxe_iterators_ArrayKeyValueIterator
_hx_classes["haxe.iterators.ArrayKeyValueIterator"] = haxe_iterators_ArrayKeyValueIterator


class hx_concurrent_ConcurrentException:
    _hx_class_name = "hx.concurrent.ConcurrentException"
    __slots__ = ("cause", "causeStackTrace")
    _hx_fields = ["cause", "causeStackTrace"]
    _hx_methods = ["rethrow", "toString"]

    def __init__(self,cause):
        self.cause = cause
        self.causeStackTrace = haxe__CallStack_CallStack_Impl_.exceptionStack()

    def rethrow(self):
        raise Exception(self.toString()) from None

    def toString(self):
        sb_b = python_lib_io_StringIO()
        sb_b.write("rethrown exception:\n")
        sb_b.write("  ")
        sb_b.write("--------------------\n")
        sb_b.write("  ")
        sb_b.write("| Exception : ")
        sb_b.write(Std.string(self.cause))
        sb_b.write("\n")
        _g = 0
        _this = haxe__CallStack_CallStack_Impl_.toString(self.causeStackTrace)
        _g1 = _this.split("\n")
        while (_g < len(_g1)):
            item = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            if (item == ""):
                continue
            sb_b.write("  ")
            sb_b.write(Std.string(StringTools.replace(item,"Called from","| at")))
            sb_b.write("\n")
        sb_b.write("  ")
        sb_b.write("--------------------")
        return sb_b.getvalue()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.cause = None
        _hx_o.causeStackTrace = None
hx_concurrent_ConcurrentException._hx_class = hx_concurrent_ConcurrentException
_hx_classes["hx.concurrent.ConcurrentException"] = hx_concurrent_ConcurrentException


class hx_concurrent_Future:
    _hx_class_name = "hx.concurrent.Future"
    __slots__ = ()
hx_concurrent_Future._hx_class = hx_concurrent_Future
_hx_classes["hx.concurrent.Future"] = hx_concurrent_Future

class hx_concurrent_FutureResult(Enum):
    __slots__ = ()
    _hx_class_name = "hx.concurrent.FutureResult"
    _hx_constructs = ["SUCCESS", "FAILURE", "NONE"]

    @staticmethod
    def SUCCESS(result,time,future):
        return hx_concurrent_FutureResult("SUCCESS", 0, (result,time,future))

    @staticmethod
    def FAILURE(ex,time,future):
        return hx_concurrent_FutureResult("FAILURE", 1, (ex,time,future))

    @staticmethod
    def NONE(future):
        return hx_concurrent_FutureResult("NONE", 2, (future,))
hx_concurrent_FutureResult._hx_class = hx_concurrent_FutureResult
_hx_classes["hx.concurrent.FutureResult"] = hx_concurrent_FutureResult


class hx_concurrent_FutureBase:
    _hx_class_name = "hx.concurrent.FutureBase"
    __slots__ = ("result", "onResult")
    _hx_fields = ["result", "onResult"]
    _hx_interfaces = [hx_concurrent_Future]

    def __init__(self):
        self.onResult = None
        self.result = None
        self.result = hx_concurrent_FutureResult.NONE(self)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.result = None
        _hx_o.onResult = None
hx_concurrent_FutureBase._hx_class = hx_concurrent_FutureBase
_hx_classes["hx.concurrent.FutureBase"] = hx_concurrent_FutureBase


class hx_concurrent_Service:
    _hx_class_name = "hx.concurrent.Service"
    __slots__ = ()
hx_concurrent_Service._hx_class = hx_concurrent_Service
_hx_classes["hx.concurrent.Service"] = hx_concurrent_Service

class hx_concurrent_ServiceState(Enum):
    __slots__ = ()
    _hx_class_name = "hx.concurrent.ServiceState"
    _hx_constructs = ["STARTING", "RUNNING", "STOPPING", "STOPPED"]
hx_concurrent_ServiceState.STARTING = hx_concurrent_ServiceState("STARTING", 0, ())
hx_concurrent_ServiceState.RUNNING = hx_concurrent_ServiceState("RUNNING", 1, ())
hx_concurrent_ServiceState.STOPPING = hx_concurrent_ServiceState("STOPPING", 2, ())
hx_concurrent_ServiceState.STOPPED = hx_concurrent_ServiceState("STOPPED", 3, ())
hx_concurrent_ServiceState._hx_class = hx_concurrent_ServiceState
_hx_classes["hx.concurrent.ServiceState"] = hx_concurrent_ServiceState


class hx_concurrent_ServiceBase:
    _hx_class_name = "hx.concurrent.ServiceBase"
    __slots__ = ("id", "state", "_stateLock")
    _hx_fields = ["id", "state", "_stateLock"]
    _hx_methods = ["set_state", "start", "onStart", "toString"]
    _hx_statics = ["_ids"]
    _hx_interfaces = [hx_concurrent_Service]

    def __init__(self):
        self._stateLock = hx_concurrent_lock_RLock()
        self.state = hx_concurrent_ServiceState.STOPPED
        self.id = hx_concurrent_ServiceBase._ids.incrementAndGet()
        haxe_Log.trace((("[" + Std.string(self)) + "] instantiated."),_hx_AnonObject({'fileName': "hx/concurrent/Service.hx", 'lineNumber': 57, 'className': "hx.concurrent.ServiceBase", 'methodName': "new"}))

    def set_state(self,s):
        tmp = s.index
        if (tmp == 0):
            haxe_Log.trace((("[" + Std.string(self)) + "] is starting..."),_hx_AnonObject({'fileName': "hx/concurrent/Service.hx", 'lineNumber': 46, 'className': "hx.concurrent.ServiceBase", 'methodName': "set_state"}))
        elif (tmp == 1):
            haxe_Log.trace((("[" + Std.string(self)) + "] is running."),_hx_AnonObject({'fileName': "hx/concurrent/Service.hx", 'lineNumber': 47, 'className': "hx.concurrent.ServiceBase", 'methodName': "set_state"}))
        elif (tmp == 2):
            haxe_Log.trace((("[" + Std.string(self)) + "] is stopping..."),_hx_AnonObject({'fileName': "hx/concurrent/Service.hx", 'lineNumber': 48, 'className': "hx.concurrent.ServiceBase", 'methodName': "set_state"}))
        elif (tmp == 3):
            haxe_Log.trace((("[" + Std.string(self)) + "] is stopped."),_hx_AnonObject({'fileName': "hx/concurrent/Service.hx", 'lineNumber': 49, 'className': "hx.concurrent.ServiceBase", 'methodName': "set_state"}))
        else:
            pass
        def _hx_local_1():
            def _hx_local_0():
                self.state = s
                return self.state
            return _hx_local_0()
        return _hx_local_1()

    def start(self):
        _gthis = self
        def _hx_local_0():
            tmp = _gthis.state.index
            if (tmp == 0):
                pass
            elif (tmp == 1):
                pass
            elif (tmp == 2):
                raise haxe_Exception.thrown((("Service [" + Std.string(_gthis)) + "] is currently stopping!"))
            elif (tmp == 3):
                _gthis.set_state(hx_concurrent_ServiceState.STARTING)
                _gthis.onStart()
                _gthis.set_state(hx_concurrent_ServiceState.RUNNING)
            else:
                pass
        self._stateLock.execute(_hx_local_0)

    def onStart(self):
        pass

    def toString(self):
        return ((HxOverrides.stringOrNull(Type.getClassName(Type.getClass(self))) + "#") + Std.string(self.id))

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.id = None
        _hx_o.state = None
        _hx_o._stateLock = None
hx_concurrent_ServiceBase._hx_class = hx_concurrent_ServiceBase
_hx_classes["hx.concurrent.ServiceBase"] = hx_concurrent_ServiceBase


class hx_concurrent_collection_Queue:
    _hx_class_name = "hx.concurrent.collection.Queue"
    __slots__ = ("_queue", "_length")
    _hx_fields = ["_queue", "_length"]
    _hx_methods = ["pop", "push"]

    def __init__(self):
        self._length = hx_concurrent_atomic__AtomicInt_AtomicIntImpl(0)
        import collections
        self._queue = collections.deque()

    def pop(self,timeoutMS = None):
        if (timeoutMS is None):
            timeoutMS = 0
        _gthis = self
        msg = None
        if (timeoutMS < -1):
            raise haxe_Exception.thrown("[timeoutMS] must be >= -1")
        if (timeoutMS == 0):
            try:
                msg = Reflect.field(self._queue,"pop")()
            except BaseException as _g:
                None
                msg = None
        else:
            def _hx_local_0():
                nonlocal msg
                nonlocal msg
                try:
                    msg = Reflect.field(_gthis._queue,"pop")()
                except BaseException as _g:
                    None
                    msg = None
                return (msg is not None)
            hx_concurrent_thread_Threads._hx_await(_hx_local_0,timeoutMS)
        if (msg is not None):
            self._length.getAndIncrement(-1)
        return msg

    def push(self,msg):
        if (msg is None):
            raise haxe_Exception.thrown("[msg] must not be null")
        Reflect.field(self._queue,"appendleft")(msg)
        self._length.getAndIncrement()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._queue = None
        _hx_o._length = None
hx_concurrent_collection_Queue._hx_class = hx_concurrent_collection_Queue
_hx_classes["hx.concurrent.collection.Queue"] = hx_concurrent_collection_Queue

class hx_concurrent_executor_Schedule(Enum):
    __slots__ = ()
    _hx_class_name = "hx.concurrent.executor.Schedule"
    _hx_constructs = ["ONCE", "FIXED_DELAY", "FIXED_RATE", "HOURLY", "DAILY", "WEEKLY"]

    @staticmethod
    def ONCE(initialDelayMS = None):
        return hx_concurrent_executor_Schedule("ONCE", 0, (initialDelayMS,))

    @staticmethod
    def FIXED_DELAY(intervalMS,initialDelayMS = None):
        return hx_concurrent_executor_Schedule("FIXED_DELAY", 1, (intervalMS,initialDelayMS))

    @staticmethod
    def FIXED_RATE(intervalMS,initialDelayMS = None):
        return hx_concurrent_executor_Schedule("FIXED_RATE", 2, (intervalMS,initialDelayMS))

    @staticmethod
    def HOURLY(minute = None,second= None):
        return hx_concurrent_executor_Schedule("HOURLY", 3, (minute,second))

    @staticmethod
    def DAILY(hour = None,minute= None,second= None):
        return hx_concurrent_executor_Schedule("DAILY", 4, (hour,minute,second))

    @staticmethod
    def WEEKLY(day = None,hour= None,minute= None,second= None):
        return hx_concurrent_executor_Schedule("WEEKLY", 5, (day,hour,minute,second))
hx_concurrent_executor_Schedule._hx_class = hx_concurrent_executor_Schedule
_hx_classes["hx.concurrent.executor.Schedule"] = hx_concurrent_executor_Schedule


class hx_concurrent_executor_Executor(hx_concurrent_ServiceBase):
    _hx_class_name = "hx.concurrent.executor.Executor"
    __slots__ = ("onResult",)
    _hx_fields = ["onResult"]
    _hx_methods = ["submit"]
    _hx_statics = ["NOW_ONCE", "create"]
    _hx_interfaces = []
    _hx_super = hx_concurrent_ServiceBase


    def __init__(self):
        def _hx_local_0(result):
            if (result.index == 1):
                _g1 = result.params[1]
                _g1 = result.params[2]
                ex = result.params[0]
                haxe_Log.trace(ex,_hx_AnonObject({'fileName': "hx/concurrent/executor/Executor.hx", 'lineNumber': 45, 'className': "hx.concurrent.executor.Executor", 'methodName': "onResult"}))
        self.onResult = _hx_local_0
        super().__init__()

    def submit(self,task,schedule = None):
        raise haxe_Exception.thrown("Not implemented")

    @staticmethod
    def create(maxConcurrent = None,autostart = None):
        if (maxConcurrent is None):
            maxConcurrent = 1
        if (autostart is None):
            autostart = True
        if hx_concurrent_thread_Threads.get_isSupported():
            return hx_concurrent_executor_ThreadPoolExecutor(maxConcurrent,autostart)
        return hx_concurrent_executor_TimerExecutor(autostart)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.onResult = None
hx_concurrent_executor_Executor._hx_class = hx_concurrent_executor_Executor
_hx_classes["hx.concurrent.executor.Executor"] = hx_concurrent_executor_Executor


class hx_concurrent_executor_TaskFuture:
    _hx_class_name = "hx.concurrent.executor.TaskFuture"
    __slots__ = ()
    _hx_interfaces = [hx_concurrent_Future]
hx_concurrent_executor_TaskFuture._hx_class = hx_concurrent_executor_TaskFuture
_hx_classes["hx.concurrent.executor.TaskFuture"] = hx_concurrent_executor_TaskFuture


class hx_concurrent_executor_TaskFutureBase(hx_concurrent_FutureBase):
    _hx_class_name = "hx.concurrent.executor.TaskFutureBase"
    __slots__ = ("schedule", "isStopped", "_executor", "_task")
    _hx_fields = ["schedule", "isStopped", "_executor", "_task"]
    _hx_methods = ["cancel"]
    _hx_statics = []
    _hx_interfaces = [hx_concurrent_executor_TaskFuture]
    _hx_super = hx_concurrent_FutureBase


    def __init__(self,executor,task,schedule):
        self._task = None
        self._executor = None
        self.schedule = None
        self.isStopped = False
        super().__init__()
        self._executor = executor
        self._task = task
        self.schedule = hx_concurrent_executor_ScheduleTools.assertValid(schedule)

    def cancel(self):
        self.isStopped = True

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.schedule = None
        _hx_o.isStopped = None
        _hx_o._executor = None
        _hx_o._task = None
hx_concurrent_executor_TaskFutureBase._hx_class = hx_concurrent_executor_TaskFutureBase
_hx_classes["hx.concurrent.executor.TaskFutureBase"] = hx_concurrent_executor_TaskFutureBase


class hx_concurrent_executor_ScheduleTools:
    _hx_class_name = "hx.concurrent.executor.ScheduleTools"
    __slots__ = ()
    _hx_statics = ["applyDefaults", "assertValid", "firstRunAt"]

    @staticmethod
    def applyDefaults(schedule):
        tmp = schedule.index
        if (tmp == 0):
            initialDelayMS = schedule.params[0]
            if (initialDelayMS is None):
                return hx_concurrent_executor_Schedule.ONCE(0)
        elif (tmp == 1):
            intervalMS = schedule.params[0]
            initialDelayMS = schedule.params[1]
            if (initialDelayMS is None):
                return hx_concurrent_executor_Schedule.FIXED_DELAY(intervalMS,0)
        elif (tmp == 2):
            intervalMS = schedule.params[0]
            initialDelayMS = schedule.params[1]
            if (initialDelayMS is None):
                return hx_concurrent_executor_Schedule.FIXED_RATE(intervalMS,0)
        elif (tmp == 3):
            minute = schedule.params[0]
            second = schedule.params[1]
            if ((minute is None) or ((second is None))):
                return hx_concurrent_executor_Schedule.HOURLY((0 if ((minute is None)) else minute),(0 if ((second is None)) else second))
        elif (tmp == 4):
            hour = schedule.params[0]
            minute = schedule.params[1]
            second = schedule.params[2]
            if (((hour is None) or ((minute is None))) or ((second is None))):
                return hx_concurrent_executor_Schedule.DAILY((0 if ((hour is None)) else hour),(0 if ((minute is None)) else minute),(0 if ((second is None)) else second))
        elif (tmp == 5):
            day = schedule.params[0]
            hour = schedule.params[1]
            minute = schedule.params[2]
            second = schedule.params[3]
            if ((((day is None) or ((hour is None))) or ((minute is None))) or ((second is None))):
                return hx_concurrent_executor_Schedule.WEEKLY((0 if ((day is None)) else day),(0 if ((hour is None)) else hour),(0 if ((minute is None)) else minute),(0 if ((second is None)) else second))
        else:
            pass
        return schedule

    @staticmethod
    def assertValid(schedule):
        schedule = hx_concurrent_executor_ScheduleTools.applyDefaults(schedule)
        tmp = schedule.index
        if (tmp == 0):
            initialDelayMS = schedule.params[0]
            if (initialDelayMS < 0):
                raise haxe_Exception.thrown("[Schedule.ONCE.initialDelayMS] must be >= 0")
        elif (tmp == 1):
            intervalMS = schedule.params[0]
            initialDelayMS = schedule.params[1]
            if (intervalMS <= 0):
                raise haxe_Exception.thrown("[Schedule.FIXED_DELAY.intervalMS] must be > 0")
            if ((initialDelayMS is None) or ((initialDelayMS < 0))):
                raise haxe_Exception.thrown("[Schedule.FIXED_DELAY.initialDelayMS] must be >= 0")
        elif (tmp == 2):
            intervalMS = schedule.params[0]
            initialDelayMS = schedule.params[1]
            if (intervalMS <= 0):
                raise haxe_Exception.thrown("[Schedule.FIXED_RATE.intervalMS] must be > 0")
            if (initialDelayMS < 0):
                raise haxe_Exception.thrown("[Schedule.FIXED_RATE.initialDelayMS] must be >= 0")
        elif (tmp == 3):
            minute = schedule.params[0]
            second = schedule.params[1]
            if ((minute is None) or ((minute < 0))):
                raise haxe_Exception.thrown("[Schedule.DAILY.minute] must be between >= 0 and <= 59")
            if ((second is None) or ((second < 0))):
                raise haxe_Exception.thrown("[Schedule.DAILY.second] must be between >= 0 and <= 59")
        elif (tmp == 4):
            hour = schedule.params[0]
            minute = schedule.params[1]
            second = schedule.params[2]
            if ((hour is None) or ((hour < 0))):
                raise haxe_Exception.thrown("[Schedule.DAILY.hour] must be between >= 0 and <= 23")
            if ((minute is None) or ((minute < 0))):
                raise haxe_Exception.thrown("[Schedule.DAILY.minute] must be between >= 0 and <= 59")
            if ((second is None) or ((second < 0))):
                raise haxe_Exception.thrown("[Schedule.DAILY.second] must be between >= 0 and <= 59")
        elif (tmp == 5):
            day = schedule.params[0]
            hour = schedule.params[1]
            minute = schedule.params[2]
            second = schedule.params[3]
            if ((hour is None) or ((hour < 0))):
                raise haxe_Exception.thrown("[Schedule.WEEKLY.hour] must be between >= 0 and <= 23")
            if ((minute is None) or ((minute < 0))):
                raise haxe_Exception.thrown("[Schedule.WEEKLY.minute] must be between >= 0 and <= 59")
            if ((second is None) or ((second < 0))):
                raise haxe_Exception.thrown("[Schedule.WEEKLY.second] must be between >= 0 and <= 59")
        else:
            pass
        return schedule

    @staticmethod
    def firstRunAt(schedule):
        schedule = hx_concurrent_executor_ScheduleTools.assertValid(schedule)
        tmp = schedule.index
        if (tmp == 0):
            initialDelayMS = schedule.params[0]
            return ((python_lib_Time.time() * 1000) + initialDelayMS)
        elif (tmp == 1):
            intervalMS = schedule.params[0]
            initialDelayMS = schedule.params[1]
            return ((python_lib_Time.time() * 1000) + initialDelayMS)
        elif (tmp == 2):
            intervalMS = schedule.params[0]
            initialDelayMS = schedule.params[1]
            return ((python_lib_Time.time() * 1000) + initialDelayMS)
        elif (tmp == 3):
            minute = schedule.params[0]
            second = schedule.params[1]
            nowMS = (python_lib_Time.time() * 1000)
            now = Date.fromTime(nowMS)
            runAtSecondOfHour = ((minute * 60) + second)
            elapsedSecondsThisHour = ((now.date.minute * 60) + now.date.second)
            return ((nowMS + ((((runAtSecondOfHour - elapsedSecondsThisHour)) * 1000))) + ((3600000 if ((elapsedSecondsThisHour > runAtSecondOfHour)) else 0)))
        elif (tmp == 4):
            hour = schedule.params[0]
            minute = schedule.params[1]
            second = schedule.params[2]
            nowMS = (python_lib_Time.time() * 1000)
            now = Date.fromTime(nowMS)
            runAtSecondOfDay = ((((hour * 60) * 60) + ((minute * 60))) + second)
            elapsedSecondsToday = ((((now.date.hour * 60) * 60) + ((now.date.minute * 60))) + now.date.second)
            return ((nowMS + ((((runAtSecondOfDay - elapsedSecondsToday)) * 1000))) + ((86400000 if ((elapsedSecondsToday > runAtSecondOfDay)) else 0)))
        elif (tmp == 5):
            day = schedule.params[0]
            hour = schedule.params[1]
            minute = schedule.params[2]
            second = schedule.params[3]
            nowMS = (python_lib_Time.time() * 1000)
            now = Date.fromTime(nowMS)
            runAtSecondOfDay = ((((hour * 60) * 60) + ((minute * 60))) + second)
            elapsedSecondsToday = ((((now.date.hour * 60) * 60) + ((now.date.minute * 60))) + now.date.second)
            dayIndex = day
            if (dayIndex == (HxOverrides.mod(now.date.isoweekday(), 7))):
                return ((nowMS + ((((runAtSecondOfDay - elapsedSecondsToday)) * 1000))) + ((604800000 if ((elapsedSecondsToday > runAtSecondOfDay)) else 0)))
            elif (now.date.day < dayIndex):
                return ((nowMS + ((((runAtSecondOfDay - elapsedSecondsToday)) * 1000))) + ((86400000 * ((dayIndex - now.date.day)))))
            else:
                return ((nowMS + ((((runAtSecondOfDay - elapsedSecondsToday)) * 1000))) + ((86400000 * ((7 - ((dayIndex - now.date.day)))))))
        else:
            pass
hx_concurrent_executor_ScheduleTools._hx_class = hx_concurrent_executor_ScheduleTools
_hx_classes["hx.concurrent.executor.ScheduleTools"] = hx_concurrent_executor_ScheduleTools


class hx_concurrent_executor_ThreadPoolExecutor(hx_concurrent_executor_Executor):
    _hx_class_name = "hx.concurrent.executor.ThreadPoolExecutor"
    __slots__ = ("_threadPool", "_scheduledTasks", "_newScheduledTasks")
    _hx_fields = ["_threadPool", "_scheduledTasks", "_newScheduledTasks"]
    _hx_methods = ["onStart", "submit"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = hx_concurrent_executor_Executor


    def __init__(self,threadPoolSize,autostart = None):
        if (autostart is None):
            autostart = True
        self._threadPool = None
        self._newScheduledTasks = hx_concurrent_collection_Queue()
        self._scheduledTasks = list()
        if (threadPoolSize < 1):
            raise haxe_Exception.thrown("[threadPoolSize] must be > 0")
        super().__init__()
        self._threadPool = hx_concurrent_thread_ThreadPool(threadPoolSize,autostart)
        if autostart:
            self.start()

    def onStart(self):
        _gthis = self
        self.set_state(hx_concurrent_ServiceState.RUNNING)
        def _hx_local_7():
            doneTasks = list()
            while (_gthis.state == hx_concurrent_ServiceState.RUNNING):
                _g = 0
                _g1 = _gthis._scheduledTasks
                while (_g < len(_g1)):
                    t = [(_g1[_g] if _g >= 0 and _g < len(_g1) else None)]
                    _g = (_g + 1)
                    if (t[0] if 0 < len(t) else None).isDue():
                        def _hx_local_2(t):
                            def _hx_local_1(ctx):
                                (t[0] if 0 < len(t) else None).run()
                            return _hx_local_1
                        _gthis._threadPool.submit(_hx_local_2(t))
                    elif (t[0] if 0 < len(t) else None).isStopped:
                        doneTasks.append((t[0] if 0 < len(t) else None))
                if (len(doneTasks) > 0):
                    _g2 = 0
                    while (_g2 < len(doneTasks)):
                        t1 = (doneTasks[_g2] if _g2 >= 0 and _g2 < len(doneTasks) else None)
                        _g2 = (_g2 + 1)
                        python_internal_ArrayImpl.remove(_gthis._scheduledTasks,t1)
                    l = len(doneTasks)
                    if (l < 0):
                        idx = -1
                        v = None
                        l1 = len(doneTasks)
                        while (l1 < idx):
                            doneTasks.append(None)
                            l1 = (l1 + 1)
                        if (l1 == idx):
                            doneTasks.append(v)
                        else:
                            doneTasks[idx] = v
                    elif (l > 0):
                        pos = 0
                        _hx_len = l
                        if (pos < 0):
                            pos = (len(doneTasks) + pos)
                        if (pos < 0):
                            pos = 0
                        res = doneTasks[pos:(pos + _hx_len)]
                        del doneTasks[pos:(pos + _hx_len)]
                t2 = _gthis._newScheduledTasks.pop()
                if (t2 is None):
                    Sys.sleep(0.01)
                    continue
                startAt = (python_lib_Time.time() * 1000)
                _this = _gthis._scheduledTasks
                _this.append(t2)
                while (not ((((python_lib_Time.time() * 1000) - startAt) > 10))):
                    t3 = _gthis._newScheduledTasks.pop()
                    if (t3 is None):
                        break
                    _this1 = _gthis._scheduledTasks
                    _this1.append(t3)
            _g = 0
            _g1 = _gthis._scheduledTasks
            while (_g < len(_g1)):
                t1 = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                t1.cancel()
            while True:
                t1 = _gthis._newScheduledTasks.pop()
                if (t1 is None):
                    break
                t1.cancel()
            def _hx_local_6():
                return (_gthis._threadPool.state == hx_concurrent_ServiceState.STOPPED)
            hx_concurrent_thread_Threads._hx_await(_hx_local_6,-1)
            _gthis.set_state(hx_concurrent_ServiceState.STOPPED)
        t = python_lib_threading_Thread(**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'target': _hx_local_7})))
        t.daemon = True
        t.start()

    def submit(self,task,schedule = None):
        _gthis = self
        def _hx_local_2():
            def _hx_local_1():
                nonlocal schedule
                if (_gthis.state != hx_concurrent_ServiceState.RUNNING):
                    raise haxe_Exception.thrown((("Cannot accept new tasks. Executor is not in state [RUNNING] but [" + Std.string(_gthis.state)) + "]."))
                if (schedule is None):
                    schedule = hx_concurrent_executor_Executor.NOW_ONCE
                future = hx_concurrent_executor__ThreadPoolExecutor_TaskFutureImpl(_gthis,task,schedule)
                if (schedule is not None):
                    if (schedule.index == 0):
                        _g = schedule.params[0]
                        if future.isDue():
                            def _hx_local_0(ctx):
                                future.run()
                            _gthis._threadPool.submit(_hx_local_0)
                            return future
                _gthis._newScheduledTasks.push(future)
                return future
            return self._stateLock.execute(_hx_local_1)
        return _hx_local_2()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._threadPool = None
        _hx_o._scheduledTasks = None
        _hx_o._newScheduledTasks = None
hx_concurrent_executor_ThreadPoolExecutor._hx_class = hx_concurrent_executor_ThreadPoolExecutor
_hx_classes["hx.concurrent.executor.ThreadPoolExecutor"] = hx_concurrent_executor_ThreadPoolExecutor


class hx_concurrent_executor__ThreadPoolExecutor_TaskFutureImpl(hx_concurrent_executor_TaskFutureBase):
    _hx_class_name = "hx.concurrent.executor._ThreadPoolExecutor.TaskFutureImpl"
    __slots__ = ("_nextRunAt",)
    _hx_fields = ["_nextRunAt"]
    _hx_methods = ["isDue", "run"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = hx_concurrent_executor_TaskFutureBase


    def __init__(self,executor,task,schedule):
        self._nextRunAt = None
        super().__init__(executor,task,schedule)
        self._nextRunAt = hx_concurrent_executor_ScheduleTools.firstRunAt(self.schedule)

    def isDue(self):
        if (self.isStopped or ((self._nextRunAt == -1))):
            return False
        if ((python_lib_Time.time() * 1000) >= self._nextRunAt):
            _g = self.schedule
            tmp = _g.index
            if (tmp == 0):
                _g1 = _g.params[0]
                self._nextRunAt = -1
            elif (tmp == 1):
                _g1 = _g.params[0]
                _g1 = _g.params[1]
                self._nextRunAt = -1
            elif (tmp == 2):
                _g1 = _g.params[1]
                intervalMS = _g.params[0]
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0._nextRunAt
                _hx_local_0._nextRunAt = (_hx_local_1 + intervalMS)
                _hx_local_0._nextRunAt
            elif (tmp == 3):
                _g1 = _g.params[0]
                _g1 = _g.params[1]
                _hx_local_2 = self
                _hx_local_3 = _hx_local_2._nextRunAt
                _hx_local_2._nextRunAt = (_hx_local_3 + 3600000)
                _hx_local_2._nextRunAt
            elif (tmp == 4):
                _g1 = _g.params[0]
                _g1 = _g.params[1]
                _g1 = _g.params[2]
                _hx_local_4 = self
                _hx_local_5 = _hx_local_4._nextRunAt
                _hx_local_4._nextRunAt = (_hx_local_5 + 86400000)
                _hx_local_4._nextRunAt
            elif (tmp == 5):
                _g1 = _g.params[0]
                _g1 = _g.params[1]
                _g1 = _g.params[2]
                _g1 = _g.params[3]
                _hx_local_6 = self
                _hx_local_7 = _hx_local_6._nextRunAt
                _hx_local_6._nextRunAt = (_hx_local_7 + 604800000)
                _hx_local_6._nextRunAt
            else:
                pass
            return True
        return False

    def run(self):
        if self.isStopped:
            return
        result = hx_concurrent_FutureResult.NONE(self)
        try:
            resultValue = None
            _g = self._task
            resultValue1 = _g.index
            if (resultValue1 == 0):
                fn = _g.params[0]
                resultValue = fn()
            elif (resultValue1 == 1):
                fn = _g.params[0]
                fn()
                resultValue = None
            else:
                pass
            result = hx_concurrent_FutureResult.SUCCESS(resultValue,(python_lib_Time.time() * 1000),self)
        except BaseException as _g:
            None
            ex = haxe_Exception.caught(_g).unwrap()
            result = hx_concurrent_FutureResult.FAILURE(hx_concurrent_ConcurrentException(ex),(python_lib_Time.time() * 1000),self)
        _g = self.schedule
        tmp = _g.index
        if (tmp == 0):
            _g1 = _g.params[0]
            self.isStopped = True
        elif (tmp == 1):
            _g1 = _g.params[1]
            intervalMS = _g.params[0]
            self._nextRunAt = ((python_lib_Time.time() * 1000) + intervalMS)
        else:
            pass
        self.result = result
        fn = self.onResult
        if (fn is not None):
            try:
                fn(result)
            except BaseException as _g:
                None
                ex = haxe_Exception.caught(_g).unwrap()
                haxe_Log.trace(ex,_hx_AnonObject({'fileName': "hx/concurrent/executor/ThreadPoolExecutor.hx", 'lineNumber': 217, 'className': "hx.concurrent.executor._ThreadPoolExecutor.TaskFutureImpl", 'methodName': "run"}))
        fn = self._executor.onResult
        if (fn is not None):
            try:
                fn(result)
            except BaseException as _g:
                None
                ex = haxe_Exception.caught(_g).unwrap()
                haxe_Log.trace(ex,_hx_AnonObject({'fileName': "hx/concurrent/executor/ThreadPoolExecutor.hx", 'lineNumber': 219, 'className': "hx.concurrent.executor._ThreadPoolExecutor.TaskFutureImpl", 'methodName': "run"}))

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._nextRunAt = None
hx_concurrent_executor__ThreadPoolExecutor_TaskFutureImpl._hx_class = hx_concurrent_executor__ThreadPoolExecutor_TaskFutureImpl
_hx_classes["hx.concurrent.executor._ThreadPoolExecutor.TaskFutureImpl"] = hx_concurrent_executor__ThreadPoolExecutor_TaskFutureImpl


class hx_concurrent_executor_TimerExecutor(hx_concurrent_executor_Executor):
    _hx_class_name = "hx.concurrent.executor.TimerExecutor"
    __slots__ = ("_scheduledTasks",)
    _hx_fields = ["_scheduledTasks"]
    _hx_methods = ["submit"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = hx_concurrent_executor_Executor


    def __init__(self,autostart = None):
        if (autostart is None):
            autostart = True
        self._scheduledTasks = []
        super().__init__()
        if autostart:
            self.start()

    def submit(self,task,schedule = None):
        _gthis = self
        def _hx_local_1():
            def _hx_local_0():
                if (_gthis.state != hx_concurrent_ServiceState.RUNNING):
                    raise haxe_Exception.thrown((("Cannot accept new tasks. Executor is not in state [RUNNING] but [" + Std.string(_gthis.state)) + "]."))
                i = len(_gthis._scheduledTasks)
                while True:
                    tmp = i
                    i = (i - 1)
                    if (not ((tmp > 0))):
                        break
                    if (_gthis._scheduledTasks[i] if i >= 0 and i < len(_gthis._scheduledTasks) else None).isStopped:
                        _this = _gthis._scheduledTasks
                        pos = i
                        if (pos < 0):
                            pos = (len(_this) + pos)
                        if (pos < 0):
                            pos = 0
                        res = _this[pos:(pos + 1)]
                        del _this[pos:(pos + 1)]
                future = hx_concurrent_executor__TimerExecutor_TaskFutureImpl(_gthis,task,(hx_concurrent_executor_Executor.NOW_ONCE if ((schedule is None)) else schedule))
                if (schedule is None):
                    _this = _gthis._scheduledTasks
                    _this.append(future)
                elif (schedule.index == 0):
                    _g = schedule.params[0]
                    if (_g is None):
                        _this = _gthis._scheduledTasks
                        _this.append(future)
                    elif (_g != 0):
                        _this = _gthis._scheduledTasks
                        _this.append(future)
                else:
                    _this = _gthis._scheduledTasks
                    _this.append(future)
                return future
            return self._stateLock.execute(_hx_local_0)
        return _hx_local_1()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._scheduledTasks = None
hx_concurrent_executor_TimerExecutor._hx_class = hx_concurrent_executor_TimerExecutor
_hx_classes["hx.concurrent.executor.TimerExecutor"] = hx_concurrent_executor_TimerExecutor


class hx_concurrent_executor__TimerExecutor_TaskFutureImpl(hx_concurrent_executor_TaskFutureBase):
    _hx_class_name = "hx.concurrent.executor._TimerExecutor.TaskFutureImpl"
    __slots__ = ("_timer",)
    _hx_fields = ["_timer"]
    _hx_methods = ["run", "cancel"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = hx_concurrent_executor_TaskFutureBase


    def __init__(self,executor,task,schedule):
        self._timer = None
        super().__init__(executor,task,schedule)
        x = (hx_concurrent_executor_ScheduleTools.firstRunAt(self.schedule) - ((python_lib_Time.time() * 1000)))
        initialDelay = None
        try:
            initialDelay = int(x)
        except BaseException as _g:
            None
            initialDelay = None
        if (initialDelay < 0):
            initialDelay = 0
        haxe_Timer.delay(self.run,initialDelay)

    def run(self):
        if self.isStopped:
            return
        if (self._timer is None):
            t = None
            _g = self.schedule
            tmp = _g.index
            if (tmp == 2):
                _g1 = _g.params[1]
                intervalMS = _g.params[0]
                t = haxe_Timer(intervalMS)
                t.run = self.run
            elif (tmp == 3):
                _g1 = _g.params[0]
                _g1 = _g.params[1]
                t = haxe_Timer(3600000)
                t.run = self.run
            elif (tmp == 4):
                _g1 = _g.params[0]
                _g1 = _g.params[1]
                _g1 = _g.params[2]
                t = haxe_Timer(86400000)
                t.run = self.run
            elif (tmp == 5):
                _g1 = _g.params[0]
                _g1 = _g.params[1]
                _g1 = _g.params[2]
                _g1 = _g.params[3]
                t = haxe_Timer(604800000)
                t.run = self.run
            else:
                pass
            self._timer = t
        result = hx_concurrent_FutureResult.NONE(self)
        try:
            resultValue = None
            _g = self._task
            resultValue1 = _g.index
            if (resultValue1 == 0):
                fn = _g.params[0]
                resultValue = fn()
            elif (resultValue1 == 1):
                fn = _g.params[0]
                fn()
                resultValue = None
            else:
                pass
            result = hx_concurrent_FutureResult.SUCCESS(resultValue,(python_lib_Time.time() * 1000),self)
        except BaseException as _g:
            None
            ex = haxe_Exception.caught(_g).unwrap()
            result = hx_concurrent_FutureResult.FAILURE(hx_concurrent_ConcurrentException(ex),(python_lib_Time.time() * 1000),self)
        _g = self.schedule
        tmp = _g.index
        if (tmp == 0):
            _g1 = _g.params[0]
            self.isStopped = True
        elif (tmp == 1):
            _g1 = _g.params[1]
            intervalMS = _g.params[0]
            self._timer = haxe_Timer.delay(self.run,intervalMS)
        else:
            pass
        self.result = result
        fn = self.onResult
        if (fn is not None):
            try:
                fn(result)
            except BaseException as _g:
                None
                ex = haxe_Exception.caught(_g).unwrap()
                haxe_Log.trace(ex,_hx_AnonObject({'fileName': "hx/concurrent/executor/TimerExecutor.hx", 'lineNumber': 114, 'className': "hx.concurrent.executor._TimerExecutor.TaskFutureImpl", 'methodName': "run"}))
        fn = self._executor.onResult
        if (fn is not None):
            try:
                fn(result)
            except BaseException as _g:
                None
                ex = haxe_Exception.caught(_g).unwrap()
                haxe_Log.trace(ex,_hx_AnonObject({'fileName': "hx/concurrent/executor/TimerExecutor.hx", 'lineNumber': 116, 'className': "hx.concurrent.executor._TimerExecutor.TaskFutureImpl", 'methodName': "run"}))

    def cancel(self):
        t = self._timer
        if (t is not None):
            t.stop()
        super().cancel()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._timer = None
hx_concurrent_executor__TimerExecutor_TaskFutureImpl._hx_class = hx_concurrent_executor__TimerExecutor_TaskFutureImpl
_hx_classes["hx.concurrent.executor._TimerExecutor.TaskFutureImpl"] = hx_concurrent_executor__TimerExecutor_TaskFutureImpl

class hx_concurrent_internal__Either2__Either2(Enum):
    __slots__ = ()
    _hx_class_name = "hx.concurrent.internal._Either2._Either2"
    _hx_constructs = ["a", "b"]

    @staticmethod
    def a(v):
        return hx_concurrent_internal__Either2__Either2("a", 0, (v,))

    @staticmethod
    def b(v):
        return hx_concurrent_internal__Either2__Either2("b", 1, (v,))
hx_concurrent_internal__Either2__Either2._hx_class = hx_concurrent_internal__Either2__Either2
_hx_classes["hx.concurrent.internal._Either2._Either2"] = hx_concurrent_internal__Either2__Either2

class hx_concurrent_internal__Either3__Either3(Enum):
    __slots__ = ()
    _hx_class_name = "hx.concurrent.internal._Either3._Either3"
    _hx_constructs = ["a", "b", "c"]

    @staticmethod
    def a(v):
        return hx_concurrent_internal__Either3__Either3("a", 0, (v,))

    @staticmethod
    def b(v):
        return hx_concurrent_internal__Either3__Either3("b", 1, (v,))

    @staticmethod
    def c(v):
        return hx_concurrent_internal__Either3__Either3("c", 2, (v,))
hx_concurrent_internal__Either3__Either3._hx_class = hx_concurrent_internal__Either3__Either3
_hx_classes["hx.concurrent.internal._Either3._Either3"] = hx_concurrent_internal__Either3__Either3


class hx_concurrent_lock_Acquirable:
    _hx_class_name = "hx.concurrent.lock.Acquirable"
    __slots__ = ()
hx_concurrent_lock_Acquirable._hx_class = hx_concurrent_lock_Acquirable
_hx_classes["hx.concurrent.lock.Acquirable"] = hx_concurrent_lock_Acquirable


class hx_concurrent_lock_RLock:
    _hx_class_name = "hx.concurrent.lock.RLock"
    __slots__ = ("_rlock", "_holder", "_holderEntranceCount")
    _hx_fields = ["_rlock", "_holder", "_holderEntranceCount"]
    _hx_methods = ["execute", "acquire", "release"]
    _hx_interfaces = [hx_concurrent_lock_Acquirable]

    def __init__(self):
        self._holderEntranceCount = 0
        self._holder = None
        self._rlock = python_lib_threading_RLock()

    def execute(self,func,swallowExceptions = None):
        if (swallowExceptions is None):
            swallowExceptions = False
        ex = None
        result = None
        self.acquire()
        try:
            result = func()
        except BaseException as _g:
            None
            e = haxe_Exception.caught(_g).unwrap()
            ex = hx_concurrent_ConcurrentException(e)
        self.release()
        if ((not swallowExceptions) and ((ex is not None))):
            ex.rethrow()
        return result

    def acquire(self):
        self._rlock.acquire()
        self._holder = hx_concurrent_thread_Threads.get_current()
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._holderEntranceCount
        _hx_local_0._holderEntranceCount = (_hx_local_1 + 1)
        _hx_local_1

    def release(self):
        if HxOverrides.eq(self._holder,hx_concurrent_thread_Threads.get_current()):
            _hx_local_0 = self
            _hx_local_1 = _hx_local_0._holderEntranceCount
            _hx_local_0._holderEntranceCount = (_hx_local_1 - 1)
            _hx_local_1
            if (self._holderEntranceCount == 0):
                self._holder = None
        elif ((self._holder is not None) and (not HxOverrides.eq(self._holder,hx_concurrent_thread_Threads.get_current()))):
            raise haxe_Exception.thrown("Lock was aquired by another thread!")
        else:
            raise haxe_Exception.thrown("Lock was not aquired by any thread!")
        self._rlock.release()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._rlock = None
        _hx_o._holder = None
        _hx_o._holderEntranceCount = None
hx_concurrent_lock_RLock._hx_class = hx_concurrent_lock_RLock
_hx_classes["hx.concurrent.lock.RLock"] = hx_concurrent_lock_RLock


class hx_concurrent_thread_ThreadPool(hx_concurrent_ServiceBase):
    _hx_class_name = "hx.concurrent.thread.ThreadPool"
    __slots__ = ("_spawnedThreadCount", "_workingThreadCount", "_workQueue", "threadCount")
    _hx_fields = ["_spawnedThreadCount", "_workingThreadCount", "_workQueue", "threadCount"]
    _hx_methods = ["onStart", "submit"]
    _hx_statics = ["_threadIDs"]
    _hx_interfaces = []
    _hx_super = hx_concurrent_ServiceBase


    def __init__(self,numThreads,autostart = None):
        if (autostart is None):
            autostart = True
        self.threadCount = None
        self._workQueue = hx_concurrent_collection_Queue()
        self._workingThreadCount = hx_concurrent_atomic__AtomicInt_AtomicIntImpl(0)
        self._spawnedThreadCount = hx_concurrent_atomic__AtomicInt_AtomicIntImpl(0)
        if (numThreads < 1):
            raise haxe_Exception.thrown("[numThreads] must be > 0")
        super().__init__()
        self.threadCount = numThreads
        if autostart:
            self.start()

    def onStart(self):
        _gthis = self
        self.set_state(hx_concurrent_ServiceState.RUNNING)
        _g = 0
        _g1 = self.threadCount
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            def _hx_local_1():
                _gthis._spawnedThreadCount.getAndIncrement()
                context = hx_concurrent_thread_ThreadContext(hx_concurrent_thread_ThreadPool._threadIDs.incrementAndGet())
                haxe_Log.trace((((((((("[" + Std.string(_gthis)) + "] Spawned thread ") + HxOverrides.stringOrNull((("null" if ((_gthis._spawnedThreadCount is None)) else Std.string(_gthis._spawnedThreadCount.get_value()))))) + "/") + Std.string(_gthis.threadCount)) + " with ID ") + Std.string(context.id)) + "."),_hx_AnonObject({'fileName': "hx/concurrent/thread/ThreadPool.hx", 'lineNumber': 94, 'className': "hx.concurrent.thread.ThreadPool", 'methodName': "onStart"}))
                while True:
                    task = _gthis._workQueue.pop()
                    if (task is None):
                        if (_gthis.state != hx_concurrent_ServiceState.RUNNING):
                            break
                        Sys.sleep(0.001)
                    else:
                        try:
                            _gthis._workingThreadCount.getAndIncrement()
                            task(context)
                        except BaseException as _g:
                            None
                            ex = haxe_Exception.caught(_g).unwrap()
                            haxe_Log.trace(ex,_hx_AnonObject({'fileName': "hx/concurrent/thread/ThreadPool.hx", 'lineNumber': 107, 'className': "hx.concurrent.thread.ThreadPool", 'methodName': "onStart"}))
                        _gthis._workingThreadCount.getAndIncrement(-1)
                haxe_Log.trace((((("[" + Std.string(_gthis)) + "] Stopped thread with ID ") + Std.string(context.id)) + "."),_hx_AnonObject({'fileName': "hx/concurrent/thread/ThreadPool.hx", 'lineNumber': 113, 'className': "hx.concurrent.thread.ThreadPool", 'methodName': "onStart"}))
                _gthis._spawnedThreadCount.getAndIncrement(-1)
                if (_gthis._spawnedThreadCount.get_value() == 0):
                    def _hx_local_0():
                        return _gthis.set_state(hx_concurrent_ServiceState.STOPPED)
                    _gthis._stateLock.execute(_hx_local_0)
            t = python_lib_threading_Thread(**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'target': _hx_local_1})))
            t.daemon = True
            t.start()

    def submit(self,task):
        _gthis = self
        if (task is None):
            raise haxe_Exception.thrown("[task] must not be null")
        def _hx_local_0():
            if (_gthis.state != hx_concurrent_ServiceState.RUNNING):
                raise haxe_Exception.thrown((("ThreadPool is not in requried state [RUNNING] but [" + Std.string(_gthis.state)) + "]"))
            _gthis._workQueue.push(task)
        self._stateLock.execute(_hx_local_0)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._spawnedThreadCount = None
        _hx_o._workingThreadCount = None
        _hx_o._workQueue = None
        _hx_o.threadCount = None
hx_concurrent_thread_ThreadPool._hx_class = hx_concurrent_thread_ThreadPool
_hx_classes["hx.concurrent.thread.ThreadPool"] = hx_concurrent_thread_ThreadPool


class hx_concurrent_thread_ThreadContext:
    _hx_class_name = "hx.concurrent.thread.ThreadContext"
    __slots__ = ("id",)
    _hx_fields = ["id"]

    def __init__(self,id):
        self.id = id

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.id = None
hx_concurrent_thread_ThreadContext._hx_class = hx_concurrent_thread_ThreadContext
_hx_classes["hx.concurrent.thread.ThreadContext"] = hx_concurrent_thread_ThreadContext


class hx_concurrent_thread_Threads:
    _hx_class_name = "hx.concurrent.thread.Threads"
    __slots__ = ()
    _hx_statics = ["get_current", "get_isSupported", "await"]
    current = None
    isSupported = None

    @staticmethod
    def get_current():
        return sys_thread__Thread_HxThread.current()

    @staticmethod
    def get_isSupported():
        try:
            from threading import Thread
            return True
        except BaseException as _g:
            None
            return False

    @staticmethod
    def _hx_await(condition,timeoutMS,waitLoopSleepMS = None):
        if (waitLoopSleepMS is None):
            waitLoopSleepMS = 10
        if (timeoutMS < -1):
            raise haxe_Exception.thrown("[timeoutMS] must be >= -1")
        if (timeoutMS == 0):
            return condition()
        waitLoopSleepSecs = (waitLoopSleepMS / 1000.0)
        startAt = (python_lib_Time.time() * 1000)
        while (not condition()):
            if (timeoutMS > 0):
                elapsedMS = ((python_lib_Time.time() * 1000) - startAt)
                if (elapsedMS >= timeoutMS):
                    return False
            Sys.sleep(waitLoopSleepSecs)
        return True
hx_concurrent_thread_Threads._hx_class = hx_concurrent_thread_Threads
_hx_classes["hx.concurrent.thread.Threads"] = hx_concurrent_thread_Threads


class pako_Inflate:
    _hx_class_name = "pako.Inflate"
    __slots__ = ("options", "err", "msg", "ended", "chunks", "strm", "header", "result", "onData", "onEnd")
    _hx_fields = ["options", "err", "msg", "ended", "chunks", "strm", "header", "result", "onData", "onEnd"]
    _hx_methods = ["push", "_onData", "_onEnd"]
    _hx_statics = ["DEFAULT_OPTIONS"]

    def __init__(self,options = None):
        self.onEnd = None
        self.onData = None
        self.result = None
        self.header = pako_zlib_GZHeader()
        self.strm = pako_zlib_ZStream()
        self.chunks = []
        self.ended = False
        self.msg = ""
        self.err = 0
        self.options = None
        self.options = _hx_AnonObject({})
        Reflect.setField(self.options,"chunkSize",(Reflect.field(options,"chunkSize") if (((options is not None) and ((Reflect.field(options,"chunkSize") is not None)))) else Reflect.field(pako_Inflate.DEFAULT_OPTIONS,"chunkSize")))
        Reflect.setField(self.options,"windowBits",(Reflect.field(options,"windowBits") if (((options is not None) and ((Reflect.field(options,"windowBits") is not None)))) else Reflect.field(pako_Inflate.DEFAULT_OPTIONS,"windowBits")))
        Reflect.setField(self.options,"raw",(Reflect.field(options,"raw") if (((options is not None) and ((Reflect.field(options,"raw") is not None)))) else Reflect.field(pako_Inflate.DEFAULT_OPTIONS,"raw")))
        Reflect.setField(self.options,"dictionary",(Reflect.field(options,"dictionary") if (((options is not None) and ((Reflect.field(options,"dictionary") is not None)))) else Reflect.field(pako_Inflate.DEFAULT_OPTIONS,"dictionary")))
        if ((Reflect.field(self.options,"raw") and ((Reflect.field(self.options,"windowBits") >= 0))) and ((Reflect.field(self.options,"windowBits") < 16))):
            Reflect.setField(self.options,"windowBits",-Reflect.field(self.options,"windowBits"))
            if (Reflect.field(self.options,"windowBits") == 0):
                Reflect.setField(self.options,"windowBits",-15)
        if (((Reflect.field(self.options,"windowBits") >= 0) and ((Reflect.field(self.options,"windowBits") < 16))) and (((options is None) or ((Reflect.field(options,"windowBits") is None))))):
            _hx_local_0 = self.options
            Reflect.setField(_hx_local_0,"windowBits",(Reflect.field(_hx_local_0,"windowBits") + 32))
        if ((Reflect.field(self.options,"windowBits") > 15) and ((Reflect.field(self.options,"windowBits") < 48))):
            if (((Reflect.field(self.options,"windowBits") & 15)) == 0):
                _hx_local_1 = self.options
                Reflect.setField(_hx_local_1,"windowBits",(Reflect.field(_hx_local_1,"windowBits") | 15))
        self.onData = self._onData
        self.onEnd = self._onEnd
        self.strm.avail_out = 0
        status = pako_zlib_Inflate.inflateInit2(self.strm,Reflect.field(self.options,"windowBits"))
        if (status != 0):
            raise haxe_Exception.thrown(pako_zlib_Messages.get(status))
        pako_zlib_Inflate.inflateGetHeader(self.strm,self.header)

    def push(self,data,mode = None):
        if (mode is None):
            mode = False
        strm = self.strm
        chunkSize = Reflect.field(self.options,"chunkSize")
        dictionary = Reflect.field(self.options,"dictionary")
        status = None
        _mode = None
        next_out_utf8 = None
        tail = None
        utf8str = None
        allowBufError = False
        if self.ended:
            return False
        if Std.isOfType(mode,Int):
            _mode = mode
        elif Std.isOfType(mode,Bool):
            _mode = (4 if mode else 0)
        else:
            raise haxe_Exception.thrown("Invalid mode.")
        strm.input = data
        strm.next_in = 0
        strm.avail_in = strm.input.byteLength
        while True:
            if (strm.avail_out == 0):
                this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(chunkSize),0,chunkSize)
                this2 = this1
                strm.output = this2
                strm.next_out = 0
                strm.avail_out = chunkSize
            status = pako_zlib_Inflate.inflate(strm,0)
            if ((status == 2) and ((dictionary is not None))):
                status = pako_zlib_Inflate.inflateSetDictionary(self.strm,dictionary)
            if ((status == -5) and allowBufError):
                status = 0
                allowBufError = False
            if ((status != 1) and ((status != 0))):
                self.onEnd(status)
                self.ended = True
                return False
            if (strm.next_out != 0):
                if (((strm.avail_out == 0) or ((status == 1))) or (((strm.avail_in == 0) and (((_mode == 4) or ((_mode == 2))))))):
                    tmp = self.onData
                    buf = strm.output
                    size = strm.next_out
                    if (buf.byteLength != size):
                        buf = haxe_io__UInt8Array_UInt8Array_Impl_.fromData(buf.subarray(0,size))
                    tmp(buf)
            if ((strm.avail_in == 0) and ((strm.avail_out == 0))):
                allowBufError = True
            if (not (((((strm.avail_in > 0) or ((strm.avail_out == 0)))) and ((status != 1))))):
                break
        if (status == 1):
            _mode = 4
        if (_mode == 4):
            status = pako_zlib_Inflate.inflateEnd(self.strm)
            self.onEnd(status)
            self.ended = True
            return (status == 0)
        if (_mode == 2):
            self.onEnd(0)
            strm.avail_out = 0
            return True
        return True

    def _onData(self,chunk):
        _this = self.chunks
        _this.append(chunk)

    def _onEnd(self,status):
        if (status == 0):
            self.result = pako_utils_Common.flattenChunks(self.chunks)
        self.chunks = []
        self.err = status
        self.msg = self.strm.msg

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.options = None
        _hx_o.err = None
        _hx_o.msg = None
        _hx_o.ended = None
        _hx_o.chunks = None
        _hx_o.strm = None
        _hx_o.header = None
        _hx_o.result = None
        _hx_o.onData = None
        _hx_o.onEnd = None
pako_Inflate._hx_class = pako_Inflate
_hx_classes["pako.Inflate"] = pako_Inflate


class pako_utils_Common:
    _hx_class_name = "pako.utils.Common"
    __slots__ = ()
    _hx_statics = ["flattenChunks"]

    @staticmethod
    def flattenChunks(chunks):
        i = None
        chunk = None
        _hx_len = 0
        l = len(chunks)
        _g = 0
        _g1 = l
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            _hx_len = (_hx_len + (chunks[i] if i >= 0 and i < len(chunks) else None).byteLength)
        this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(_hx_len),0,_hx_len)
        this2 = this1
        result = this2
        pos = 0
        _g = 0
        _g1 = l
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            chunk = (chunks[i] if i >= 0 and i < len(chunks) else None)
            result.bytes.blit(pos,chunk.bytes,0,chunk.byteLength)
            pos = (pos + chunk.byteLength)
        return result
pako_utils_Common._hx_class = pako_utils_Common
_hx_classes["pako.utils.Common"] = pako_utils_Common


class pako_zlib_Adler32:
    _hx_class_name = "pako.zlib.Adler32"
    __slots__ = ()
    _hx_statics = ["adler32"]

    @staticmethod
    def adler32(adler,buf,_hx_len,pos):
        s1 = ((adler & 65535) | 0)
        s2 = ((HxOverrides.rshift(adler, 16) & 65535) | 0)
        n = 0
        while (_hx_len != 0):
            n = (2000 if ((_hx_len > 2000)) else _hx_len)
            _hx_len = (_hx_len - n)
            while True:
                index = pos
                pos = (pos + 1)
                s1 = ((s1 + buf.bytes.b[(index + buf.byteOffset)]) | 0)
                s2 = ((s2 + s1) | 0)
                n = (n - 1)
                tmp = n
                if (not ((tmp != 0))):
                    break
            s1 = HxOverrides.mod(s1, 65521)
            s2 = HxOverrides.mod(s2, 65521)
        return ((s1 | ((s2 << 16))) | 0)
pako_zlib_Adler32._hx_class = pako_zlib_Adler32
_hx_classes["pako.zlib.Adler32"] = pako_zlib_Adler32


class pako_zlib_CRC32:
    _hx_class_name = "pako.zlib.CRC32"
    __slots__ = ()
    _hx_statics = ["makeTable", "crcTable", "crc32"]

    @staticmethod
    def makeTable():
        c = None
        this1 = [None]*256
        table = this1
        _g = 0
        while (_g < 256):
            n = _g
            _g = (_g + 1)
            c = n
            if (((c & 1)) == 1):
                c = (-306674912 ^ (HxOverrides.rshift(c, 1)))
            else:
                c = HxOverrides.rshift(c, 1)
            if (((c & 1)) == 1):
                c = (-306674912 ^ (HxOverrides.rshift(c, 1)))
            else:
                c = HxOverrides.rshift(c, 1)
            if (((c & 1)) == 1):
                c = (-306674912 ^ (HxOverrides.rshift(c, 1)))
            else:
                c = HxOverrides.rshift(c, 1)
            if (((c & 1)) == 1):
                c = (-306674912 ^ (HxOverrides.rshift(c, 1)))
            else:
                c = HxOverrides.rshift(c, 1)
            if (((c & 1)) == 1):
                c = (-306674912 ^ (HxOverrides.rshift(c, 1)))
            else:
                c = HxOverrides.rshift(c, 1)
            if (((c & 1)) == 1):
                c = (-306674912 ^ (HxOverrides.rshift(c, 1)))
            else:
                c = HxOverrides.rshift(c, 1)
            if (((c & 1)) == 1):
                c = (-306674912 ^ (HxOverrides.rshift(c, 1)))
            else:
                c = HxOverrides.rshift(c, 1)
            if (((c & 1)) == 1):
                c = (-306674912 ^ (HxOverrides.rshift(c, 1)))
            else:
                c = HxOverrides.rshift(c, 1)
            table[n] = c
        return table

    @staticmethod
    def crc32(crc,buf,_hx_len,pos):
        t = pako_zlib_CRC32.crcTable
        end = (pos + _hx_len)
        crc = (crc ^ -1)
        _g = pos
        _g1 = end
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            crc = (HxOverrides.rshift(crc, 8) ^ t[(((crc ^ buf.bytes.b[(i + buf.byteOffset)])) & 255)])
        return (crc ^ -1)
pako_zlib_CRC32._hx_class = pako_zlib_CRC32
_hx_classes["pako.zlib.CRC32"] = pako_zlib_CRC32


class pako_zlib_GZHeader:
    _hx_class_name = "pako.zlib.GZHeader"
    __slots__ = ("text", "time", "xflags", "os", "extra", "extra_len", "name", "comment", "hcrc", "done")
    _hx_fields = ["text", "time", "xflags", "os", "extra", "extra_len", "name", "comment", "hcrc", "done"]

    def __init__(self):
        self.done = False
        self.hcrc = 0
        self.comment = ""
        self.name = ""
        self.extra_len = 0
        self.extra = None
        self.os = 0
        self.xflags = 0
        self.time = 0
        self.text = False

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.text = None
        _hx_o.time = None
        _hx_o.xflags = None
        _hx_o.os = None
        _hx_o.extra = None
        _hx_o.extra_len = None
        _hx_o.name = None
        _hx_o.comment = None
        _hx_o.hcrc = None
        _hx_o.done = None
pako_zlib_GZHeader._hx_class = pako_zlib_GZHeader
_hx_classes["pako.zlib.GZHeader"] = pako_zlib_GZHeader


class pako_zlib_InfFast:
    _hx_class_name = "pako.zlib.InfFast"
    __slots__ = ()
    _hx_statics = ["inflate_fast"]

    @staticmethod
    def inflate_fast(strm,start):
        here = None
        op = None
        _hx_len = None
        dist = None
        _hx_from = None
        from_source = None
        state = strm.inflateState
        _in = strm.next_in
        input = strm.input
        last = (_in + ((strm.avail_in - 5)))
        _out = strm.next_out
        output = strm.output
        beg = (_out - ((start - strm.avail_out)))
        end = (_out + ((strm.avail_out - 257)))
        dmax = state.dmax
        wsize = state.wsize
        whave = state.whave
        wnext = state.wnext
        s_window = state.window
        hold = state.hold
        bits = state.bits
        lcode = state.lencode
        dcode = state.distcode
        lmask = (((1 << state.lenbits)) - 1)
        dmask = (((1 << state.distbits)) - 1)
        exit_top = False
        while (not exit_top):
            exit_top = False
            if (bits < 15):
                index = _in
                _in = (_in + 1)
                hold = (hold + ((input.bytes.b[(index + input.byteOffset)] << bits)))
                bits = (bits + 8)
                index1 = _in
                _in = (_in + 1)
                hold = (hold + ((input.bytes.b[(index1 + input.byteOffset)] << bits)))
                bits = (bits + 8)
            _this = lcode.bytes
            pos = (((((hold & lmask)) << 2)) + lcode.byteOffset)
            v = (((_this.b[pos] | ((_this.b[(pos + 1)] << 8))) | ((_this.b[(pos + 2)] << 16))) | ((_this.b[(pos + 3)] << 24)))
            here = ((v | -2147483648) if ((((v & -2147483648)) != 0)) else v)
            while True:
                op = HxOverrides.rshift(here, 24)
                hold = HxOverrides.rshift(hold, op)
                bits = (bits - op)
                op = (HxOverrides.rshift(here, 16) & 255)
                if (op == 0):
                    index2 = _out
                    _out = (_out + 1)
                    value = (here & 65535)
                    if ((index2 >= 0) and ((index2 < output.byteLength))):
                        output.bytes.b[(index2 + output.byteOffset)] = (value & 255)
                elif (((op & 16)) != 0):
                    _hx_len = (here & 65535)
                    op = (op & 15)
                    if (op != 0):
                        if (bits < op):
                            index3 = _in
                            _in = (_in + 1)
                            hold = (hold + ((input.bytes.b[(index3 + input.byteOffset)] << bits)))
                            bits = (bits + 8)
                        _hx_len = (_hx_len + ((hold & ((((1 << op)) - 1)))))
                        hold = HxOverrides.rshift(hold, op)
                        bits = (bits - op)
                    if (bits < 15):
                        index4 = _in
                        _in = (_in + 1)
                        hold = (hold + ((input.bytes.b[(index4 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                        index5 = _in
                        _in = (_in + 1)
                        hold = (hold + ((input.bytes.b[(index5 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    _this1 = dcode.bytes
                    pos1 = (((((hold & dmask)) << 2)) + dcode.byteOffset)
                    v1 = (((_this1.b[pos1] | ((_this1.b[(pos1 + 1)] << 8))) | ((_this1.b[(pos1 + 2)] << 16))) | ((_this1.b[(pos1 + 3)] << 24)))
                    here = ((v1 | -2147483648) if ((((v1 & -2147483648)) != 0)) else v1)
                    while True:
                        op = HxOverrides.rshift(here, 24)
                        hold = HxOverrides.rshift(hold, op)
                        bits = (bits - op)
                        op = (HxOverrides.rshift(here, 16) & 255)
                        if (((op & 16)) != 0):
                            dist = (here & 65535)
                            op = (op & 15)
                            if (bits < op):
                                index6 = _in
                                _in = (_in + 1)
                                hold = (hold + ((input.bytes.b[(index6 + input.byteOffset)] << bits)))
                                bits = (bits + 8)
                                if (bits < op):
                                    index7 = _in
                                    _in = (_in + 1)
                                    hold = (hold + ((input.bytes.b[(index7 + input.byteOffset)] << bits)))
                                    bits = (bits + 8)
                            dist = (dist + ((hold & ((((1 << op)) - 1)))))
                            if (dist > dmax):
                                strm.msg = "invalid distance too far back"
                                state.mode = 30
                                exit_top = True
                                break
                            hold = HxOverrides.rshift(hold, op)
                            bits = (bits - op)
                            op = (_out - beg)
                            if (dist > op):
                                op = (dist - op)
                                if (op > whave):
                                    if (state.sane != 0):
                                        strm.msg = "invalid distance too far back"
                                        state.mode = 30
                                        exit_top = True
                                        break
                                _hx_from = 0
                                from_source = s_window
                                if (wnext == 0):
                                    _hx_from = (_hx_from + ((wsize - op)))
                                    if (op < _hx_len):
                                        _hx_len = (_hx_len - op)
                                        while True:
                                            index8 = _out
                                            _out = (_out + 1)
                                            index9 = _hx_from
                                            _hx_from = (_hx_from + 1)
                                            value1 = s_window.bytes.b[(index9 + s_window.byteOffset)]
                                            if ((index8 >= 0) and ((index8 < output.byteLength))):
                                                output.bytes.b[(index8 + output.byteOffset)] = (value1 & 255)
                                            op = (op - 1)
                                            tmp = op
                                            if (not ((tmp != 0))):
                                                break
                                        _hx_from = (_out - dist)
                                        from_source = output
                                elif (wnext < op):
                                    _hx_from = (_hx_from + (((wsize + wnext) - op)))
                                    op = (op - wnext)
                                    if (op < _hx_len):
                                        _hx_len = (_hx_len - op)
                                        while True:
                                            index10 = _out
                                            _out = (_out + 1)
                                            index11 = _hx_from
                                            _hx_from = (_hx_from + 1)
                                            value2 = s_window.bytes.b[(index11 + s_window.byteOffset)]
                                            if ((index10 >= 0) and ((index10 < output.byteLength))):
                                                output.bytes.b[(index10 + output.byteOffset)] = (value2 & 255)
                                            op = (op - 1)
                                            tmp1 = op
                                            if (not ((tmp1 != 0))):
                                                break
                                        _hx_from = 0
                                        if (wnext < _hx_len):
                                            op = wnext
                                            _hx_len = (_hx_len - op)
                                            while True:
                                                index12 = _out
                                                _out = (_out + 1)
                                                index13 = _hx_from
                                                _hx_from = (_hx_from + 1)
                                                value3 = s_window.bytes.b[(index13 + s_window.byteOffset)]
                                                if ((index12 >= 0) and ((index12 < output.byteLength))):
                                                    output.bytes.b[(index12 + output.byteOffset)] = (value3 & 255)
                                                op = (op - 1)
                                                tmp2 = op
                                                if (not ((tmp2 != 0))):
                                                    break
                                            _hx_from = (_out - dist)
                                            from_source = output
                                else:
                                    _hx_from = (_hx_from + ((wnext - op)))
                                    if (op < _hx_len):
                                        _hx_len = (_hx_len - op)
                                        while True:
                                            index14 = _out
                                            _out = (_out + 1)
                                            index15 = _hx_from
                                            _hx_from = (_hx_from + 1)
                                            value4 = s_window.bytes.b[(index15 + s_window.byteOffset)]
                                            if ((index14 >= 0) and ((index14 < output.byteLength))):
                                                output.bytes.b[(index14 + output.byteOffset)] = (value4 & 255)
                                            op = (op - 1)
                                            tmp3 = op
                                            if (not ((tmp3 != 0))):
                                                break
                                        _hx_from = (_out - dist)
                                        from_source = output
                                while (_hx_len > 2):
                                    index16 = _out
                                    _out = (_out + 1)
                                    index17 = _hx_from
                                    _hx_from = (_hx_from + 1)
                                    value5 = from_source.bytes.b[(index17 + from_source.byteOffset)]
                                    if ((index16 >= 0) and ((index16 < output.byteLength))):
                                        output.bytes.b[(index16 + output.byteOffset)] = (value5 & 255)
                                    index18 = _out
                                    _out = (_out + 1)
                                    index19 = _hx_from
                                    _hx_from = (_hx_from + 1)
                                    value6 = from_source.bytes.b[(index19 + from_source.byteOffset)]
                                    if ((index18 >= 0) and ((index18 < output.byteLength))):
                                        output.bytes.b[(index18 + output.byteOffset)] = (value6 & 255)
                                    index20 = _out
                                    _out = (_out + 1)
                                    index21 = _hx_from
                                    _hx_from = (_hx_from + 1)
                                    value7 = from_source.bytes.b[(index21 + from_source.byteOffset)]
                                    if ((index20 >= 0) and ((index20 < output.byteLength))):
                                        output.bytes.b[(index20 + output.byteOffset)] = (value7 & 255)
                                    _hx_len = (_hx_len - 3)
                                if (_hx_len != 0):
                                    index22 = _out
                                    _out = (_out + 1)
                                    index23 = _hx_from
                                    _hx_from = (_hx_from + 1)
                                    value8 = from_source.bytes.b[(index23 + from_source.byteOffset)]
                                    if ((index22 >= 0) and ((index22 < output.byteLength))):
                                        output.bytes.b[(index22 + output.byteOffset)] = (value8 & 255)
                                    if (_hx_len > 1):
                                        index24 = _out
                                        _out = (_out + 1)
                                        index25 = _hx_from
                                        _hx_from = (_hx_from + 1)
                                        value9 = from_source.bytes.b[(index25 + from_source.byteOffset)]
                                        if ((index24 >= 0) and ((index24 < output.byteLength))):
                                            output.bytes.b[(index24 + output.byteOffset)] = (value9 & 255)
                            else:
                                _hx_from = (_out - dist)
                                while True:
                                    index26 = _out
                                    _out = (_out + 1)
                                    index27 = _hx_from
                                    _hx_from = (_hx_from + 1)
                                    value10 = output.bytes.b[(index27 + output.byteOffset)]
                                    if ((index26 >= 0) and ((index26 < output.byteLength))):
                                        output.bytes.b[(index26 + output.byteOffset)] = (value10 & 255)
                                    index28 = _out
                                    _out = (_out + 1)
                                    index29 = _hx_from
                                    _hx_from = (_hx_from + 1)
                                    value11 = output.bytes.b[(index29 + output.byteOffset)]
                                    if ((index28 >= 0) and ((index28 < output.byteLength))):
                                        output.bytes.b[(index28 + output.byteOffset)] = (value11 & 255)
                                    index30 = _out
                                    _out = (_out + 1)
                                    index31 = _hx_from
                                    _hx_from = (_hx_from + 1)
                                    value12 = output.bytes.b[(index31 + output.byteOffset)]
                                    if ((index30 >= 0) and ((index30 < output.byteLength))):
                                        output.bytes.b[(index30 + output.byteOffset)] = (value12 & 255)
                                    _hx_len = (_hx_len - 3)
                                    if (not ((_hx_len > 2))):
                                        break
                                if (_hx_len != 0):
                                    index32 = _out
                                    _out = (_out + 1)
                                    index33 = _hx_from
                                    _hx_from = (_hx_from + 1)
                                    value13 = output.bytes.b[(index33 + output.byteOffset)]
                                    if ((index32 >= 0) and ((index32 < output.byteLength))):
                                        output.bytes.b[(index32 + output.byteOffset)] = (value13 & 255)
                                    if (_hx_len > 1):
                                        index34 = _out
                                        _out = (_out + 1)
                                        index35 = _hx_from
                                        _hx_from = (_hx_from + 1)
                                        value14 = output.bytes.b[(index35 + output.byteOffset)]
                                        if ((index34 >= 0) and ((index34 < output.byteLength))):
                                            output.bytes.b[(index34 + output.byteOffset)] = (value14 & 255)
                        elif (((op & 64)) == 0):
                            _this2 = dcode.bytes
                            pos2 = ((((((here & 65535)) + ((hold & ((((1 << op)) - 1))))) << 2)) + dcode.byteOffset)
                            v2 = (((_this2.b[pos2] | ((_this2.b[(pos2 + 1)] << 8))) | ((_this2.b[(pos2 + 2)] << 16))) | ((_this2.b[(pos2 + 3)] << 24)))
                            here = ((v2 | -2147483648) if ((((v2 & -2147483648)) != 0)) else v2)
                            continue
                        else:
                            strm.msg = "invalid distance code"
                            state.mode = 30
                            exit_top = True
                            break
                        break
                    if exit_top:
                        break
                elif (((op & 64)) == 0):
                    _this3 = lcode.bytes
                    pos3 = ((((((here & 65535)) + ((hold & ((((1 << op)) - 1))))) << 2)) + lcode.byteOffset)
                    v3 = (((_this3.b[pos3] | ((_this3.b[(pos3 + 1)] << 8))) | ((_this3.b[(pos3 + 2)] << 16))) | ((_this3.b[(pos3 + 3)] << 24)))
                    here = ((v3 | -2147483648) if ((((v3 & -2147483648)) != 0)) else v3)
                    continue
                elif (((op & 32)) != 0):
                    state.mode = 12
                    exit_top = True
                    break
                else:
                    strm.msg = "invalid literal/length code"
                    state.mode = 30
                    exit_top = True
                    break
                break
            if exit_top:
                if (not (((_in < last) and ((_out < end))))):
                    break
                else:
                    continue
            if (not (((_in < last) and ((_out < end))))):
                break
        _hx_len = (bits >> 3)
        _in = (_in - _hx_len)
        bits = (bits - ((_hx_len << 3)))
        hold = (hold & ((((1 << bits)) - 1)))
        strm.next_in = _in
        strm.next_out = _out
        strm.avail_in = ((5 + ((last - _in))) if ((_in < last)) else (5 - ((_in - last))))
        strm.avail_out = ((257 + ((end - _out))) if ((_out < end)) else (257 - ((_out - end))))
        state.hold = hold
        state.bits = bits
pako_zlib_InfFast._hx_class = pako_zlib_InfFast
_hx_classes["pako.zlib.InfFast"] = pako_zlib_InfFast


class pako_zlib_InfTrees:
    _hx_class_name = "pako.zlib.InfTrees"
    __slots__ = ()
    _hx_statics = ["MAXBITS", "ENOUGH_LENS", "ENOUGH_DISTS", "CODES", "LENS", "DISTS", "lbase", "lext", "dbase", "dext", "inflate_table"]

    @staticmethod
    def inflate_table(_hx_type,lens,lens_index,codes,table,table_index,work,opts):
        bits = 0
        _hx_len = 0
        sym = 0
        _hx_min = 0
        _hx_max = 0
        root = 0
        curr = 0
        drop = 0
        left = 0
        used = 0
        huff = 0
        incr = 0
        fill = 0
        low = 0
        mask = 0
        next = 0
        base = None
        base_index = 0
        end = 0
        size = (((pako_zlib_InfTrees.MAXBITS + 1)) * 2)
        this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(size),0,size)
        this2 = this1
        count = this2
        size = (((pako_zlib_InfTrees.MAXBITS + 1)) * 2)
        this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(size),0,size)
        this2 = this1
        offs = this2
        extra = None
        extra_index = 0
        bits = opts.bits
        here_bits = None
        here_op = None
        here_val = None
        _hx_len = 0
        while (_hx_len <= pako_zlib_InfTrees.MAXBITS):
            if ((_hx_len >= 0) and ((_hx_len < ((count.byteLength >> 1))))):
                _this = count.bytes
                pos = (((_hx_len << 1)) + count.byteOffset)
                _this.b[pos] = 0
                _this.b[(pos + 1)] = 0
            _hx_len = (_hx_len + 1)
        sym = 0
        while (sym < codes):
            _this = lens.bytes
            pos = ((((lens_index + sym) << 1)) + lens.byteOffset)
            _g = (_this.b[pos] | ((_this.b[(pos + 1)] << 8)))
            _g1 = count
            _this1 = _g1.bytes
            pos1 = (((_g << 1)) + _g1.byteOffset)
            value = (((_this1.b[pos1] | ((_this1.b[(pos1 + 1)] << 8)))) + 1)
            if ((_g >= 0) and ((_g < ((_g1.byteLength >> 1))))):
                _this2 = _g1.bytes
                pos2 = (((_g << 1)) + _g1.byteOffset)
                _this2.b[pos2] = (value & 255)
                _this2.b[(pos2 + 1)] = ((value >> 8) & 255)
            sym = (sym + 1)
        root = bits
        _hx_max = pako_zlib_InfTrees.MAXBITS
        while (_hx_max >= 1):
            _this = count.bytes
            pos = (((_hx_max << 1)) + count.byteOffset)
            if (((_this.b[pos] | ((_this.b[(pos + 1)] << 8)))) != 0):
                break
            _hx_max = (_hx_max - 1)
        if (root > _hx_max):
            root = _hx_max
        if (_hx_max == 0):
            index = table_index
            table_index = (table_index + 1)
            if ((index >= 0) and ((index < ((table.byteLength >> 2))))):
                _this = table.bytes
                pos = (((index << 2)) + table.byteOffset)
                _this.b[pos] = 0
                _this.b[(pos + 1)] = 0
                _this.b[(pos + 2)] = 64
                _this.b[(pos + 3)] = 1
            index = table_index
            table_index = (table_index + 1)
            if ((index >= 0) and ((index < ((table.byteLength >> 2))))):
                _this = table.bytes
                pos = (((index << 2)) + table.byteOffset)
                _this.b[pos] = 0
                _this.b[(pos + 1)] = 0
                _this.b[(pos + 2)] = 64
                _this.b[(pos + 3)] = 1
            opts.bits = 1
            return 0
        _hx_min = 1
        while (_hx_min < _hx_max):
            _this = count.bytes
            pos = (((_hx_min << 1)) + count.byteOffset)
            if (((_this.b[pos] | ((_this.b[(pos + 1)] << 8)))) != 0):
                break
            _hx_min = (_hx_min + 1)
        if (root < _hx_min):
            root = _hx_min
        left = 1
        _hx_len = 1
        while (_hx_len <= pako_zlib_InfTrees.MAXBITS):
            left = (left << 1)
            _this = count.bytes
            pos = (((_hx_len << 1)) + count.byteOffset)
            left = (left - ((_this.b[pos] | ((_this.b[(pos + 1)] << 8)))))
            if (left < 0):
                return -1
            _hx_len = (_hx_len + 1)
        if ((left > 0) and (((_hx_type == pako_zlib_InfTrees.CODES) or ((_hx_max != 1))))):
            return -1
        if (1 < ((offs.byteLength >> 1))):
            _this = offs.bytes
            pos = (2 + offs.byteOffset)
            _this.b[pos] = 0
            _this.b[(pos + 1)] = 0
        _hx_len = 1
        while (_hx_len < pako_zlib_InfTrees.MAXBITS):
            index = (_hx_len + 1)
            _this = offs.bytes
            pos = (((_hx_len << 1)) + offs.byteOffset)
            value = (_this.b[pos] | ((_this.b[(pos + 1)] << 8)))
            _this1 = count.bytes
            pos1 = (((_hx_len << 1)) + count.byteOffset)
            value1 = (value + ((_this1.b[pos1] | ((_this1.b[(pos1 + 1)] << 8)))))
            if ((index >= 0) and ((index < ((offs.byteLength >> 1))))):
                _this2 = offs.bytes
                pos2 = (((index << 1)) + offs.byteOffset)
                _this2.b[pos2] = (value1 & 255)
                _this2.b[(pos2 + 1)] = ((value1 >> 8) & 255)
            _hx_len = (_hx_len + 1)
        sym = 0
        while (sym < codes):
            _this = lens.bytes
            pos = ((((lens_index + sym) << 1)) + lens.byteOffset)
            if (((_this.b[pos] | ((_this.b[(pos + 1)] << 8)))) != 0):
                _this1 = lens.bytes
                pos1 = ((((lens_index + sym) << 1)) + lens.byteOffset)
                index = (_this1.b[pos1] | ((_this1.b[(pos1 + 1)] << 8)))
                _this2 = offs.bytes
                pos2 = (((index << 1)) + offs.byteOffset)
                index1 = (_this2.b[pos2] | ((_this2.b[(pos2 + 1)] << 8)))
                if ((index1 >= 0) and ((index1 < ((work.byteLength >> 1))))):
                    _this3 = work.bytes
                    pos3 = (((index1 << 1)) + work.byteOffset)
                    _this3.b[pos3] = (sym & 255)
                    _this3.b[(pos3 + 1)] = ((sym >> 8) & 255)
                _this4 = lens.bytes
                pos4 = ((((lens_index + sym) << 1)) + lens.byteOffset)
                _g = (_this4.b[pos4] | ((_this4.b[(pos4 + 1)] << 8)))
                _g1 = offs
                _this5 = _g1.bytes
                pos5 = (((_g << 1)) + _g1.byteOffset)
                value = (((_this5.b[pos5] | ((_this5.b[(pos5 + 1)] << 8)))) + 1)
                if ((_g >= 0) and ((_g < ((_g1.byteLength >> 1))))):
                    _this6 = _g1.bytes
                    pos6 = (((_g << 1)) + _g1.byteOffset)
                    _this6.b[pos6] = (value & 255)
                    _this6.b[(pos6 + 1)] = ((value >> 8) & 255)
            sym = (sym + 1)
        if (_hx_type == pako_zlib_InfTrees.CODES):
            extra = work
            base = extra
            end = 19
        elif (_hx_type == pako_zlib_InfTrees.LENS):
            base = pako_zlib_InfTrees.lbase
            base_index = (base_index - 257)
            extra = pako_zlib_InfTrees.lext
            extra_index = (extra_index - 257)
            end = 256
        else:
            base = pako_zlib_InfTrees.dbase
            extra = pako_zlib_InfTrees.dext
            end = -1
        huff = 0
        sym = 0
        _hx_len = _hx_min
        next = table_index
        curr = root
        drop = 0
        low = -1
        used = (1 << root)
        mask = (used - 1)
        if (((_hx_type == pako_zlib_InfTrees.LENS) and ((used > pako_zlib_InfTrees.ENOUGH_LENS))) or (((_hx_type == pako_zlib_InfTrees.DISTS) and ((used > pako_zlib_InfTrees.ENOUGH_DISTS))))):
            return 1
        i = 0
        while True:
            i = (i + 1)
            here_bits = (_hx_len - drop)
            _this = work.bytes
            pos = (((sym << 1)) + work.byteOffset)
            if (((_this.b[pos] | ((_this.b[(pos + 1)] << 8)))) < end):
                here_op = 0
                _this1 = work.bytes
                pos1 = (((sym << 1)) + work.byteOffset)
                here_val = (_this1.b[pos1] | ((_this1.b[(pos1 + 1)] << 8)))
            else:
                _this2 = work.bytes
                pos2 = (((sym << 1)) + work.byteOffset)
                if (((_this2.b[pos2] | ((_this2.b[(pos2 + 1)] << 8)))) > end):
                    _this3 = work.bytes
                    pos3 = (((sym << 1)) + work.byteOffset)
                    index = (extra_index + ((_this3.b[pos3] | ((_this3.b[(pos3 + 1)] << 8)))))
                    _this4 = extra.bytes
                    pos4 = (((index << 1)) + extra.byteOffset)
                    here_op = (_this4.b[pos4] | ((_this4.b[(pos4 + 1)] << 8)))
                    _this5 = work.bytes
                    pos5 = (((sym << 1)) + work.byteOffset)
                    index1 = (base_index + ((_this5.b[pos5] | ((_this5.b[(pos5 + 1)] << 8)))))
                    _this6 = base.bytes
                    pos6 = (((index1 << 1)) + base.byteOffset)
                    here_val = (_this6.b[pos6] | ((_this6.b[(pos6 + 1)] << 8)))
                else:
                    here_op = 96
                    here_val = 0
            incr = (1 << ((_hx_len - drop)))
            fill = (1 << curr)
            _hx_min = fill
            while True:
                fill = (fill - incr)
                index2 = ((next + ((huff >> drop))) + fill)
                value = ((((here_bits << 24) | ((here_op << 16))) | here_val) | 0)
                if ((index2 >= 0) and ((index2 < ((table.byteLength >> 2))))):
                    _this7 = table.bytes
                    pos7 = (((index2 << 2)) + table.byteOffset)
                    _this7.b[pos7] = (value & 255)
                    _this7.b[(pos7 + 1)] = ((value >> 8) & 255)
                    _this7.b[(pos7 + 2)] = ((value >> 16) & 255)
                    _this7.b[(pos7 + 3)] = (HxOverrides.rshift(value, 24) & 255)
                if (not ((fill != 0))):
                    break
            incr = (1 << ((_hx_len - 1)))
            while (((huff & incr)) != 0):
                incr = (incr >> 1)
            if (incr != 0):
                huff = (huff & ((incr - 1)))
                huff = (huff + incr)
            else:
                huff = 0
            sym = (sym + 1)
            _g = _hx_len
            _g1 = count
            _this8 = _g1.bytes
            pos8 = (((_g << 1)) + _g1.byteOffset)
            value1 = (((_this8.b[pos8] | ((_this8.b[(pos8 + 1)] << 8)))) - 1)
            if ((_g >= 0) and ((_g < ((_g1.byteLength >> 1))))):
                _this9 = _g1.bytes
                pos9 = (((_g << 1)) + _g1.byteOffset)
                _this9.b[pos9] = (value1 & 255)
                _this9.b[(pos9 + 1)] = ((value1 >> 8) & 255)
            _this10 = count.bytes
            pos10 = (((_hx_len << 1)) + count.byteOffset)
            if (((_this10.b[pos10] | ((_this10.b[(pos10 + 1)] << 8)))) == 0):
                if (_hx_len == _hx_max):
                    break
                _this11 = work.bytes
                pos11 = (((sym << 1)) + work.byteOffset)
                index3 = (lens_index + ((_this11.b[pos11] | ((_this11.b[(pos11 + 1)] << 8)))))
                _this12 = lens.bytes
                pos12 = (((index3 << 1)) + lens.byteOffset)
                _hx_len = (_this12.b[pos12] | ((_this12.b[(pos12 + 1)] << 8)))
            if ((_hx_len > root) and ((((huff & mask)) != low))):
                if (drop == 0):
                    drop = root
                next = (next + _hx_min)
                curr = (_hx_len - drop)
                left = (1 << curr)
                while ((curr + drop) < _hx_max):
                    _this13 = count.bytes
                    pos13 = ((((curr + drop) << 1)) + count.byteOffset)
                    left = (left - ((_this13.b[pos13] | ((_this13.b[(pos13 + 1)] << 8)))))
                    if (left <= 0):
                        break
                    curr = (curr + 1)
                    left = (left << 1)
                used = (used + ((1 << curr)))
                if (((_hx_type == pako_zlib_InfTrees.LENS) and ((used > pako_zlib_InfTrees.ENOUGH_LENS))) or (((_hx_type == pako_zlib_InfTrees.DISTS) and ((used > pako_zlib_InfTrees.ENOUGH_DISTS))))):
                    return 1
                low = (huff & mask)
                value2 = ((((root << 24) | ((curr << 16))) | ((next - table_index))) | 0)
                if ((low >= 0) and ((low < ((table.byteLength >> 2))))):
                    _this14 = table.bytes
                    pos14 = (((low << 2)) + table.byteOffset)
                    _this14.b[pos14] = (value2 & 255)
                    _this14.b[(pos14 + 1)] = ((value2 >> 8) & 255)
                    _this14.b[(pos14 + 2)] = ((value2 >> 16) & 255)
                    _this14.b[(pos14 + 3)] = (HxOverrides.rshift(value2, 24) & 255)
        if (huff != 0):
            index = (next + huff)
            value = ((((_hx_len - drop) << 24) | 4194304) | 0)
            if ((index >= 0) and ((index < ((table.byteLength >> 2))))):
                _this = table.bytes
                pos = (((index << 2)) + table.byteOffset)
                _this.b[pos] = (value & 255)
                _this.b[(pos + 1)] = ((value >> 8) & 255)
                _this.b[(pos + 2)] = ((value >> 16) & 255)
                _this.b[(pos + 3)] = (HxOverrides.rshift(value, 24) & 255)
        opts.bits = root
        return 0
pako_zlib_InfTrees._hx_class = pako_zlib_InfTrees
_hx_classes["pako.zlib.InfTrees"] = pako_zlib_InfTrees


class pako_zlib_Inflate:
    _hx_class_name = "pako.zlib.Inflate"
    __slots__ = ()
    _hx_statics = ["inflateResetKeep", "inflateReset", "inflateReset2", "inflateInit2", "virgin", "lenfix", "distfix", "fixedtables", "updatewindow", "inflate", "inflateEnd", "inflateGetHeader", "inflateSetDictionary"]

    @staticmethod
    def inflateResetKeep(strm):
        if ((strm is None) or ((strm.inflateState is None))):
            return -2
        state = strm.inflateState
        def _hx_local_1():
            def _hx_local_0():
                state.total = 0
                return state.total
            strm.total_out = _hx_local_0()
            return strm.total_out
        strm.total_in = _hx_local_1()
        strm.msg = ""
        if (state.wrap != 0):
            strm.adler = (state.wrap & 1)
        state.mode = 1
        state.last = False
        state.havedict = False
        state.dmax = 32768
        state.head = None
        state.hold = 0
        state.bits = 0
        size = 3408
        this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(size),0,size)
        this2 = this1
        def _hx_local_2():
            state.lendyn = this2
            return state.lendyn
        state.lencode = _hx_local_2()
        size = 2368
        this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(size),0,size)
        this2 = this1
        def _hx_local_3():
            state.distdyn = this2
            return state.distdyn
        state.distcode = _hx_local_3()
        state.sane = 1
        state.back = -1
        return 0

    @staticmethod
    def inflateReset(strm):
        if ((strm is None) or ((strm.inflateState is None))):
            return -2
        state = strm.inflateState
        state.wsize = 0
        state.whave = 0
        state.wnext = 0
        return pako_zlib_Inflate.inflateResetKeep(strm)

    @staticmethod
    def inflateReset2(strm,windowBits):
        wrap = None
        if ((strm is None) or ((strm.inflateState is None))):
            return -2
        state = strm.inflateState
        if (windowBits < 0):
            wrap = 0
            windowBits = -windowBits
        else:
            wrap = (((windowBits >> 4)) + 1)
            if (windowBits < 48):
                windowBits = (windowBits & 15)
        if ((windowBits != 0) and (((windowBits < 8) or ((windowBits > 15))))):
            return -2
        if ((state.window is not None) and ((state.wbits != windowBits))):
            state.window = None
        state.wrap = wrap
        state.wbits = windowBits
        return pako_zlib_Inflate.inflateReset(strm)

    @staticmethod
    def inflateInit2(strm,windowBits):
        if (strm is None):
            return -2
        state = pako_zlib_InflateState()
        strm.inflateState = state
        state.window = None
        ret = pako_zlib_Inflate.inflateReset2(strm,windowBits)
        if (ret != 0):
            strm.inflateState = None
        return ret

    @staticmethod
    def fixedtables(state):
        if pako_zlib_Inflate.virgin:
            size = 2048
            this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(size),0,size)
            this2 = this1
            pako_zlib_Inflate.lenfix = this2
            size = 128
            this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(size),0,size)
            this2 = this1
            pako_zlib_Inflate.distfix = this2
            sym = 0
            while (sym < 144):
                this1 = state.lens
                index = sym
                sym = (sym + 1)
                if ((index >= 0) and ((index < ((this1.byteLength >> 1))))):
                    _this = this1.bytes
                    pos = (((index << 1)) + this1.byteOffset)
                    _this.b[pos] = 8
                    _this.b[(pos + 1)] = 0
            while (sym < 256):
                this1 = state.lens
                index = sym
                sym = (sym + 1)
                if ((index >= 0) and ((index < ((this1.byteLength >> 1))))):
                    _this = this1.bytes
                    pos = (((index << 1)) + this1.byteOffset)
                    _this.b[pos] = 9
                    _this.b[(pos + 1)] = 0
            while (sym < 280):
                this1 = state.lens
                index = sym
                sym = (sym + 1)
                if ((index >= 0) and ((index < ((this1.byteLength >> 1))))):
                    _this = this1.bytes
                    pos = (((index << 1)) + this1.byteOffset)
                    _this.b[pos] = 7
                    _this.b[(pos + 1)] = 0
            while (sym < 288):
                this1 = state.lens
                index = sym
                sym = (sym + 1)
                if ((index >= 0) and ((index < ((this1.byteLength >> 1))))):
                    _this = this1.bytes
                    pos = (((index << 1)) + this1.byteOffset)
                    _this.b[pos] = 8
                    _this.b[(pos + 1)] = 0
            pako_zlib_InfTrees.inflate_table(1,state.lens,0,288,pako_zlib_Inflate.lenfix,0,state.work,_hx_AnonObject({'bits': 9}))
            sym = 0
            while (sym < 32):
                this1 = state.lens
                index = sym
                sym = (sym + 1)
                if ((index >= 0) and ((index < ((this1.byteLength >> 1))))):
                    _this = this1.bytes
                    pos = (((index << 1)) + this1.byteOffset)
                    _this.b[pos] = 5
                    _this.b[(pos + 1)] = 0
            pako_zlib_InfTrees.inflate_table(2,state.lens,0,32,pako_zlib_Inflate.distfix,0,state.work,_hx_AnonObject({'bits': 5}))
            pako_zlib_Inflate.virgin = False
        state.lencode = pako_zlib_Inflate.lenfix
        state.lenbits = 9
        state.distcode = pako_zlib_Inflate.distfix
        state.distbits = 5

    @staticmethod
    def updatewindow(strm,src,end,copy):
        dist = None
        state = strm.inflateState
        if (state.window is None):
            state.wsize = (1 << state.wbits)
            state.wnext = 0
            state.whave = 0
            elements = state.wsize
            this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(elements),0,elements)
            this2 = this1
            state.window = this2
        if (copy >= state.wsize):
            dest = state.window
            src1 = src
            dest.bytes.blit(dest.byteOffset,src1.bytes,(src1.byteOffset + ((end - state.wsize))),state.wsize)
            state.wnext = 0
            state.whave = state.wsize
        else:
            dist = (state.wsize - state.wnext)
            if (dist > copy):
                dist = copy
            dest = state.window
            src1 = src
            dest.bytes.blit((dest.byteOffset + state.wnext),src1.bytes,(src1.byteOffset + ((end - copy))),dist)
            copy = (copy - dist)
            if (copy != 0):
                dest = state.window
                src1 = src
                dest.bytes.blit(dest.byteOffset,src1.bytes,(src1.byteOffset + ((end - copy))),copy)
                state.wnext = copy
                state.whave = state.wsize
            else:
                state.wnext = (state.wnext + dist)
                if (state.wnext == state.wsize):
                    state.wnext = 0
                if (state.whave < state.wsize):
                    state.whave = (state.whave + dist)
        return 0

    @staticmethod
    def inflate(strm = None,flush = None):
        hold = 0
        bits = 0
        copy = 0
        _hx_from = None
        from_source = None
        here = 0
        here_bits = 0
        here_op = 0
        here_val = 0
        last_bits = None
        last_op = None
        last_val = None
        _hx_len = 0
        this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(4),0,4)
        this2 = this1
        hbuf = this2
        opts = None
        n = None
        order = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]
        if ((((strm is None) or ((strm.inflateState is None))) or ((strm.output is None))) or (((strm.input is None) and ((strm.avail_in != 0))))):
            return -2
        state = strm.inflateState
        if (state.mode == 12):
            state.mode = 13
        put = strm.next_out
        output = strm.output
        left = strm.avail_out
        next = strm.next_in
        input = strm.input
        have = strm.avail_in
        hold = state.hold
        bits = state.bits
        _in = have
        _out = left
        ret = 0
        inf_leave = False
        while (not inf_leave):
            inf_leave = False
            _g = state.mode
            if (_g == 1):
                if (state.wrap == 0):
                    state.mode = 13
                    continue
                while (bits < 16):
                    if (have == 0):
                        inf_leave = True
                        break
                    have = (have - 1)
                    index = next
                    next = (next + 1)
                    hold = (hold + ((input.bytes.b[(index + input.byteOffset)] << bits)))
                    bits = (bits + 8)
                if inf_leave:
                    break
                if ((((state.wrap & 2)) != 0) and ((hold == 35615))):
                    state.check = 0
                    value = (hold & 255)
                    if (0 < hbuf.byteLength):
                        hbuf.bytes.b[hbuf.byteOffset] = (value & 255)
                    value1 = (HxOverrides.rshift(hold, 8) & 255)
                    if (1 < hbuf.byteLength):
                        hbuf.bytes.b[(1 + hbuf.byteOffset)] = (value1 & 255)
                    state.check = pako_zlib_CRC32.crc32(state.check,hbuf,2,0)
                    hold = 0
                    bits = 0
                    state.mode = 2
                    continue
                state.flags = 0
                if (state.head is not None):
                    state.head.done = False
                if ((((state.wrap & 1)) != 1) or ((HxOverrides.mod(((((((hold & 255)) << 8)) + ((hold >> 8)))), 31) != 0))):
                    strm.msg = "incorrect header check"
                    state.mode = 30
                    continue
                if (((hold & 15)) != 8):
                    strm.msg = "unknown compression method"
                    state.mode = 30
                    continue
                hold = HxOverrides.rshift(hold, 4)
                bits = (bits - 4)
                _hx_len = (((hold & 15)) + 8)
                if (state.wbits == 0):
                    state.wbits = _hx_len
                elif (_hx_len > state.wbits):
                    strm.msg = "invalid window size"
                    state.mode = 30
                    continue
                state.dmax = (1 << _hx_len)
                def _hx_local_5():
                    state.check = 1
                    return state.check
                strm.adler = _hx_local_5()
                state.mode = (10 if ((((hold & 512)) != 0)) else 12)
                hold = 0
                bits = 0
            elif (_g == 2):
                while (bits < 16):
                    if (have == 0):
                        inf_leave = True
                        break
                    have = (have - 1)
                    index1 = next
                    next = (next + 1)
                    hold = (hold + ((input.bytes.b[(index1 + input.byteOffset)] << bits)))
                    bits = (bits + 8)
                if inf_leave:
                    break
                state.flags = hold
                if (((state.flags & 255)) != 8):
                    strm.msg = "unknown compression method"
                    state.mode = 30
                    continue
                if (((state.flags & 57344)) != 0):
                    strm.msg = "unknown header flags set"
                    state.mode = 30
                    continue
                if (state.head is not None):
                    state.head.text = ((((hold >> 8) & 1)) == 1)
                if (((state.flags & 512)) != 0):
                    value2 = (hold & 255)
                    if (0 < hbuf.byteLength):
                        hbuf.bytes.b[hbuf.byteOffset] = (value2 & 255)
                    value3 = (HxOverrides.rshift(hold, 8) & 255)
                    if (1 < hbuf.byteLength):
                        hbuf.bytes.b[(1 + hbuf.byteOffset)] = (value3 & 255)
                    state.check = pako_zlib_CRC32.crc32(state.check,hbuf,2,0)
                hold = 0
                bits = 0
                state.mode = 3
            elif (_g == 3):
                while (bits < 32):
                    if (have == 0):
                        inf_leave = True
                        break
                    have = (have - 1)
                    index2 = next
                    next = (next + 1)
                    hold = (hold + ((input.bytes.b[(index2 + input.byteOffset)] << bits)))
                    bits = (bits + 8)
                if inf_leave:
                    break
                if (state.head is not None):
                    state.head.time = hold
                if (((state.flags & 512)) != 0):
                    value4 = (hold & 255)
                    if (0 < hbuf.byteLength):
                        hbuf.bytes.b[hbuf.byteOffset] = (value4 & 255)
                    value5 = (HxOverrides.rshift(hold, 8) & 255)
                    if (1 < hbuf.byteLength):
                        hbuf.bytes.b[(1 + hbuf.byteOffset)] = (value5 & 255)
                    value6 = (HxOverrides.rshift(hold, 16) & 255)
                    if (2 < hbuf.byteLength):
                        hbuf.bytes.b[(2 + hbuf.byteOffset)] = (value6 & 255)
                    value7 = (HxOverrides.rshift(hold, 24) & 255)
                    if (3 < hbuf.byteLength):
                        hbuf.bytes.b[(3 + hbuf.byteOffset)] = (value7 & 255)
                    state.check = pako_zlib_CRC32.crc32(state.check,hbuf,4,0)
                hold = 0
                bits = 0
                state.mode = 4
            elif (_g == 4):
                while (bits < 16):
                    if (have == 0):
                        inf_leave = True
                        break
                    have = (have - 1)
                    index3 = next
                    next = (next + 1)
                    hold = (hold + ((input.bytes.b[(index3 + input.byteOffset)] << bits)))
                    bits = (bits + 8)
                if inf_leave:
                    break
                if (state.head is not None):
                    state.head.xflags = (hold & 255)
                    state.head.os = (hold >> 8)
                if (((state.flags & 512)) != 0):
                    value8 = (hold & 255)
                    if (0 < hbuf.byteLength):
                        hbuf.bytes.b[hbuf.byteOffset] = (value8 & 255)
                    value9 = (HxOverrides.rshift(hold, 8) & 255)
                    if (1 < hbuf.byteLength):
                        hbuf.bytes.b[(1 + hbuf.byteOffset)] = (value9 & 255)
                    state.check = pako_zlib_CRC32.crc32(state.check,hbuf,2,0)
                hold = 0
                bits = 0
                state.mode = 5
            elif (_g == 5):
                if (((state.flags & 1024)) != 0):
                    while (bits < 16):
                        if (have == 0):
                            inf_leave = True
                            break
                        have = (have - 1)
                        index4 = next
                        next = (next + 1)
                        hold = (hold + ((input.bytes.b[(index4 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    if inf_leave:
                        break
                    state.length = hold
                    if (state.head is not None):
                        state.head.extra_len = hold
                    if (((state.flags & 512)) != 0):
                        value10 = (hold & 255)
                        if (0 < hbuf.byteLength):
                            hbuf.bytes.b[hbuf.byteOffset] = (value10 & 255)
                        value11 = (HxOverrides.rshift(hold, 8) & 255)
                        if (1 < hbuf.byteLength):
                            hbuf.bytes.b[(1 + hbuf.byteOffset)] = (value11 & 255)
                        state.check = pako_zlib_CRC32.crc32(state.check,hbuf,2,0)
                    hold = 0
                    bits = 0
                elif (state.head is not None):
                    state.head.extra = None
                state.mode = 6
            elif (_g == 6):
                if (((state.flags & 1024)) != 0):
                    copy = state.length
                    if (copy > have):
                        copy = have
                    if (copy != 0):
                        if (state.head is not None):
                            _hx_len = (state.head.extra_len - state.length)
                            if (state.head.extra is None):
                                elements = state.head.extra_len
                                this1 = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(elements),0,elements)
                                this2 = this1
                                state.head.extra = this2
                            dest = state.head.extra
                            src = input
                            dest.bytes.blit((dest.byteOffset + _hx_len),src.bytes,(src.byteOffset + next),copy)
                        if (((state.flags & 512)) != 0):
                            state.check = pako_zlib_CRC32.crc32(state.check,input,copy,next)
                        have = (have - copy)
                        next = (next + copy)
                        state.length = (state.length - copy)
                    if (state.length != 0):
                        inf_leave = True
                        break
                state.length = 0
                state.mode = 7
            elif (_g == 7):
                if (((state.flags & 2048)) != 0):
                    if (have == 0):
                        inf_leave = True
                        break
                    copy = 0
                    while True:
                        index5 = copy
                        copy = (copy + 1)
                        _hx_len = input.bytes.b[((next + index5) + input.byteOffset)]
                        if (((state.head is not None) and ((_hx_len != 0))) and ((state.length < 65536))):
                            _hx_local_21 = state.head
                            _hx_local_22 = _hx_local_21.name
                            _hx_local_21.name = (("null" if _hx_local_22 is None else _hx_local_22) + HxOverrides.stringOrNull("".join(map(chr,[_hx_len]))))
                            _hx_local_21.name
                        if (not (((_hx_len != 0) and ((copy < have))))):
                            break
                    if (((state.flags & 512)) != 0):
                        state.check = pako_zlib_CRC32.crc32(state.check,input,copy,next)
                    have = (have - copy)
                    next = (next + copy)
                    if (_hx_len != 0):
                        inf_leave = True
                        break
                elif (state.head is not None):
                    state.head.name = None
                state.length = 0
                state.mode = 8
            elif (_g == 8):
                if (((state.flags & 4096)) != 0):
                    if (have == 0):
                        inf_leave = True
                        break
                    copy = 0
                    while True:
                        index6 = copy
                        copy = (copy + 1)
                        _hx_len = input.bytes.b[((next + index6) + input.byteOffset)]
                        if (((state.head is not None) and ((_hx_len != 0))) and ((state.length < 65536))):
                            _hx_local_25 = state.head
                            _hx_local_26 = _hx_local_25.comment
                            _hx_local_25.comment = (("null" if _hx_local_26 is None else _hx_local_26) + HxOverrides.stringOrNull("".join(map(chr,[_hx_len]))))
                            _hx_local_25.comment
                        if (not (((_hx_len != 0) and ((copy < have))))):
                            break
                    if (((state.flags & 512)) != 0):
                        state.check = pako_zlib_CRC32.crc32(state.check,input,copy,next)
                    have = (have - copy)
                    next = (next + copy)
                    if (_hx_len != 0):
                        inf_leave = True
                        break
                elif (state.head is not None):
                    state.head.comment = None
                state.mode = 9
            elif (_g == 9):
                if (((state.flags & 512)) != 0):
                    while (bits < 16):
                        if (have == 0):
                            inf_leave = True
                            break
                        have = (have - 1)
                        index7 = next
                        next = (next + 1)
                        hold = (hold + ((input.bytes.b[(index7 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    if inf_leave:
                        break
                    if (hold != ((state.check & 65535))):
                        strm.msg = "header crc mismatch"
                        state.mode = 30
                        continue
                    hold = 0
                    bits = 0
                if (state.head is not None):
                    state.head.hcrc = ((state.flags >> 9) & 1)
                    state.head.done = True
                def _hx_local_32():
                    state.check = 0
                    return state.check
                strm.adler = _hx_local_32()
                state.mode = 12
            elif (_g == 10):
                while (bits < 32):
                    if (have == 0):
                        inf_leave = True
                        break
                    have = (have - 1)
                    index8 = next
                    next = (next + 1)
                    hold = (hold + ((input.bytes.b[(index8 + input.byteOffset)] << bits)))
                    bits = (bits + 8)
                if inf_leave:
                    break
                def _hx_local_36():
                    state.check = (((((HxOverrides.rshift(hold, 24) & 255)) + ((HxOverrides.rshift(hold, 8) & 65280))) + ((((hold & 65280)) << 8))) + ((((hold & 255)) << 24)))
                    return state.check
                strm.adler = _hx_local_36()
                hold = 0
                bits = 0
                state.mode = 11
            elif (_g == 11):
                if (not state.havedict):
                    strm.next_out = put
                    strm.avail_out = left
                    strm.next_in = next
                    strm.avail_in = have
                    state.hold = hold
                    state.bits = bits
                    return 2
                def _hx_local_37():
                    state.check = 1
                    return state.check
                strm.adler = _hx_local_37()
                state.mode = 12
            elif (_g == 12):
                if ((flush == 5) or ((flush == 6))):
                    continue
                state.mode = 13
            elif (_g == 13):
                if state.last:
                    hold = HxOverrides.rshift(hold, ((bits & 7)))
                    bits = (bits - ((bits & 7)))
                    state.mode = 27
                    continue
                while (bits < 3):
                    if (have == 0):
                        inf_leave = True
                        break
                    have = (have - 1)
                    index9 = next
                    next = (next + 1)
                    hold = (hold + ((input.bytes.b[(index9 + input.byteOffset)] << bits)))
                    bits = (bits + 8)
                if inf_leave:
                    break
                state.last = (((hold & 1)) == 1)
                hold = HxOverrides.rshift(hold, 1)
                bits = (bits - 1)
                _g1 = (hold & 3)
                if (_g1 == 0):
                    state.mode = 14
                elif (_g1 == 1):
                    pako_zlib_Inflate.fixedtables(state)
                    state.mode = 20
                    if (flush == 6):
                        hold = HxOverrides.rshift(hold, 2)
                        bits = (bits - 2)
                        inf_leave = True
                        break
                elif (_g1 == 2):
                    state.mode = 17
                elif (_g1 == 3):
                    strm.msg = "invalid block type"
                    state.mode = 30
                else:
                    pass
                hold = HxOverrides.rshift(hold, 2)
                bits = (bits - 2)
            elif (_g == 14):
                hold = HxOverrides.rshift(hold, ((bits & 7)))
                bits = (bits - ((bits & 7)))
                while (bits < 32):
                    if (have == 0):
                        inf_leave = True
                        break
                    have = (have - 1)
                    index10 = next
                    next = (next + 1)
                    hold = (hold + ((input.bytes.b[(index10 + input.byteOffset)] << bits)))
                    bits = (bits + 8)
                if inf_leave:
                    break
                if (((hold & 65535)) != ((HxOverrides.rshift(hold, 16) ^ 65535))):
                    strm.msg = "invalid stored block lengths"
                    state.mode = 30
                    continue
                state.length = (hold & 65535)
                hold = 0
                bits = 0
                state.mode = 15
                if (flush == 6):
                    inf_leave = True
                    break
            elif (_g == 15):
                state.mode = 16
            elif (_g == 16):
                copy = state.length
                if (copy != 0):
                    if (copy > have):
                        copy = have
                    if (copy > left):
                        copy = left
                    if (copy == 0):
                        inf_leave = True
                        break
                    dest1 = output
                    src1 = input
                    dest1.bytes.blit((dest1.byteOffset + put),src1.bytes,(src1.byteOffset + next),copy)
                    have = (have - copy)
                    next = (next + copy)
                    left = (left - copy)
                    put = (put + copy)
                    state.length = (state.length - copy)
                    continue
                state.mode = 12
            elif (_g == 17):
                while (bits < 14):
                    if (have == 0):
                        inf_leave = True
                        break
                    have = (have - 1)
                    index11 = next
                    next = (next + 1)
                    hold = (hold + ((input.bytes.b[(index11 + input.byteOffset)] << bits)))
                    bits = (bits + 8)
                if inf_leave:
                    break
                state.nlen = (((hold & 31)) + 257)
                hold = HxOverrides.rshift(hold, 5)
                bits = (bits - 5)
                state.ndist = (((hold & 31)) + 1)
                hold = HxOverrides.rshift(hold, 5)
                bits = (bits - 5)
                state.ncode = (((hold & 15)) + 4)
                hold = HxOverrides.rshift(hold, 4)
                bits = (bits - 4)
                if ((state.nlen > 286) or ((state.ndist > 30))):
                    strm.msg = "too many length or distance symbols"
                    state.mode = 30
                    continue
                state.have = 0
                state.mode = 18
            elif (_g == 18):
                while (state.have < state.ncode):
                    while (bits < 3):
                        if (have == 0):
                            inf_leave = True
                            break
                        have = (have - 1)
                        index12 = next
                        next = (next + 1)
                        hold = (hold + ((input.bytes.b[(index12 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    if inf_leave:
                        break
                    this3 = state.lens
                    def _hx_local_72():
                        _hx_local_71 = state.have
                        state.have = (state.have + 1)
                        return _hx_local_71
                    index13 = python_internal_ArrayImpl._get(order, _hx_local_72())
                    value12 = (hold & 7)
                    if ((index13 >= 0) and ((index13 < ((this3.byteLength >> 1))))):
                        _this = this3.bytes
                        pos = (((index13 << 1)) + this3.byteOffset)
                        _this.b[pos] = (value12 & 255)
                        _this.b[(pos + 1)] = ((value12 >> 8) & 255)
                    hold = HxOverrides.rshift(hold, 3)
                    bits = (bits - 3)
                if inf_leave:
                    break
                while (state.have < 19):
                    this4 = state.lens
                    def _hx_local_76():
                        _hx_local_75 = state.have
                        state.have = (state.have + 1)
                        return _hx_local_75
                    index14 = python_internal_ArrayImpl._get(order, _hx_local_76())
                    if ((index14 >= 0) and ((index14 < ((this4.byteLength >> 1))))):
                        _this1 = this4.bytes
                        pos1 = (((index14 << 1)) + this4.byteOffset)
                        _this1.b[pos1] = 0
                        _this1.b[(pos1 + 1)] = 0
                state.lencode = state.lendyn
                state.lenbits = 7
                opts = _hx_AnonObject({'bits': state.lenbits})
                ret = pako_zlib_InfTrees.inflate_table(0,state.lens,0,19,state.lencode,0,state.work,opts)
                state.lenbits = opts.bits
                if (ret != 0):
                    strm.msg = "invalid code lengths set"
                    state.mode = 30
                    continue
                state.have = 0
                state.mode = 19
            elif (_g == 19):
                while (state.have < ((state.nlen + state.ndist))):
                    while True:
                        this5 = state.lencode
                        _this2 = this5.bytes
                        pos2 = (((((hold & ((((1 << state.lenbits)) - 1)))) << 2)) + this5.byteOffset)
                        v = (((_this2.b[pos2] | ((_this2.b[(pos2 + 1)] << 8))) | ((_this2.b[(pos2 + 2)] << 16))) | ((_this2.b[(pos2 + 3)] << 24)))
                        here = ((v | -2147483648) if ((((v & -2147483648)) != 0)) else v)
                        here_bits = HxOverrides.rshift(here, 24)
                        here_op = (HxOverrides.rshift(here, 16) & 255)
                        here_val = (here & 65535)
                        if (here_bits <= bits):
                            break
                        if (have == 0):
                            inf_leave = True
                            break
                        have = (have - 1)
                        index15 = next
                        next = (next + 1)
                        hold = (hold + ((input.bytes.b[(index15 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    if inf_leave:
                        break
                    if (here_val < 16):
                        hold = HxOverrides.rshift(hold, here_bits)
                        bits = (bits - here_bits)
                        this6 = state.lens
                        def _hx_local_83():
                            _hx_local_82 = state.have
                            state.have = (state.have + 1)
                            return _hx_local_82
                        index16 = _hx_local_83()
                        if ((index16 >= 0) and ((index16 < ((this6.byteLength >> 1))))):
                            _this3 = this6.bytes
                            pos3 = (((index16 << 1)) + this6.byteOffset)
                            _this3.b[pos3] = (here_val & 255)
                            _this3.b[(pos3 + 1)] = ((here_val >> 8) & 255)
                    else:
                        if (here_val == 16):
                            n = (here_bits + 2)
                            while (bits < n):
                                if (have == 0):
                                    inf_leave = True
                                    break
                                have = (have - 1)
                                index17 = next
                                next = (next + 1)
                                hold = (hold + ((input.bytes.b[(index17 + input.byteOffset)] << bits)))
                                bits = (bits + 8)
                            if inf_leave:
                                break
                            hold = HxOverrides.rshift(hold, here_bits)
                            bits = (bits - here_bits)
                            if (state.have == 0):
                                strm.msg = "invalid bit length repeat"
                                state.mode = 30
                                break
                            this7 = state.lens
                            _this4 = this7.bytes
                            pos4 = ((((state.have - 1) << 1)) + this7.byteOffset)
                            _hx_len = (_this4.b[pos4] | ((_this4.b[(pos4 + 1)] << 8)))
                            copy = (3 + ((hold & 3)))
                            hold = HxOverrides.rshift(hold, 2)
                            bits = (bits - 2)
                        elif (here_val == 17):
                            n = (here_bits + 3)
                            while (bits < n):
                                if (have == 0):
                                    inf_leave = True
                                    break
                                have = (have - 1)
                                index18 = next
                                next = (next + 1)
                                hold = (hold + ((input.bytes.b[(index18 + input.byteOffset)] << bits)))
                                bits = (bits + 8)
                            if inf_leave:
                                break
                            hold = HxOverrides.rshift(hold, here_bits)
                            bits = (bits - here_bits)
                            _hx_len = 0
                            copy = (3 + ((hold & 7)))
                            hold = HxOverrides.rshift(hold, 3)
                            bits = (bits - 3)
                        else:
                            n = (here_bits + 7)
                            while (bits < n):
                                if (have == 0):
                                    inf_leave = True
                                    break
                                have = (have - 1)
                                index19 = next
                                next = (next + 1)
                                hold = (hold + ((input.bytes.b[(index19 + input.byteOffset)] << bits)))
                                bits = (bits + 8)
                            if inf_leave:
                                break
                            hold = HxOverrides.rshift(hold, here_bits)
                            bits = (bits - here_bits)
                            _hx_len = 0
                            copy = (11 + ((hold & 127)))
                            hold = HxOverrides.rshift(hold, 7)
                            bits = (bits - 7)
                        if ((state.have + copy) > ((state.nlen + state.ndist))):
                            strm.msg = "invalid bit length repeat"
                            state.mode = 30
                            break
                        while True:
                            tmp = copy
                            copy = (copy - 1)
                            if (not ((tmp != 0))):
                                break
                            this8 = state.lens
                            def _hx_local_106():
                                _hx_local_105 = state.have
                                state.have = (state.have + 1)
                                return _hx_local_105
                            index20 = _hx_local_106()
                            if ((index20 >= 0) and ((index20 < ((this8.byteLength >> 1))))):
                                _this5 = this8.bytes
                                pos5 = (((index20 << 1)) + this8.byteOffset)
                                _this5.b[pos5] = (_hx_len & 255)
                                _this5.b[(pos5 + 1)] = ((_hx_len >> 8) & 255)
                if (inf_leave or ((state.mode == 30))):
                    continue
                this9 = state.lens
                _this6 = this9.bytes
                pos6 = (512 + this9.byteOffset)
                if (((_this6.b[pos6] | ((_this6.b[(pos6 + 1)] << 8)))) == 0):
                    strm.msg = "invalid code -- missing end-of-block"
                    state.mode = 30
                    continue
                state.lenbits = 9
                opts = _hx_AnonObject({'bits': state.lenbits})
                ret = pako_zlib_InfTrees.inflate_table(1,state.lens,0,state.nlen,state.lencode,0,state.work,opts)
                state.lenbits = opts.bits
                if (ret != 0):
                    strm.msg = "invalid literal/lengths set"
                    state.mode = 30
                    continue
                state.distbits = 6
                state.distcode = state.distdyn
                opts = _hx_AnonObject({'bits': state.distbits})
                ret = pako_zlib_InfTrees.inflate_table(2,state.lens,state.nlen,state.ndist,state.distcode,0,state.work,opts)
                state.distbits = opts.bits
                if (ret != 0):
                    strm.msg = "invalid distances set"
                    state.mode = 30
                    continue
                state.mode = 20
                if (flush == 6):
                    inf_leave = True
                    continue
            elif (_g == 20):
                state.mode = 21
            elif (_g == 21):
                if ((have >= 6) and ((left >= 258))):
                    strm.next_out = put
                    strm.avail_out = left
                    strm.next_in = next
                    strm.avail_in = have
                    state.hold = hold
                    state.bits = bits
                    pako_zlib_InfFast.inflate_fast(strm,_out)
                    put = strm.next_out
                    output = strm.output
                    left = strm.avail_out
                    next = strm.next_in
                    input = strm.input
                    have = strm.avail_in
                    hold = state.hold
                    bits = state.bits
                    if (state.mode == 12):
                        state.back = -1
                    continue
                state.back = 0
                while True:
                    this10 = state.lencode
                    _this7 = this10.bytes
                    pos7 = (((((hold & ((((1 << state.lenbits)) - 1)))) << 2)) + this10.byteOffset)
                    v1 = (((_this7.b[pos7] | ((_this7.b[(pos7 + 1)] << 8))) | ((_this7.b[(pos7 + 2)] << 16))) | ((_this7.b[(pos7 + 3)] << 24)))
                    here = ((v1 | -2147483648) if ((((v1 & -2147483648)) != 0)) else v1)
                    here_bits = HxOverrides.rshift(here, 24)
                    here_op = (HxOverrides.rshift(here, 16) & 255)
                    here_val = (here & 65535)
                    if (here_bits <= bits):
                        break
                    if (have == 0):
                        inf_leave = True
                        break
                    have = (have - 1)
                    index21 = next
                    next = (next + 1)
                    hold = (hold + ((input.bytes.b[(index21 + input.byteOffset)] << bits)))
                    bits = (bits + 8)
                if inf_leave:
                    continue
                if ((here_op != 0) and ((((here_op & 240)) == 0))):
                    last_bits = here_bits
                    last_op = here_op
                    last_val = here_val
                    while True:
                        this11 = state.lencode
                        _this8 = this11.bytes
                        pos8 = ((((last_val + ((((hold & ((((1 << ((last_bits + last_op)))) - 1)))) >> last_bits))) << 2)) + this11.byteOffset)
                        v2 = (((_this8.b[pos8] | ((_this8.b[(pos8 + 1)] << 8))) | ((_this8.b[(pos8 + 2)] << 16))) | ((_this8.b[(pos8 + 3)] << 24)))
                        here = ((v2 | -2147483648) if ((((v2 & -2147483648)) != 0)) else v2)
                        here_bits = HxOverrides.rshift(here, 24)
                        here_op = (HxOverrides.rshift(here, 16) & 255)
                        here_val = (here & 65535)
                        if ((last_bits + here_bits) <= bits):
                            break
                        if (have == 0):
                            inf_leave = True
                            break
                        have = (have - 1)
                        index22 = next
                        next = (next + 1)
                        hold = (hold + ((input.bytes.b[(index22 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    if inf_leave:
                        continue
                    hold = HxOverrides.rshift(hold, last_bits)
                    bits = (bits - last_bits)
                    state.back = (state.back + last_bits)
                hold = HxOverrides.rshift(hold, here_bits)
                bits = (bits - here_bits)
                state.back = (state.back + here_bits)
                state.length = here_val
                if (here_op == 0):
                    state.mode = 26
                    continue
                if (((here_op & 32)) != 0):
                    state.back = -1
                    state.mode = 12
                    continue
                if (((here_op & 64)) != 0):
                    strm.msg = "invalid literal/length code"
                    state.mode = 30
                    continue
                state.extra = (here_op & 15)
                state.mode = 22
            elif (_g == 22):
                if (state.extra != 0):
                    n = state.extra
                    while (bits < n):
                        if (have == 0):
                            inf_leave = True
                            break
                        have = (have - 1)
                        index23 = next
                        next = (next + 1)
                        hold = (hold + ((input.bytes.b[(index23 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    if inf_leave:
                        continue
                    state.length = (state.length + ((hold & ((((1 << state.extra)) - 1)))))
                    hold = HxOverrides.rshift(hold, state.extra)
                    bits = (bits - state.extra)
                    state.back = (state.back + state.extra)
                state.was = state.length
                state.mode = 23
            elif (_g == 23):
                while True:
                    this12 = state.distcode
                    _this9 = this12.bytes
                    pos9 = (((((hold & ((((1 << state.distbits)) - 1)))) << 2)) + this12.byteOffset)
                    v3 = (((_this9.b[pos9] | ((_this9.b[(pos9 + 1)] << 8))) | ((_this9.b[(pos9 + 2)] << 16))) | ((_this9.b[(pos9 + 3)] << 24)))
                    here = ((v3 | -2147483648) if ((((v3 & -2147483648)) != 0)) else v3)
                    here_bits = HxOverrides.rshift(here, 24)
                    here_op = (HxOverrides.rshift(here, 16) & 255)
                    here_val = (here & 65535)
                    if (here_bits <= bits):
                        break
                    if (have == 0):
                        inf_leave = True
                        break
                    have = (have - 1)
                    index24 = next
                    next = (next + 1)
                    hold = (hold + ((input.bytes.b[(index24 + input.byteOffset)] << bits)))
                    bits = (bits + 8)
                if inf_leave:
                    continue
                if (((here_op & 240)) == 0):
                    last_bits = here_bits
                    last_op = here_op
                    last_val = here_val
                    while True:
                        this13 = state.distcode
                        _this10 = this13.bytes
                        pos10 = ((((last_val + ((((hold & ((((1 << ((last_bits + last_op)))) - 1)))) >> last_bits))) << 2)) + this13.byteOffset)
                        v4 = (((_this10.b[pos10] | ((_this10.b[(pos10 + 1)] << 8))) | ((_this10.b[(pos10 + 2)] << 16))) | ((_this10.b[(pos10 + 3)] << 24)))
                        here = ((v4 | -2147483648) if ((((v4 & -2147483648)) != 0)) else v4)
                        here_bits = HxOverrides.rshift(here, 24)
                        here_op = (HxOverrides.rshift(here, 16) & 255)
                        here_val = (here & 65535)
                        if ((last_bits + here_bits) <= bits):
                            break
                        if (have == 0):
                            inf_leave = True
                            break
                        have = (have - 1)
                        index25 = next
                        next = (next + 1)
                        hold = (hold + ((input.bytes.b[(index25 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    if inf_leave:
                        continue
                    hold = HxOverrides.rshift(hold, last_bits)
                    bits = (bits - last_bits)
                    state.back = (state.back + last_bits)
                hold = HxOverrides.rshift(hold, here_bits)
                bits = (bits - here_bits)
                state.back = (state.back + here_bits)
                if (((here_op & 64)) != 0):
                    strm.msg = "invalid distance code"
                    state.mode = 30
                    continue
                state.offset = here_val
                state.extra = (here_op & 15)
                state.mode = 24
            elif (_g == 24):
                if (state.extra != 0):
                    n = state.extra
                    while (bits < n):
                        if (have == 0):
                            inf_leave = True
                            break
                        have = (have - 1)
                        index26 = next
                        next = (next + 1)
                        hold = (hold + ((input.bytes.b[(index26 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    if inf_leave:
                        continue
                    state.offset = (state.offset + ((hold & ((((1 << state.extra)) - 1)))))
                    hold = HxOverrides.rshift(hold, state.extra)
                    bits = (bits - state.extra)
                    state.back = (state.back + state.extra)
                if (state.offset > state.dmax):
                    strm.msg = "invalid distance too far back"
                    state.mode = 30
                    continue
                state.mode = 25
            elif (_g == 25):
                if (left == 0):
                    inf_leave = True
                    continue
                copy = (_out - left)
                if (state.offset > copy):
                    copy = (state.offset - copy)
                    if (copy > state.whave):
                        if (state.sane != 0):
                            strm.msg = "invalid distance too far back"
                            state.mode = 30
                            continue
                    if (copy > state.wnext):
                        copy = (copy - state.wnext)
                        _hx_from = (state.wsize - copy)
                    else:
                        _hx_from = (state.wnext - copy)
                    if (copy > state.length):
                        copy = state.length
                    from_source = state.window
                else:
                    from_source = output
                    _hx_from = (put - state.offset)
                    copy = state.length
                if (copy > left):
                    copy = left
                left = (left - copy)
                state.length = (state.length - copy)
                while True:
                    index27 = put
                    put = (put + 1)
                    index28 = _hx_from
                    _hx_from = (_hx_from + 1)
                    value13 = from_source.bytes.b[(index28 + from_source.byteOffset)]
                    if ((index27 >= 0) and ((index27 < output.byteLength))):
                        output.bytes.b[(index27 + output.byteOffset)] = (value13 & 255)
                    copy = (copy - 1)
                    tmp1 = copy
                    if (not ((tmp1 != 0))):
                        break
                if (state.length == 0):
                    state.mode = 21
            elif (_g == 26):
                if (left == 0):
                    inf_leave = True
                    continue
                index29 = put
                put = (put + 1)
                value14 = state.length
                if ((index29 >= 0) and ((index29 < output.byteLength))):
                    output.bytes.b[(index29 + output.byteOffset)] = (value14 & 255)
                left = (left - 1)
                state.mode = 21
            elif (_g == 27):
                if (state.wrap != 0):
                    while (bits < 32):
                        if (have == 0):
                            inf_leave = True
                            break
                        have = (have - 1)
                        index30 = next
                        next = (next + 1)
                        hold = (hold | ((input.bytes.b[(index30 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    if inf_leave:
                        continue
                    _out = (_out - left)
                    strm.total_out = (strm.total_out + _out)
                    state.total = (state.total + _out)
                    if (_out != 0):
                        def _hx_local_155():
                            state.check = (pako_zlib_CRC32.crc32(state.check,output,_out,(put - _out)) if ((state.flags != 0)) else pako_zlib_Adler32.adler32(state.check,output,_out,(put - _out)))
                            return state.check
                        strm.adler = _hx_local_155()
                    _out = left
                    hold = ((hold + (2 ** 31)) % (2 ** 32) - (2 ** 31))
                    if (((hold if ((state.flags != 0)) else (((((HxOverrides.rshift(hold, 24) & 255)) + ((HxOverrides.rshift(hold, 8) & 65280))) + ((((hold & 65280)) << 8))) + ((((hold & 255)) << 24))))) != state.check):
                        strm.msg = "incorrect data check"
                        state.mode = 30
                        continue
                    hold = 0
                    bits = 0
                state.mode = 28
            elif (_g == 28):
                if ((state.wrap != 0) and ((state.flags != 0))):
                    while (bits < 32):
                        if (have == 0):
                            inf_leave = True
                            break
                        have = (have - 1)
                        index31 = next
                        next = (next + 1)
                        hold = (hold + ((input.bytes.b[(index31 + input.byteOffset)] << bits)))
                        bits = (bits + 8)
                    if inf_leave:
                        continue
                    if (hold != ((state.total & -1))):
                        strm.msg = "incorrect length check"
                        state.mode = 30
                        continue
                    hold = 0
                    bits = 0
                state.mode = 29
            elif (_g == 29):
                ret = 1
                inf_leave = True
                continue
            elif (_g == 30):
                ret = -3
                inf_leave = True
                continue
            elif (_g == 31):
                return -4
            elif (_g == 32):
                return -2
            else:
                return -2
        strm.next_out = put
        strm.avail_out = left
        strm.next_in = next
        strm.avail_in = have
        state.hold = hold
        state.bits = bits
        if ((state.wsize != 0) or ((((_out != strm.avail_out) and ((state.mode < 30))) and (((state.mode < 27) or ((flush != 4))))))):
            if (pako_zlib_Inflate.updatewindow(strm,strm.output,strm.next_out,(_out - strm.avail_out)) != 0):
                state.mode = 31
                return -4
        _in = (_in - strm.avail_in)
        _out = (_out - strm.avail_out)
        strm.total_in = (strm.total_in + _in)
        strm.total_out = (strm.total_out + _out)
        state.total = (state.total + _out)
        if ((state.wrap != 0) and ((_out != 0))):
            def _hx_local_164():
                state.check = (pako_zlib_CRC32.crc32(state.check,output,_out,(strm.next_out - _out)) if ((state.flags != 0)) else pako_zlib_Adler32.adler32(state.check,output,_out,(strm.next_out - _out)))
                return state.check
            strm.adler = _hx_local_164()
        strm.data_type = (((state.bits + ((64 if (state.last) else 0))) + ((128 if ((state.mode == 12)) else 0))) + ((256 if (((state.mode == 20) or ((state.mode == 15)))) else 0)))
        if (((((_in == 0) and ((_out == 0))) or ((flush == 4)))) and ((ret == 0))):
            ret = -5
        return ret

    @staticmethod
    def inflateEnd(strm = None):
        if ((strm is None) or ((strm.inflateState is None))):
            return -2
        state = strm.inflateState
        if (state.window is not None):
            state.window = None
        strm.inflateState = None
        return 0

    @staticmethod
    def inflateGetHeader(strm,head):
        if ((strm is None) or ((strm.inflateState is None))):
            return -2
        state = strm.inflateState
        if (((state.wrap & 2)) == 0):
            return -2
        state.head = head
        head.done = False
        return 0

    @staticmethod
    def inflateSetDictionary(strm,dictionary):
        dictLength = dictionary.byteLength
        dictid = None
        if ((strm is None) or ((strm.inflateState is None))):
            return -2
        state = strm.inflateState
        if ((state.wrap != 0) and ((state.mode != 11))):
            return -2
        if (state.mode == 11):
            dictid = 1
            dictid = pako_zlib_Adler32.adler32(dictid,dictionary,dictLength,0)
            if (dictid != state.check):
                return -3
        ret = pako_zlib_Inflate.updatewindow(strm,dictionary,dictLength,dictLength)
        if (ret != 0):
            state.mode = 31
            return -4
        state.havedict = True
        return 0
pako_zlib_Inflate._hx_class = pako_zlib_Inflate
_hx_classes["pako.zlib.Inflate"] = pako_zlib_Inflate


class pako_zlib_InflateState:
    _hx_class_name = "pako.zlib.InflateState"
    __slots__ = ("mode", "last", "wrap", "havedict", "flags", "dmax", "check", "total", "head", "wbits", "wsize", "whave", "wnext", "window", "hold", "bits", "length", "offset", "extra", "lencode", "distcode", "lenbits", "distbits", "ncode", "nlen", "ndist", "have", "lens", "work", "lendyn", "distdyn", "sane", "back", "was")
    _hx_fields = ["mode", "last", "wrap", "havedict", "flags", "dmax", "check", "total", "head", "wbits", "wsize", "whave", "wnext", "window", "hold", "bits", "length", "offset", "extra", "lencode", "distcode", "lenbits", "distbits", "ncode", "nlen", "ndist", "have", "lens", "work", "lendyn", "distdyn", "sane", "back", "was"]

    def __init__(self):
        self.was = 0
        self.back = 0
        self.sane = 0
        self.distdyn = None
        self.lendyn = None
        self.work = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(576),0,576)
        self.lens = haxe_io_ArrayBufferViewImpl(haxe_io_Bytes.alloc(640),0,640)
        self.have = 0
        self.ndist = 0
        self.nlen = 0
        self.ncode = 0
        self.distbits = 0
        self.lenbits = 0
        self.distcode = None
        self.lencode = None
        self.extra = 0
        self.offset = 0
        self.length = 0
        self.bits = 0
        self.hold = 0
        self.window = None
        self.wnext = 0
        self.whave = 0
        self.wsize = 0
        self.wbits = 0
        self.head = None
        self.total = 0
        self.check = 0
        self.dmax = 0
        self.flags = 0
        self.havedict = False
        self.wrap = 0
        self.last = False
        self.mode = 0

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.mode = None
        _hx_o.last = None
        _hx_o.wrap = None
        _hx_o.havedict = None
        _hx_o.flags = None
        _hx_o.dmax = None
        _hx_o.check = None
        _hx_o.total = None
        _hx_o.head = None
        _hx_o.wbits = None
        _hx_o.wsize = None
        _hx_o.whave = None
        _hx_o.wnext = None
        _hx_o.window = None
        _hx_o.hold = None
        _hx_o.bits = None
        _hx_o.length = None
        _hx_o.offset = None
        _hx_o.extra = None
        _hx_o.lencode = None
        _hx_o.distcode = None
        _hx_o.lenbits = None
        _hx_o.distbits = None
        _hx_o.ncode = None
        _hx_o.nlen = None
        _hx_o.ndist = None
        _hx_o.have = None
        _hx_o.lens = None
        _hx_o.work = None
        _hx_o.lendyn = None
        _hx_o.distdyn = None
        _hx_o.sane = None
        _hx_o.back = None
        _hx_o.was = None
pako_zlib_InflateState._hx_class = pako_zlib_InflateState
_hx_classes["pako.zlib.InflateState"] = pako_zlib_InflateState


class pako_zlib_Messages:
    _hx_class_name = "pako.zlib.Messages"
    __slots__ = ()
    _hx_statics = ["map", "get"]

    @staticmethod
    def get(error):
        return ("ERROR: " + HxOverrides.stringOrNull(pako_zlib_Messages.map.h.get(error,None)))
pako_zlib_Messages._hx_class = pako_zlib_Messages
_hx_classes["pako.zlib.Messages"] = pako_zlib_Messages


class pako_zlib_ZStream:
    _hx_class_name = "pako.zlib.ZStream"
    __slots__ = ("input", "next_in", "avail_in", "total_in", "output", "next_out", "avail_out", "total_out", "msg", "inflateState", "data_type", "adler")
    _hx_fields = ["input", "next_in", "avail_in", "total_in", "output", "next_out", "avail_out", "total_out", "msg", "inflateState", "data_type", "adler"]

    def __init__(self):
        self.adler = 0
        self.data_type = 2
        self.inflateState = None
        self.msg = ""
        self.total_out = 0
        self.avail_out = 0
        self.next_out = 0
        self.output = None
        self.total_in = 0
        self.avail_in = 0
        self.next_in = 0
        self.input = None

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.input = None
        _hx_o.next_in = None
        _hx_o.avail_in = None
        _hx_o.total_in = None
        _hx_o.output = None
        _hx_o.next_out = None
        _hx_o.avail_out = None
        _hx_o.total_out = None
        _hx_o.msg = None
        _hx_o.inflateState = None
        _hx_o.data_type = None
        _hx_o.adler = None
pako_zlib_ZStream._hx_class = pako_zlib_ZStream
_hx_classes["pako.zlib.ZStream"] = pako_zlib_ZStream


class python_Boot:
    _hx_class_name = "python.Boot"
    __slots__ = ()
    _hx_statics = ["keywords", "toString1", "fields", "simpleField", "hasField", "field", "getInstanceFields", "getSuperClass", "getClassFields", "prefixLength", "unhandleKeywords"]

    @staticmethod
    def toString1(o,s):
        if (o is None):
            return "null"
        if isinstance(o,str):
            return o
        if (s is None):
            s = ""
        if (len(s) >= 5):
            return "<...>"
        if isinstance(o,bool):
            if o:
                return "true"
            else:
                return "false"
        if (isinstance(o,int) and (not isinstance(o,bool))):
            return str(o)
        if isinstance(o,float):
            try:
                if (o == int(o)):
                    return str(Math.floor((o + 0.5)))
                else:
                    return str(o)
            except BaseException as _g:
                None
                return str(o)
        if isinstance(o,list):
            o1 = o
            l = len(o1)
            st = "["
            s = (("null" if s is None else s) + "\t")
            _g = 0
            _g1 = l
            while (_g < _g1):
                i = _g
                _g = (_g + 1)
                prefix = ""
                if (i > 0):
                    prefix = ","
                st = (("null" if st is None else st) + HxOverrides.stringOrNull(((("null" if prefix is None else prefix) + HxOverrides.stringOrNull(python_Boot.toString1((o1[i] if i >= 0 and i < len(o1) else None),s))))))
            st = (("null" if st is None else st) + "]")
            return st
        try:
            if hasattr(o,"toString"):
                return o.toString()
        except BaseException as _g:
            None
        if hasattr(o,"__class__"):
            if isinstance(o,_hx_AnonObject):
                toStr = None
                try:
                    fields = python_Boot.fields(o)
                    _g = []
                    _g1 = 0
                    while (_g1 < len(fields)):
                        f = (fields[_g1] if _g1 >= 0 and _g1 < len(fields) else None)
                        _g1 = (_g1 + 1)
                        x = ((("" + ("null" if f is None else f)) + " : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.simpleField(o,f),(("null" if s is None else s) + "\t"))))
                        _g.append(x)
                    fieldsStr = _g
                    toStr = (("{ " + HxOverrides.stringOrNull(", ".join([x1 for x1 in fieldsStr]))) + " }")
                except BaseException as _g:
                    None
                    return "{ ... }"
                if (toStr is None):
                    return "{ ... }"
                else:
                    return toStr
            if isinstance(o,Enum):
                o1 = o
                l = len(o1.params)
                hasParams = (l > 0)
                if hasParams:
                    paramsStr = ""
                    _g = 0
                    _g1 = l
                    while (_g < _g1):
                        i = _g
                        _g = (_g + 1)
                        prefix = ""
                        if (i > 0):
                            prefix = ","
                        paramsStr = (("null" if paramsStr is None else paramsStr) + HxOverrides.stringOrNull(((("null" if prefix is None else prefix) + HxOverrides.stringOrNull(python_Boot.toString1(o1.params[i],s))))))
                    return (((HxOverrides.stringOrNull(o1.tag) + "(") + ("null" if paramsStr is None else paramsStr)) + ")")
                else:
                    return o1.tag
            if hasattr(o,"_hx_class_name"):
                if (o.__class__.__name__ != "type"):
                    fields = python_Boot.getInstanceFields(o)
                    _g = []
                    _g1 = 0
                    while (_g1 < len(fields)):
                        f = (fields[_g1] if _g1 >= 0 and _g1 < len(fields) else None)
                        _g1 = (_g1 + 1)
                        x = ((("" + ("null" if f is None else f)) + " : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.simpleField(o,f),(("null" if s is None else s) + "\t"))))
                        _g.append(x)
                    fieldsStr = _g
                    toStr = (((HxOverrides.stringOrNull(o._hx_class_name) + "( ") + HxOverrides.stringOrNull(", ".join([x1 for x1 in fieldsStr]))) + " )")
                    return toStr
                else:
                    fields = python_Boot.getClassFields(o)
                    _g = []
                    _g1 = 0
                    while (_g1 < len(fields)):
                        f = (fields[_g1] if _g1 >= 0 and _g1 < len(fields) else None)
                        _g1 = (_g1 + 1)
                        x = ((("" + ("null" if f is None else f)) + " : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.simpleField(o,f),(("null" if s is None else s) + "\t"))))
                        _g.append(x)
                    fieldsStr = _g
                    toStr = (((("#" + HxOverrides.stringOrNull(o._hx_class_name)) + "( ") + HxOverrides.stringOrNull(", ".join([x1 for x1 in fieldsStr]))) + " )")
                    return toStr
            if (o == str):
                return "#String"
            if (o == list):
                return "#Array"
            if callable(o):
                return "function"
            try:
                if hasattr(o,"__repr__"):
                    return o.__repr__()
            except BaseException as _g:
                None
            if hasattr(o,"__str__"):
                return o.__str__([])
            if hasattr(o,"__name__"):
                return o.__name__
            return "???"
        else:
            return str(o)

    @staticmethod
    def fields(o):
        a = []
        if (o is not None):
            if hasattr(o,"_hx_fields"):
                fields = o._hx_fields
                if (fields is not None):
                    return list(fields)
            if isinstance(o,_hx_AnonObject):
                d = o.__dict__
                keys = d.keys()
                handler = python_Boot.unhandleKeywords
                for k in keys:
                    if (k != '_hx_disable_getattr'):
                        a.append(handler(k))
            elif hasattr(o,"__dict__"):
                d = o.__dict__
                keys1 = d.keys()
                for k in keys1:
                    a.append(k)
        return a

    @staticmethod
    def simpleField(o,field):
        if (field is None):
            return None
        field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
        if hasattr(o,field1):
            return getattr(o,field1)
        else:
            return None

    @staticmethod
    def hasField(o,field):
        if isinstance(o,_hx_AnonObject):
            return o._hx_hasattr(field)
        return hasattr(o,(("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field)))

    @staticmethod
    def field(o,field):
        if (field is None):
            return None
        if isinstance(o,str):
            field1 = field
            _hx_local_0 = len(field1)
            if (_hx_local_0 == 10):
                if (field1 == "charCodeAt"):
                    return python_internal_MethodClosure(o,HxString.charCodeAt)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 11):
                if (field1 == "lastIndexOf"):
                    return python_internal_MethodClosure(o,HxString.lastIndexOf)
                elif (field1 == "toLowerCase"):
                    return python_internal_MethodClosure(o,HxString.toLowerCase)
                elif (field1 == "toUpperCase"):
                    return python_internal_MethodClosure(o,HxString.toUpperCase)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 9):
                if (field1 == "substring"):
                    return python_internal_MethodClosure(o,HxString.substring)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 5):
                if (field1 == "split"):
                    return python_internal_MethodClosure(o,HxString.split)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 7):
                if (field1 == "indexOf"):
                    return python_internal_MethodClosure(o,HxString.indexOf)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 8):
                if (field1 == "toString"):
                    return python_internal_MethodClosure(o,HxString.toString)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 6):
                if (field1 == "charAt"):
                    return python_internal_MethodClosure(o,HxString.charAt)
                elif (field1 == "length"):
                    return len(o)
                elif (field1 == "substr"):
                    return python_internal_MethodClosure(o,HxString.substr)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            else:
                field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                if hasattr(o,field1):
                    return getattr(o,field1)
                else:
                    return None
        elif isinstance(o,list):
            field1 = field
            _hx_local_1 = len(field1)
            if (_hx_local_1 == 11):
                if (field1 == "lastIndexOf"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.lastIndexOf)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 4):
                if (field1 == "copy"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.copy)
                elif (field1 == "join"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.join)
                elif (field1 == "push"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.push)
                elif (field1 == "sort"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.sort)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 5):
                if (field1 == "shift"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.shift)
                elif (field1 == "slice"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.slice)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 7):
                if (field1 == "indexOf"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.indexOf)
                elif (field1 == "reverse"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.reverse)
                elif (field1 == "unshift"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.unshift)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 3):
                if (field1 == "map"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.map)
                elif (field1 == "pop"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.pop)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 8):
                if (field1 == "contains"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.contains)
                elif (field1 == "iterator"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.iterator)
                elif (field1 == "toString"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.toString)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 16):
                if (field1 == "keyValueIterator"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.keyValueIterator)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 6):
                if (field1 == "concat"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.concat)
                elif (field1 == "filter"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.filter)
                elif (field1 == "insert"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.insert)
                elif (field1 == "length"):
                    return len(o)
                elif (field1 == "remove"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.remove)
                elif (field1 == "splice"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.splice)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            else:
                field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                if hasattr(o,field1):
                    return getattr(o,field1)
                else:
                    return None
        else:
            field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
            if hasattr(o,field1):
                return getattr(o,field1)
            else:
                return None

    @staticmethod
    def getInstanceFields(c):
        f = (list(c._hx_fields) if (hasattr(c,"_hx_fields")) else [])
        if hasattr(c,"_hx_methods"):
            f = (f + c._hx_methods)
        sc = python_Boot.getSuperClass(c)
        if (sc is None):
            return f
        else:
            scArr = python_Boot.getInstanceFields(sc)
            scMap = set(scArr)
            _g = 0
            while (_g < len(f)):
                f1 = (f[_g] if _g >= 0 and _g < len(f) else None)
                _g = (_g + 1)
                if (not (f1 in scMap)):
                    scArr.append(f1)
            return scArr

    @staticmethod
    def getSuperClass(c):
        if (c is None):
            return None
        try:
            if hasattr(c,"_hx_super"):
                return c._hx_super
            return None
        except BaseException as _g:
            None
        return None

    @staticmethod
    def getClassFields(c):
        if hasattr(c,"_hx_statics"):
            x = c._hx_statics
            return list(x)
        else:
            return []

    @staticmethod
    def unhandleKeywords(name):
        if (HxString.substr(name,0,python_Boot.prefixLength) == "_hx_"):
            real = HxString.substr(name,python_Boot.prefixLength,None)
            if (real in python_Boot.keywords):
                return real
        return name
python_Boot._hx_class = python_Boot
_hx_classes["python.Boot"] = python_Boot


class python_HaxeIterator:
    _hx_class_name = "python.HaxeIterator"
    __slots__ = ("it", "x", "has", "checked")
    _hx_fields = ["it", "x", "has", "checked"]
    _hx_methods = ["next", "hasNext"]

    def __init__(self,it):
        self.checked = False
        self.has = False
        self.x = None
        self.it = it

    def next(self):
        if (not self.checked):
            self.hasNext()
        self.checked = False
        return self.x

    def hasNext(self):
        if (not self.checked):
            try:
                self.x = self.it.__next__()
                self.has = True
            except BaseException as _g:
                None
                if Std.isOfType(haxe_Exception.caught(_g).unwrap(),StopIteration):
                    self.has = False
                    self.x = None
                else:
                    raise _g
            self.checked = True
        return self.has

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.it = None
        _hx_o.x = None
        _hx_o.has = None
        _hx_o.checked = None
python_HaxeIterator._hx_class = python_HaxeIterator
_hx_classes["python.HaxeIterator"] = python_HaxeIterator


class python__KwArgs_KwArgs_Impl_:
    _hx_class_name = "python._KwArgs.KwArgs_Impl_"
    __slots__ = ()
    _hx_statics = ["fromT"]

    @staticmethod
    def fromT(d):
        this1 = python_Lib.anonAsDict(d)
        return this1
python__KwArgs_KwArgs_Impl_._hx_class = python__KwArgs_KwArgs_Impl_
_hx_classes["python._KwArgs.KwArgs_Impl_"] = python__KwArgs_KwArgs_Impl_


class python_Lib:
    _hx_class_name = "python.Lib"
    __slots__ = ()
    _hx_statics = ["lineEnd", "printString", "dictToAnon", "anonToDict", "anonAsDict"]

    @staticmethod
    def printString(_hx_str):
        encoding = "utf-8"
        if (encoding is None):
            encoding = "utf-8"
        python_lib_Sys.stdout.buffer.write(_hx_str.encode(encoding, "strict"))
        python_lib_Sys.stdout.flush()

    @staticmethod
    def dictToAnon(v):
        return _hx_AnonObject(v.copy())

    @staticmethod
    def anonToDict(o):
        if isinstance(o,_hx_AnonObject):
            return o.__dict__.copy()
        else:
            return None

    @staticmethod
    def anonAsDict(o):
        if isinstance(o,_hx_AnonObject):
            return o.__dict__
        else:
            return None
python_Lib._hx_class = python_Lib
_hx_classes["python.Lib"] = python_Lib


class python_internal_ArrayImpl:
    _hx_class_name = "python.internal.ArrayImpl"
    __slots__ = ()
    _hx_statics = ["concat", "copy", "iterator", "keyValueIterator", "indexOf", "lastIndexOf", "join", "toString", "pop", "push", "unshift", "remove", "contains", "shift", "slice", "sort", "splice", "map", "filter", "insert", "reverse", "_get", "_set"]

    @staticmethod
    def concat(a1,a2):
        return (a1 + a2)

    @staticmethod
    def copy(x):
        return list(x)

    @staticmethod
    def iterator(x):
        return python_HaxeIterator(x.__iter__())

    @staticmethod
    def keyValueIterator(x):
        return haxe_iterators_ArrayKeyValueIterator(x)

    @staticmethod
    def indexOf(a,x,fromIndex = None):
        _hx_len = len(a)
        l = (0 if ((fromIndex is None)) else ((_hx_len + fromIndex) if ((fromIndex < 0)) else fromIndex))
        if (l < 0):
            l = 0
        _g = l
        _g1 = _hx_len
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            if HxOverrides.eq(a[i],x):
                return i
        return -1

    @staticmethod
    def lastIndexOf(a,x,fromIndex = None):
        _hx_len = len(a)
        l = (_hx_len if ((fromIndex is None)) else (((_hx_len + fromIndex) + 1) if ((fromIndex < 0)) else (fromIndex + 1)))
        if (l > _hx_len):
            l = _hx_len
        while True:
            l = (l - 1)
            tmp = l
            if (not ((tmp > -1))):
                break
            if HxOverrides.eq(a[l],x):
                return l
        return -1

    @staticmethod
    def join(x,sep):
        return sep.join([python_Boot.toString1(x1,'') for x1 in x])

    @staticmethod
    def toString(x):
        return (("[" + HxOverrides.stringOrNull(",".join([python_Boot.toString1(x1,'') for x1 in x]))) + "]")

    @staticmethod
    def pop(x):
        if (len(x) == 0):
            return None
        else:
            return x.pop()

    @staticmethod
    def push(x,e):
        x.append(e)
        return len(x)

    @staticmethod
    def unshift(x,e):
        x.insert(0, e)

    @staticmethod
    def remove(x,e):
        try:
            x.remove(e)
            return True
        except BaseException as _g:
            None
            return False

    @staticmethod
    def contains(x,e):
        return (e in x)

    @staticmethod
    def shift(x):
        if (len(x) == 0):
            return None
        return x.pop(0)

    @staticmethod
    def slice(x,pos,end = None):
        return x[pos:end]

    @staticmethod
    def sort(x,f):
        x.sort(key= python_lib_Functools.cmp_to_key(f))

    @staticmethod
    def splice(x,pos,_hx_len):
        if (pos < 0):
            pos = (len(x) + pos)
        if (pos < 0):
            pos = 0
        res = x[pos:(pos + _hx_len)]
        del x[pos:(pos + _hx_len)]
        return res

    @staticmethod
    def map(x,f):
        return list(map(f,x))

    @staticmethod
    def filter(x,f):
        return list(filter(f,x))

    @staticmethod
    def insert(a,pos,x):
        a.insert(pos, x)

    @staticmethod
    def reverse(a):
        a.reverse()

    @staticmethod
    def _get(x,idx):
        if ((idx > -1) and ((idx < len(x)))):
            return x[idx]
        else:
            return None

    @staticmethod
    def _set(x,idx,v):
        l = len(x)
        while (l < idx):
            x.append(None)
            l = (l + 1)
        if (l == idx):
            x.append(v)
        else:
            x[idx] = v
        return v
python_internal_ArrayImpl._hx_class = python_internal_ArrayImpl
_hx_classes["python.internal.ArrayImpl"] = python_internal_ArrayImpl


class HxOverrides:
    _hx_class_name = "HxOverrides"
    __slots__ = ()
    _hx_statics = ["iterator", "eq", "stringOrNull", "pop", "toLowerCase", "rshift", "modf", "mod", "mapKwArgs"]

    @staticmethod
    def iterator(x):
        if isinstance(x,list):
            return haxe_iterators_ArrayIterator(x)
        return x.iterator()

    @staticmethod
    def eq(a,b):
        if (isinstance(a,list) or isinstance(b,list)):
            return a is b
        return (a == b)

    @staticmethod
    def stringOrNull(s):
        if (s is None):
            return "null"
        else:
            return s

    @staticmethod
    def pop(x):
        if isinstance(x,list):
            _this = x
            return (None if ((len(_this) == 0)) else _this.pop())
        return x.pop()

    @staticmethod
    def toLowerCase(x):
        if isinstance(x,str):
            return x.lower()
        return x.toLowerCase()

    @staticmethod
    def rshift(val,n):
        return ((val % 0x100000000) >> n)

    @staticmethod
    def modf(a,b):
        if (b == 0.0):
            return float('nan')
        elif (a < 0):
            if (b < 0):
                return -(-a % (-b))
            else:
                return -(-a % b)
        elif (b < 0):
            return a % (-b)
        else:
            return a % b

    @staticmethod
    def mod(a,b):
        if (a < 0):
            if (b < 0):
                return -(-a % (-b))
            else:
                return -(-a % b)
        elif (b < 0):
            return a % (-b)
        else:
            return a % b

    @staticmethod
    def mapKwArgs(a,v):
        a1 = _hx_AnonObject(python_Lib.anonToDict(a))
        k = python_HaxeIterator(iter(v.keys()))
        while k.hasNext():
            k1 = k.next()
            val = v.get(k1)
            if a1._hx_hasattr(k1):
                x = getattr(a1,k1)
                setattr(a1,val,x)
                delattr(a1,k1)
        return a1
HxOverrides._hx_class = HxOverrides
_hx_classes["HxOverrides"] = HxOverrides


class python_internal_MethodClosure:
    _hx_class_name = "python.internal.MethodClosure"
    __slots__ = ("obj", "func")
    _hx_fields = ["obj", "func"]
    _hx_methods = ["__call__"]

    def __init__(self,obj,func):
        self.obj = obj
        self.func = func

    def __call__(self,*args):
        return self.func(self.obj,*args)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.obj = None
        _hx_o.func = None
python_internal_MethodClosure._hx_class = python_internal_MethodClosure
_hx_classes["python.internal.MethodClosure"] = python_internal_MethodClosure


class HxString:
    _hx_class_name = "HxString"
    __slots__ = ()
    _hx_statics = ["split", "charCodeAt", "charAt", "lastIndexOf", "toUpperCase", "toLowerCase", "indexOf", "indexOfImpl", "toString", "substring", "substr"]

    @staticmethod
    def split(s,d):
        if (d == ""):
            return list(s)
        else:
            return s.split(d)

    @staticmethod
    def charCodeAt(s,index):
        if ((((s is None) or ((len(s) == 0))) or ((index < 0))) or ((index >= len(s)))):
            return None
        else:
            return ord(s[index])

    @staticmethod
    def charAt(s,index):
        if ((index < 0) or ((index >= len(s)))):
            return ""
        else:
            return s[index]

    @staticmethod
    def lastIndexOf(s,_hx_str,startIndex = None):
        if (startIndex is None):
            return s.rfind(_hx_str, 0, len(s))
        elif (_hx_str == ""):
            length = len(s)
            if (startIndex < 0):
                startIndex = (length + startIndex)
                if (startIndex < 0):
                    startIndex = 0
            if (startIndex > length):
                return length
            else:
                return startIndex
        else:
            i = s.rfind(_hx_str, 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len(_hx_str))) if ((i == -1)) else (i + 1))
            check = s.find(_hx_str, startLeft, len(s))
            if ((check > i) and ((check <= startIndex))):
                return check
            else:
                return i

    @staticmethod
    def toUpperCase(s):
        return s.upper()

    @staticmethod
    def toLowerCase(s):
        return s.lower()

    @staticmethod
    def indexOf(s,_hx_str,startIndex = None):
        if (startIndex is None):
            return s.find(_hx_str)
        else:
            return HxString.indexOfImpl(s,_hx_str,startIndex)

    @staticmethod
    def indexOfImpl(s,_hx_str,startIndex):
        if (_hx_str == ""):
            length = len(s)
            if (startIndex < 0):
                startIndex = (length + startIndex)
                if (startIndex < 0):
                    startIndex = 0
            if (startIndex > length):
                return length
            else:
                return startIndex
        return s.find(_hx_str, startIndex)

    @staticmethod
    def toString(s):
        return s

    @staticmethod
    def substring(s,startIndex,endIndex = None):
        if (startIndex < 0):
            startIndex = 0
        if (endIndex is None):
            return s[startIndex:]
        else:
            if (endIndex < 0):
                endIndex = 0
            if (endIndex < startIndex):
                return s[endIndex:startIndex]
            else:
                return s[startIndex:endIndex]

    @staticmethod
    def substr(s,startIndex,_hx_len = None):
        if (_hx_len is None):
            return s[startIndex:]
        else:
            if (_hx_len == 0):
                return ""
            if (startIndex < 0):
                startIndex = (len(s) + startIndex)
                if (startIndex < 0):
                    startIndex = 0
            return s[startIndex:(startIndex + _hx_len)]
HxString._hx_class = HxString
_hx_classes["HxString"] = HxString


class sys_net_Socket:
    _hx_class_name = "sys.net.Socket"
    __slots__ = ("_hx___s", "input", "output")
    _hx_fields = ["__s", "input", "output"]
    _hx_methods = ["__initSocket", "fileno"]

    def __init__(self):
        self.output = None
        self.input = None
        self._hx___s = None
        self._hx___initSocket()
        self.input = sys_net__Socket_SocketInput(self._hx___s)
        self.output = sys_net__Socket_SocketOutput(self._hx___s)

    def _hx___initSocket(self):
        self._hx___s = python_lib_socket_Socket()

    def fileno(self):
        return self._hx___s.fileno()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._hx___s = None
        _hx_o.input = None
        _hx_o.output = None
sys_net_Socket._hx_class = sys_net_Socket
_hx_classes["sys.net.Socket"] = sys_net_Socket


class python_net_SslSocket(sys_net_Socket):
    _hx_class_name = "python.net.SslSocket"
    __slots__ = ("hostName",)
    _hx_fields = ["hostName"]
    _hx_methods = ["__initSocket"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = sys_net_Socket


    def __init__(self):
        self.hostName = None
        super().__init__()

    def _hx___initSocket(self):
        context = python_lib_ssl_SSLContext(python_lib_Ssl.PROTOCOL_SSLv23)
        context.verify_mode = python_lib_Ssl.CERT_REQUIRED
        context.set_default_verify_paths()
        context.options = (context.options | python_lib_Ssl.OP_NO_SSLv2)
        context.options = (context.options | python_lib_Ssl.OP_NO_SSLv3)
        context.options = (context.options | python_lib_Ssl.OP_NO_COMPRESSION)
        context.options = (context.options | python_lib_Ssl.OP_NO_TLSv1)
        self._hx___s = python_lib_socket_Socket()
        self._hx___s = context.wrap_socket(self._hx___s,False,True,True,self.hostName)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.hostName = None
python_net_SslSocket._hx_class = python_net_SslSocket
_hx_classes["python.net.SslSocket"] = python_net_SslSocket


class sys_io_File:
    _hx_class_name = "sys.io.File"
    __slots__ = ()
    _hx_statics = ["getContent", "saveContent"]

    @staticmethod
    def getContent(path):
        f = python_lib_Builtins.open(path,"r",-1,"utf-8",None,"")
        content = f.read(-1)
        f.close()
        return content

    @staticmethod
    def saveContent(path,content):
        f = python_lib_Builtins.open(path,"w",-1,"utf-8",None,"")
        f.write(content)
        f.close()
sys_io_File._hx_class = sys_io_File
_hx_classes["sys.io.File"] = sys_io_File


class sys_net__Socket_SocketInput(haxe_io_Input):
    _hx_class_name = "sys.net._Socket.SocketInput"
    __slots__ = ("_hx___s",)
    _hx_fields = ["__s"]
    _hx_methods = []
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_io_Input


    def __init__(self,s):
        self._hx___s = s

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._hx___s = None
sys_net__Socket_SocketInput._hx_class = sys_net__Socket_SocketInput
_hx_classes["sys.net._Socket.SocketInput"] = sys_net__Socket_SocketInput


class sys_net__Socket_SocketOutput(haxe_io_Output):
    _hx_class_name = "sys.net._Socket.SocketOutput"
    __slots__ = ("_hx___s",)
    _hx_fields = ["__s"]
    _hx_methods = []
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_io_Output


    def __init__(self,s):
        self._hx___s = s

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o._hx___s = None
sys_net__Socket_SocketOutput._hx_class = sys_net__Socket_SocketOutput
_hx_classes["sys.net._Socket.SocketOutput"] = sys_net__Socket_SocketOutput


class sys_thread_EventLoop:
    _hx_class_name = "sys.thread.EventLoop"
    __slots__ = ("mutex", "oneTimeEvents", "oneTimeEventsIdx", "waitLock", "promisedEventsCount", "regularEvents")
    _hx_fields = ["mutex", "oneTimeEvents", "oneTimeEventsIdx", "waitLock", "promisedEventsCount", "regularEvents"]
    _hx_methods = ["repeat", "cancel", "loop"]

    def __init__(self):
        self.regularEvents = None
        self.promisedEventsCount = 0
        self.waitLock = sys_thread_Lock()
        self.oneTimeEventsIdx = 0
        self.oneTimeEvents = list()
        self.mutex = sys_thread_Mutex()

    def repeat(self,event,intervalMs):
        self.mutex.lock.acquire(True)
        interval = (0.001 * intervalMs)
        event1 = sys_thread__EventLoop_RegularEvent(event,(python_lib_Time.time() + interval),interval)
        _g = self.regularEvents
        if (_g is not None):
            current = _g
            event1.next = current
            current.previous = event1
        self.regularEvents = event1
        self.waitLock.semaphore.release()
        self.mutex.lock.release()
        return event1

    def cancel(self,eventHandler):
        self.mutex.lock.acquire(True)
        event = eventHandler
        if (self.regularEvents == event):
            self.regularEvents = event.next
        _g = event.next
        if (_g is not None):
            e = _g
            e.previous = event.previous
        _g = event.previous
        if (_g is not None):
            e = _g
            e.next = event.next
        self.mutex.lock.release()

    def loop(self):
        events = []
        while True:
            now = python_lib_Time.time()
            eventsToRun = events
            eventsToRunIdx = 0
            nextEventAt = -1
            self.mutex.lock.acquire(True)
            while self.waitLock.semaphore.acquire(True,0.0):
                pass
            current = self.regularEvents
            while (current is not None):
                if (current.nextRunTime <= now):
                    tmp = eventsToRunIdx
                    eventsToRunIdx = (eventsToRunIdx + 1)
                    python_internal_ArrayImpl._set(eventsToRun, tmp, current.run)
                    current.nextRunTime = (current.nextRunTime + current.interval)
                    nextEventAt = -2
                elif ((nextEventAt == -1) or ((current.nextRunTime < nextEventAt))):
                    nextEventAt = current.nextRunTime
                current = current.next
            self.mutex.lock.release()
            _g = 0
            _g1 = eventsToRunIdx
            while (_g < _g1):
                i = _g
                _g = (_g + 1)
                (eventsToRun[i] if i >= 0 and i < len(eventsToRun) else None)()
                python_internal_ArrayImpl._set(eventsToRun, i, None)
            eventsToRunIdx = 0
            self.mutex.lock.acquire(True)
            _g2_current = 0
            _g2_array = self.oneTimeEvents
            while (_g2_current < len(_g2_array)):
                _g3_value = (_g2_array[_g2_current] if _g2_current >= 0 and _g2_current < len(_g2_array) else None)
                _g3_key = _g2_current
                _g2_current = (_g2_current + 1)
                i1 = _g3_key
                event = _g3_value
                if (event is None):
                    break
                else:
                    tmp1 = eventsToRunIdx
                    eventsToRunIdx = (eventsToRunIdx + 1)
                    python_internal_ArrayImpl._set(eventsToRun, tmp1, event)
                    python_internal_ArrayImpl._set(self.oneTimeEvents, i1, None)
            self.oneTimeEventsIdx = 0
            hasPromisedEvents = (self.promisedEventsCount > 0)
            self.mutex.lock.release()
            _g2 = 0
            _g3 = eventsToRunIdx
            while (_g2 < _g3):
                i2 = _g2
                _g2 = (_g2 + 1)
                (eventsToRun[i2] if i2 >= 0 and i2 < len(eventsToRun) else None)()
                python_internal_ArrayImpl._set(eventsToRun, i2, None)
            if (eventsToRunIdx > 0):
                nextEventAt = -2
            r_nextEventAt = nextEventAt
            r_anyTime = hasPromisedEvents
            _g4 = r_anyTime
            _g5 = r_nextEventAt
            _g6 = _g5
            if (_g6 == -2):
                pass
            elif (_g6 == -1):
                if _g4:
                    self.waitLock.semaphore.acquire(True,None)
                else:
                    break
            else:
                time = _g5
                timeout = (time - python_lib_Time.time())
                _this = self.waitLock
                timeout1 = (0 if (python_lib_Math.isnan(0)) else (timeout if (python_lib_Math.isnan(timeout)) else max(0,timeout)))
                _this.semaphore.acquire(True,timeout1)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.mutex = None
        _hx_o.oneTimeEvents = None
        _hx_o.oneTimeEventsIdx = None
        _hx_o.waitLock = None
        _hx_o.promisedEventsCount = None
        _hx_o.regularEvents = None
sys_thread_EventLoop._hx_class = sys_thread_EventLoop
_hx_classes["sys.thread.EventLoop"] = sys_thread_EventLoop


class sys_thread__EventLoop_RegularEvent:
    _hx_class_name = "sys.thread._EventLoop.RegularEvent"
    __slots__ = ("nextRunTime", "interval", "run", "next", "previous")
    _hx_fields = ["nextRunTime", "interval", "run", "next", "previous"]

    def __init__(self,run,nextRunTime,interval):
        self.previous = None
        self.next = None
        self.run = run
        self.nextRunTime = nextRunTime
        self.interval = interval

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.nextRunTime = None
        _hx_o.interval = None
        _hx_o.run = None
        _hx_o.next = None
        _hx_o.previous = None
sys_thread__EventLoop_RegularEvent._hx_class = sys_thread__EventLoop_RegularEvent
_hx_classes["sys.thread._EventLoop.RegularEvent"] = sys_thread__EventLoop_RegularEvent


class sys_thread_Lock:
    _hx_class_name = "sys.thread.Lock"
    __slots__ = ("semaphore",)
    _hx_fields = ["semaphore"]

    def __init__(self):
        self.semaphore = Lock(0)

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.semaphore = None
sys_thread_Lock._hx_class = sys_thread_Lock
_hx_classes["sys.thread.Lock"] = sys_thread_Lock


class sys_thread_Mutex:
    _hx_class_name = "sys.thread.Mutex"
    __slots__ = ("lock",)
    _hx_fields = ["lock"]

    def __init__(self):
        self.lock = sys_thread__Mutex_NativeRLock()

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.lock = None
sys_thread_Mutex._hx_class = sys_thread_Mutex
_hx_classes["sys.thread.Mutex"] = sys_thread_Mutex


class sys_thread_NoEventLoopException(haxe_Exception):
    _hx_class_name = "sys.thread.NoEventLoopException"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = []
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_Exception


    def __init__(self,msg = None,previous = None):
        if (msg is None):
            msg = "Event loop is not available. Refer to sys.thread.Thread.runWithEventLoop."
        super().__init__(msg,previous)
sys_thread_NoEventLoopException._hx_class = sys_thread_NoEventLoopException
_hx_classes["sys.thread.NoEventLoopException"] = sys_thread_NoEventLoopException


class sys_thread__Thread_Thread_Impl_:
    _hx_class_name = "sys.thread._Thread.Thread_Impl_"
    __slots__ = ()
    _hx_statics = ["get_events", "processEvents"]
    events = None

    @staticmethod
    def get_events(this1):
        if (this1.events is None):
            raise sys_thread_NoEventLoopException()
        return this1.events

    @staticmethod
    def processEvents():
        sys_thread__Thread_HxThread.current().events.loop()
sys_thread__Thread_Thread_Impl_._hx_class = sys_thread__Thread_Thread_Impl_
_hx_classes["sys.thread._Thread.Thread_Impl_"] = sys_thread__Thread_Thread_Impl_


class sys_thread__Thread_HxThread:
    _hx_class_name = "sys.thread._Thread.HxThread"
    __slots__ = ("events", "nativeThread")
    _hx_fields = ["events", "nativeThread"]
    _hx_statics = ["threads", "threadsMutex", "mainThread", "current"]

    def __init__(self,t):
        self.events = None
        self.nativeThread = t
    threads = None
    threadsMutex = None
    mainThread = None

    @staticmethod
    def current():
        sys_thread__Thread_HxThread.threadsMutex.lock.acquire(True)
        ct = threading.current_thread()
        if (ct == threading.main_thread()):
            sys_thread__Thread_HxThread.threadsMutex.lock.release()
            return sys_thread__Thread_HxThread.mainThread
        if (not (ct in sys_thread__Thread_HxThread.threads.h)):
            sys_thread__Thread_HxThread.threads.set(ct,sys_thread__Thread_HxThread(ct))
        t = sys_thread__Thread_HxThread.threads.h.get(ct,None)
        sys_thread__Thread_HxThread.threadsMutex.lock.release()
        return t

    @staticmethod
    def _hx_empty_init(_hx_o):
        _hx_o.events = None
        _hx_o.nativeThread = None
sys_thread__Thread_HxThread._hx_class = sys_thread__Thread_HxThread
_hx_classes["sys.thread._Thread.HxThread"] = sys_thread__Thread_HxThread


class thx_semver__Version_Version_Impl_:
    _hx_class_name = "thx.semver._Version.Version_Impl_"
    __slots__ = ()
    _hx_statics = ["VERSION", "stringToVersion", "equals", "greaterThan", "greaterThanOrEqual", "lessThan", "lessThanOrEqual", "parseIdentifiers", "parseIdentifier", "equalsIdentifiers", "greaterThanIdentifiers", "SANITIZER", "sanitize"]

    @staticmethod
    def stringToVersion(s):
        _this = thx_semver__Version_Version_Impl_.VERSION
        _this.matchObj = python_lib_Re.search(_this.pattern,s)
        if (_this.matchObj is None):
            raise haxe_Exception.thrown((("Invalid SemVer format for \"" + ("null" if s is None else s)) + "\""))
        major = Std.parseInt(thx_semver__Version_Version_Impl_.VERSION.matchObj.group(1))
        minor = Std.parseInt(thx_semver__Version_Version_Impl_.VERSION.matchObj.group(2))
        patch = Std.parseInt(thx_semver__Version_Version_Impl_.VERSION.matchObj.group(3))
        pre = thx_semver__Version_Version_Impl_.parseIdentifiers(thx_semver__Version_Version_Impl_.VERSION.matchObj.group(4))
        build = thx_semver__Version_Version_Impl_.parseIdentifiers(thx_semver__Version_Version_Impl_.VERSION.matchObj.group(5))
        this1 = _hx_AnonObject({'version': [major, minor, patch], 'pre': pre, 'build': build})
        return this1

    @staticmethod
    def equals(this1,other):
        if (((python_internal_ArrayImpl._get(this1.version, 0) != python_internal_ArrayImpl._get(other.version, 0)) or ((python_internal_ArrayImpl._get(this1.version, 1) != python_internal_ArrayImpl._get(other.version, 1)))) or ((python_internal_ArrayImpl._get(this1.version, 2) != python_internal_ArrayImpl._get(other.version, 2)))):
            return False
        return thx_semver__Version_Version_Impl_.equalsIdentifiers(this1.pre,other.pre)

    @staticmethod
    def greaterThan(this1,other):
        if ((len(this1.pre) > 0) and ((len(other.pre) > 0))):
            if (((python_internal_ArrayImpl._get(this1.version, 0) == python_internal_ArrayImpl._get(other.version, 0)) and ((python_internal_ArrayImpl._get(this1.version, 1) == python_internal_ArrayImpl._get(other.version, 1)))) and ((python_internal_ArrayImpl._get(this1.version, 2) == python_internal_ArrayImpl._get(other.version, 2)))):
                return thx_semver__Version_Version_Impl_.greaterThanIdentifiers(this1.pre,other.pre)
            else:
                return False
        elif (len(other.pre) > 0):
            if (python_internal_ArrayImpl._get(this1.version, 0) != python_internal_ArrayImpl._get(other.version, 0)):
                return (python_internal_ArrayImpl._get(this1.version, 0) > python_internal_ArrayImpl._get(other.version, 0))
            if (python_internal_ArrayImpl._get(this1.version, 1) != python_internal_ArrayImpl._get(other.version, 1)):
                return (python_internal_ArrayImpl._get(this1.version, 1) > python_internal_ArrayImpl._get(other.version, 1))
            if (python_internal_ArrayImpl._get(this1.version, 2) != python_internal_ArrayImpl._get(other.version, 2)):
                return (python_internal_ArrayImpl._get(this1.version, 2) > python_internal_ArrayImpl._get(other.version, 2))
            if (len(this1.pre) > 0):
                return thx_semver__Version_Version_Impl_.greaterThanIdentifiers(this1.pre,other.pre)
            else:
                return True
        elif (len(this1.pre) <= 0):
            if (python_internal_ArrayImpl._get(this1.version, 0) != python_internal_ArrayImpl._get(other.version, 0)):
                return (python_internal_ArrayImpl._get(this1.version, 0) > python_internal_ArrayImpl._get(other.version, 0))
            if (python_internal_ArrayImpl._get(this1.version, 1) != python_internal_ArrayImpl._get(other.version, 1)):
                return (python_internal_ArrayImpl._get(this1.version, 1) > python_internal_ArrayImpl._get(other.version, 1))
            if (python_internal_ArrayImpl._get(this1.version, 2) != python_internal_ArrayImpl._get(other.version, 2)):
                return (python_internal_ArrayImpl._get(this1.version, 2) > python_internal_ArrayImpl._get(other.version, 2))
            return thx_semver__Version_Version_Impl_.greaterThanIdentifiers(this1.pre,other.pre)
        else:
            return False

    @staticmethod
    def greaterThanOrEqual(this1,other):
        if (not thx_semver__Version_Version_Impl_.equals(this1,other)):
            return thx_semver__Version_Version_Impl_.greaterThan(this1,other)
        else:
            return True

    @staticmethod
    def lessThan(this1,other):
        return (not thx_semver__Version_Version_Impl_.greaterThanOrEqual(this1,other))

    @staticmethod
    def lessThanOrEqual(this1,other):
        return (not thx_semver__Version_Version_Impl_.greaterThan(this1,other))

    @staticmethod
    def parseIdentifiers(s):
        _this = ("" if ((None == s)) else s)
        def _hx_local_1():
            def _hx_local_0(s):
                return (s != "")
            return list(map(thx_semver__Version_Version_Impl_.parseIdentifier,list(filter(_hx_local_0,list(map(thx_semver__Version_Version_Impl_.sanitize,_this.split(".")))))))
        return _hx_local_1()

    @staticmethod
    def parseIdentifier(s):
        i = Std.parseInt(s)
        if (None == i):
            return thx_semver_Identifier.StringId(s)
        else:
            return thx_semver_Identifier.IntId(i)

    @staticmethod
    def equalsIdentifiers(a,b):
        if (len(a) != len(b)):
            return False
        _g = 0
        _g1 = len(a)
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            _g2 = (a[i] if i >= 0 and i < len(a) else None)
            _g3 = (b[i] if i >= 0 and i < len(b) else None)
            tmp = _g2.index
            if (tmp == 0):
                if (_g3.index == 0):
                    b1 = _g3.params[0]
                    a1 = _g2.params[0]
                    if (a1 != b1):
                        return False
            elif (tmp == 1):
                if (_g3.index == 1):
                    b2 = _g3.params[0]
                    a2 = _g2.params[0]
                    if (a2 != b2):
                        return False
            else:
                pass
        return True

    @staticmethod
    def greaterThanIdentifiers(a,b):
        _g = 0
        _g1 = len(a)
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            _g2 = (a[i] if i >= 0 and i < len(a) else None)
            _g3 = (b[i] if i >= 0 and i < len(b) else None)
            tmp = _g2.index
            if (tmp == 0):
                _g4 = _g2.params[0]
                tmp1 = _g3.index
                if (tmp1 == 0):
                    _g5 = _g3.params[0]
                    b1 = _g5
                    a1 = _g4
                    if (a1 == b1):
                        continue
                    else:
                        b2 = _g5
                        a2 = _g4
                        if (a2 > b2):
                            return True
                        else:
                            return False
                elif (tmp1 == 1):
                    _g6 = _g3.params[0]
                    return True
                else:
                    return False
            elif (tmp == 1):
                _g7 = _g2.params[0]
                if (_g3.index == 1):
                    _g8 = _g3.params[0]
                    b3 = _g8
                    a3 = _g7
                    if (a3 == b3):
                        continue
                    else:
                        b4 = _g8
                        a4 = _g7
                        if (a4 > b4):
                            return True
                        else:
                            return False
                else:
                    return False
            else:
                return False
        return False

    @staticmethod
    def sanitize(s):
        return thx_semver__Version_Version_Impl_.SANITIZER.replace(s,"")
thx_semver__Version_Version_Impl_._hx_class = thx_semver__Version_Version_Impl_
_hx_classes["thx.semver._Version.Version_Impl_"] = thx_semver__Version_Version_Impl_

class thx_semver_Identifier(Enum):
    __slots__ = ()
    _hx_class_name = "thx.semver.Identifier"
    _hx_constructs = ["StringId", "IntId"]

    @staticmethod
    def StringId(value):
        return thx_semver_Identifier("StringId", 0, (value,))

    @staticmethod
    def IntId(value):
        return thx_semver_Identifier("IntId", 1, (value,))
thx_semver_Identifier._hx_class = thx_semver_Identifier
_hx_classes["thx.semver.Identifier"] = thx_semver_Identifier

Math.NEGATIVE_INFINITY = float("-inf")
Math.POSITIVE_INFINITY = float("inf")
Math.NaN = float("nan")
Math.PI = python_lib_Math.pi
sys_thread__Thread_HxThread.threads = haxe_ds_ObjectMap()
sys_thread__Thread_HxThread.threadsMutex = sys_thread_Mutex()
sys_thread__Thread_HxThread.mainThread = sys_thread__Thread_HxThread(threading.current_thread())
sys_thread__Thread_HxThread.mainThread.events = sys_thread_EventLoop()

apptimize_util_ABTDataLock.SYSTEM_DATA_LOCK = apptimize_util_ABTDataLock.getNewLock("system_data_lock")
apptimize_util_ABTDataLock.METADATA_LOCK = apptimize_util_ABTDataLock.getNewLock("meta_data_lock")
apptimize_util_ABTDataLock.CHECK_TIME_LOCK = apptimize_util_ABTDataLock.getNewLock("last_check_time_lock")
apptimize_util_ABTDataLock.INITIALIZATION = apptimize_util_ABTDataLock.getNewLock("initialize_lock")
apptimize_ABTDataStore.resultsLock = apptimize_util_ABTDataLock.getNewLock("datastore_results_lock")
apptimize_ABTLogger.LOG_LEVEL_VERBOSE = 0
apptimize_ABTLogger.LOG_LEVEL_DEBUG = 1
apptimize_ABTLogger.LOG_LEVEL_INFO = 2
apptimize_ABTLogger.LOG_LEVEL_WARN = 3
apptimize_ABTLogger.LOG_LEVEL_ERROR = 4
apptimize_ABTLogger.LOG_LEVEL_NONE = 5
apptimize_ABTLogger.logLevel = apptimize_ABTLogger.LOG_LEVEL_VERBOSE
apptimize_ABTLogger.useTraceForLogging = False
apptimize_ApptimizeInternal.kABTEventSourceApptimize = "a"
apptimize_ApptimizeInternal.kABTValueEventKey = "value"
apptimize_ApptimizeInternal._state = 0
apptimize_api_ABTApiResultsPost.MAX_FAILURE_DELAY_MS = 60000
apptimize_api_ABTApiResultsPost.DEFAULT_FAILURE_DELAY_MS = 1000
def _hx_init_apptimize_api_ABTApiResultsPost__failureDelayMs():
    def _hx_local_0():
        val = apptimize_api_ABTApiResultsPost.DEFAULT_FAILURE_DELAY_MS
        if (val is None):
            val = 0
        this1 = hx_concurrent_atomic__AtomicInt_AtomicIntImpl(val)
        return this1
    return _hx_local_0()
apptimize_api_ABTApiResultsPost._failureDelayMs = _hx_init_apptimize_api_ABTApiResultsPost__failureDelayMs()
apptimize_api_ABTApiResultsPost._pendingMap = haxe_ds_StringMap()
apptimize_api_ABTApiResultsPost._pendingResults = hx_concurrent_collection__SynchronizedLinkedList_SynchronizedLinkedList_Impl_._new()
apptimize_api_ABTApiResultsPost._postDispatch = apptimize_util_ABTDispatch("Results Post Dispatch Queue")
apptimize_api_ABTApiResultsPost._loadedPending = False
apptimize_api_ABTApiResultsPost.PENDING_LOCK = apptimize_util_ABTDataLock.getNewLock("pending_results_key")
apptimize_filter_ABTFilter.kABTFilterKeyValue = "value"
apptimize_filter_ABTFilter.kABTFilterKeyType = "type"
apptimize_filter_ABTFilter.kABTFilterKeyProperty = "property"
apptimize_filter_ABTFilter.kABTFilterKeyOperator = "operator"
apptimize_filter_ABTFilter.kABTFilterKeyPropertySource = "propertySource"
apptimize_filter_ABTFilter.kABTFilterKeyCallServerInputs = "callServerInputs"
apptimize_filter_ABTFilter.kABTFilterKeyCallURLKey = "callServerUrlKey"
apptimize_filter_ABTFilter.kABTFilterKeyUserAttribute = "userAttribute"
apptimize_filter_ABTFilter.kABTFilterKeyPrefixedAttribute = "prefixedAttribute"
apptimize_filter_ABTFilter.kABTFilterKeyNamedFilter = "namedFilter"
apptimize_filter_ABTFilterUtils.__meta__ = _hx_AnonObject({'statics': _hx_AnonObject({'ABTEvaluateString': _hx_AnonObject({'static': None}), 'ABTEvaluateBool': _hx_AnonObject({'static': None}), 'ABTEvaluateNumber': _hx_AnonObject({'static': None})})})
apptimize_models_results_ABTResultEntry.RESULT_ENTRY_CREATION_LOCK = apptimize_util_ABTDataLock.getNewLock("result_entry_creation_lock_key")
apptimize_support_persistence_ABTPersistence.LOW_LATENCY = 0
apptimize_support_persistence_ABTPersistence.HIGH_LATENCY = 1
apptimize_support_persistence_ABTPersistence.ALL_LATENCY = 2
apptimize_support_persistence_ABTPersistence.kMetadataKey = "METADATA_KEY"
apptimize_support_persistence_ABTPersistence.kUserIDKey = "USER_ID_KEY"
apptimize_support_persistence_ABTPersistence.kAnonymousGuidKey = "ANONYMOUS_GUID_KEY"
apptimize_support_persistence_ABTPersistence.kCustomPropertiesKey = "CUSTOM_PROPERTIES_KEY"
apptimize_support_persistence_ABTPersistence.kInternalPropertiesKey = "INTERNAL_PROPERTIES_KEY"
apptimize_support_persistence_ABTPersistence.kResultLogsKey = "RESULT_LOGS_KEY"
apptimize_support_persistence_ABTPersistence.kResultPostsKey = "RESULT_POSTS_KEY"
apptimize_support_persistence_ABTPersistence.kResultPostsListKey = "RESULT_POSTS_LIST_KEY"
apptimize_support_persistence_ABTPersistence.kResultEntrySequenceKey = "RESULT_ENTRY_SEQUENCE_KEY"
apptimize_support_persistence_ABTPersistence.kResultEntryTimestampKey = "RESULT_ENTRY_TIMESTAMP_KEY"
apptimize_support_persistence_ABTPersistence.kApptimizeVersionKey = "APPTIMIZE_VERSION_KEY"
apptimize_support_persistence_ABTPersistence.kLockAccessKey = "LOCK_ACCESS_KEY"
apptimize_support_persistence_ABTPersistence.kPostManagementKey = "POST_MANAGEMENT_KEY"
apptimize_support_persistence_ABTPersistence.kResultLastSubmitTimeKey = "RESULT_LAST_SUBMIT_TIME_KEY"
apptimize_support_persistence_ABTPersistence.kMetadataLastCheckTimeKey = "METADATA_LAST_CHECK_TIME_KEY"
apptimize_support_persistence_ABTPersistence.kDisabledVersions = "DISABLED_VERSIONS_KEY"
apptimize_support_properties_ABTApplicationProperties._sigilForApplicationNamespace = "$"
apptimize_support_properties_ABTConfigProperties.META_DATA_URL_KEY = "meta_data_url"
apptimize_support_properties_ABTConfigProperties.META_DATA_URL_LL_KEY = "meta_data_ll_url"
apptimize_support_properties_ABTConfigProperties.META_DATA_URL_HL_KEY = "meta_data_hl_url"
apptimize_support_properties_ABTConfigProperties.LOG_LEVEL_KEY = "log_level"
apptimize_support_properties_ABTConfigProperties.FOREGROUND_PERIOD_MS_KEY = "foreground_period_ms"
apptimize_support_properties_ABTConfigProperties.RESULT_POST_DELAY_MS_KEY = "result_post_delay_ms"
apptimize_support_properties_ABTConfigProperties.THREADING_ENABLED_KEY = "threading_enabled"
apptimize_support_properties_ABTConfigProperties.RESULT_POST_THREAD_POOL_SIZE_KEY = "result_post_thread_pool_size"
apptimize_support_properties_ABTConfigProperties.ALTERATION_CACHE_SIZE_KEY = "alteration_cache_size"
apptimize_support_properties_ABTConfigProperties.RESULTS_CACHE_SIZE_KEY = "results_cache_size"
apptimize_support_properties_ABTConfigProperties.MAXIMUM_RESULT_ENTRIES_KEY = "maximum_result_entries"
apptimize_support_properties_ABTConfigProperties.MAXIMUM_PENDING_RESULTS_KEY = "maximum_pending_results"
apptimize_support_properties_ABTConfigProperties.METADATA_POLLING_INTERVAL_MS_KEY = "metadata_polling_interval_ms"
apptimize_support_properties_ABTConfigProperties.METADATA_POLLING_BACKGROUND_INTERVAL_MS_KEY = "metadata_polling_background_interval_ms"
apptimize_support_properties_ABTConfigProperties.EXCEPTIONS_ENABLED_KEY = "exceptions_enabled"
apptimize_support_properties_ABTConfigProperties.MAXIMUM_RESULT_POST_FAILURE_KEY = "maximum_result_failures"
apptimize_support_properties_ABTConfigProperties.MAXIMUM_RESULT_POST_SENDER_TIMEOUT_MS_KEY = "maximum_result_post_sender_timeout_ms"
apptimize_support_properties_ABTConfigProperties.STORAGE_TYPE_KEY = "storage_type"
apptimize_support_properties_ABTConfigProperties.AUTOMATIC_SHUTDOWN_HOOK = "automatic_shutdown_hook"
apptimize_support_properties_ABTConfigProperties.APPTIMIZE_ENVIRONMENT_KEY = "apptimize_environment"
apptimize_support_properties_ABTConfigProperties.APPTIMIZE_REGION_KEY = "apptimize_region"
apptimize_support_properties_ABTConfigProperties.COMPRESS_PERSISTENCE_STORE_KEY = "compress_persistence_store"
apptimize_support_properties_ABTConfigProperties.GROUPS_BASE_URL_KEY = "groups_base_url"
apptimize_support_properties_ABTConfigProperties.REACT_NATIVE_STORAGE_KEY = "react_native_storage"
apptimize_support_properties_ABTConfigProperties.LOCAL_DISK_STORAGE_PATH_KEY = "local_disk_storage_path"
haxe_Serializer.USE_CACHE = False
haxe_Serializer.USE_ENUM_INDEX = False
haxe_Serializer.BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789%:"
haxe_Serializer.BASE64_CODES = None
haxe_Unserializer.DEFAULT_RESOLVER = haxe__Unserializer_DefaultResolver()
haxe_Unserializer.BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789%:"
haxe_Unserializer.CODES = None
def _hx_init_hx_concurrent_ServiceBase__ids():
    def _hx_local_0():
        this1 = hx_concurrent_atomic__AtomicInt_AtomicIntImpl(0)
        return this1
    return _hx_local_0()
hx_concurrent_ServiceBase._ids = _hx_init_hx_concurrent_ServiceBase__ids()
hx_concurrent_executor_Executor.NOW_ONCE = hx_concurrent_executor_Schedule.ONCE(0)
def _hx_init_hx_concurrent_thread_ThreadPool__threadIDs():
    def _hx_local_0():
        this1 = hx_concurrent_atomic__AtomicInt_AtomicIntImpl(0)
        return this1
    return _hx_local_0()
hx_concurrent_thread_ThreadPool._threadIDs = _hx_init_hx_concurrent_thread_ThreadPool__threadIDs()
pako_Inflate.DEFAULT_OPTIONS = _hx_AnonObject({'chunkSize': 16384, 'windowBits': 0, 'raw': False, 'dictionary': None})
pako_zlib_CRC32.crcTable = pako_zlib_CRC32.makeTable()
pako_zlib_InfTrees.MAXBITS = 15
pako_zlib_InfTrees.ENOUGH_LENS = 852
pako_zlib_InfTrees.ENOUGH_DISTS = 592
pako_zlib_InfTrees.CODES = 0
pako_zlib_InfTrees.LENS = 1
pako_zlib_InfTrees.DISTS = 2
pako_zlib_InfTrees.lbase = haxe_io__UInt16Array_UInt16Array_Impl_.fromArray([3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258, 0, 0])
pako_zlib_InfTrees.lext = haxe_io__UInt16Array_UInt16Array_Impl_.fromArray([16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 18, 18, 18, 18, 19, 19, 19, 19, 20, 20, 20, 20, 21, 21, 21, 21, 16, 72, 78])
pako_zlib_InfTrees.dbase = haxe_io__UInt16Array_UInt16Array_Impl_.fromArray([1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577, 0, 0])
pako_zlib_InfTrees.dext = haxe_io__UInt16Array_UInt16Array_Impl_.fromArray([16, 16, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 64, 64])
pako_zlib_Inflate.virgin = True
pako_zlib_Inflate.lenfix = None
pako_zlib_Inflate.distfix = None
def _hx_init_pako_zlib_Messages_map():
    def _hx_local_0():
        _g = haxe_ds_IntMap()
        _g.set(2,"need dictionary")
        _g.set(1,"stream end")
        _g.set(0,"")
        _g.set(-1,"file error")
        _g.set(-2,"stream error")
        _g.set(-3,"data error")
        _g.set(-4,"insufficient memory")
        _g.set(-5,"buffer error")
        _g.set(-6,"incompatible version")
        return _g
    return _hx_local_0()
pako_zlib_Messages.map = _hx_init_pako_zlib_Messages_map()
python_Boot.keywords = set(["and", "del", "from", "not", "with", "as", "elif", "global", "or", "yield", "assert", "else", "if", "pass", "None", "break", "except", "import", "raise", "True", "class", "exec", "in", "return", "False", "continue", "finally", "is", "try", "def", "for", "lambda", "while"])
python_Boot.prefixLength = len("_hx_")
python_Lib.lineEnd = ("\r\n" if ((Sys.systemName() == "Windows")) else "\n")
thx_semver__Version_Version_Impl_.VERSION = EReg("^(\\d+)\\.(\\d+)\\.(\\d+)(?:[-]([a-z0-9.-]+))?(?:[+]([a-z0-9.-]+))?$","i")
thx_semver__Version_Version_Impl_.SANITIZER = EReg("[^0-9A-Za-z-]","g")