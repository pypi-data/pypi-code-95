import connexion
import six

from swagger_server.models.bearer_token import BearerToken  # noqa: E501
from swagger_server import util

from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

import json
import pprint

import base64
import datetime


def obtain(userName, role, acGroups):  # noqa: E501
    """Obatin a token

    Given credentials get a bearer token # noqa: E501

    :param userName: Name Of User
    :type userName: str
    :param role: Role Of User
    :type role: str
    :param acGroups: Access Control Groups
    :type acGroups: str

    :rtype: BearerToken
    """

    tokenAsStr = jwtPlainOutStr(
        userName=userName,
        role=role,
        acGroups=acGroups,
    )


    bearerTokenDict = {}
    bearerTokenDict['id'] = str(tokenAsStr)

    now = datetime.datetime.now()
    delta = datetime.timedelta(hours = 8)
    nowPlusDelta = now + delta
    

    bearerTokenDict['issuedAt'] = now.strftime("%Y%m%d%H%M%S")    
    bearerTokenDict['expiredAt'] = nowPlusDelta.strftime("%Y%m%d%H%M%S")

    responseDict = {}
    responseDict['data'] = bearerTokenDict

    return responseDict


def jwtPlainOutStr(
        userName,
        role,
        acGroups,
):

    outBearerToken = BearerToken()
    outUserInfo = BearerTokenUserInfo()

    if userName: outUserInfo.setUserName(userName)
    if role: outUserInfo.setRole(role)
    if acGroups: outUserInfo.setResGroupIds(acGroups)
    
    outBearerToken.setUserInfo(outUserInfo)

    bearerTokenStr = outBearerToken.encodeAsJsonStr()

    base64Str = base64.standard_b64encode(
        bearerTokenStr.encode('utf-8')
    )

    return base64Str


class BearerToken(object):
     _expiredAt = None
     _issuedAt = None
     _userInfo = None  # BearerTokenUserInfo
     _userInfoDict = None

     def __init__(self):
         pass

     def initFromJsonStr(
             self,
             jsonStr,
             ):
         """
         """
         jsonData = json.loads(jsonStr)
         
         pp = pprint.PrettyPrinter(indent=4)    

         self.__class__._userInfoDict = jsonData['userInfo']

         userInfo = BearerTokenUserInfo(jsonData['userInfo'])

         self.setUserInfo(userInfo)

     def encodeAsJsonStr(
             self,
             ):
         """
         """
         tokenDict = self.selfAsDict()

         pp = pprint.PrettyPrinter(indent=4)    
         #icm.LOG_here(pp.pformat(tokenDict))

         tokenStr = json.dumps(tokenDict)

         return( tokenStr )


     def selfAsDict(self):
         selfDict={}

         def setKeyVal(key, value):
             if value:
                 selfDict[key] = value
         
         thisValue = self.getExpiredAt()
         thisKey = 'expiredAt'
         setKeyVal(thisKey, thisValue)

         thisValue = self.getIssuedAt()
         thisKey = 'issuedAt'
         setKeyVal(thisKey, thisValue)

         thisValue = self.getUserInfo()
         if thisValue:
            thisKey = 'userInfo'
            thisValue = thisValue.selfAsDict()
            setKeyVal(thisKey, thisValue)

         return selfDict

         
     def getExpiredAt(self):
         return self.__class__._expiredAt

     def setExpiredAt(self, expiredAt):
         self.__class__._expiredAt = expiredAt

     def getIssuedAt(self):
         return self.__class__._issuedAt

     def setIssuedAt(self, issuedAt):
         self.__class__._issuedAt = issuedAt

     def getUserInfo(self):
         return self.__class__._userInfo

     def setUserInfo(self, userInfo):
         self.__class__._userInfo = userInfo
         


class BearerTokenUserInfo(object):
     _userId = None
     _userName = None
     _role = None
     _acGroups = []
     _serviceBlackList = []

     def __init__(
             self,
             userInfoDict=None,
             ):
         if not userInfoDict:
             return

         pp = pprint.PrettyPrinter(indent=4)    

         if 'userId' in list(userInfoDict.keys()):
             self.setUserId(userInfoDict['userId'])
                            
         if 'userName' in list(userInfoDict.keys()):
             self.setUserName(userInfoDict['userName'])
                              
         if 'role' in list(userInfoDict.keys()):
             self.setRole(userInfoDict['role'])
                          
         if 'acGroups' in list(userInfoDict.keys()):
             self.setResGroupIds(userInfoDict['acGroups'])
                                 
         if 'serviceBlackList' in list(userInfoDict.keys()):
             self.setServiceBlackList(userInfoDict['serviceBlackList'])

     def selfAsDict(self):
         thisDict={}

         def setKeyVal(key, value):
             if value:
                 thisDict[key] = value
         
         thisValue = self.getUserId()
         thisKey = 'userId'
         setKeyVal(thisKey, thisValue)

         thisValue = self.getUserName()
         thisKey = 'userName'
         setKeyVal(thisKey, thisValue)

         thisValue = self.getRole()
         thisKey = 'role'
         setKeyVal(thisKey, thisValue)

         thisValue = self.getResGroupIds()
         thisKey = 'acGroups'
         setKeyVal(thisKey, thisValue)

         thisValue = self.getServiceBlackList()
         thisKey = 'serviceBlackList'
         setKeyVal(thisKey, thisValue)
         
         
         return thisDict
         
         
     def getUserId(self):
         return self.__class__._userId

     def setUserId(self, value):
         self.__class__._userId = value

     def getUserName(self):
         return self.__class__._userName

     def setUserName(self, value):
         self.__class__._userName = value

     def getRole(self):
         return self.__class__._role

     def setRole(self, value):
         self.__class__._role = value

     def getResGroupIds(self):
         return self.__class__._acGroups

     def setResGroupIds(self, value):
         self.__class__._acGroups = value
         
     def getServiceBlackList(self):
         return self.__class__._serviceBlackList

     def setServiceBlackList(self, value):
         self.__class__._serviceBlackList = value
         
    
