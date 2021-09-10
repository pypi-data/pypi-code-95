#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module scim
import uuid 
import json
import requests
from urllib3.exceptions import HTTPError

class SCIMObject(object):
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return cls(**json_dict)

class User(SCIMObject):
    URI = "/Users"

    CORE_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"
    ENTERPRISE_USER_SCHEMA = "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
    IDCS_USER_SCHEMA = "urn:ietf:params:scim:schemas:oracle:idcs:extension:user:User"
    PASSWORDSTATE_USER_SCHEMA = "urn:ietf:params:scim:schemas:oracle:idcs:extension:passwordState:User"
    USERSTATE_USER_SCHEMA = "urn:ietf:params:scim:schemas:oracle:idcs:extension:userState:User"
    APPARTENANCEORG_SCHEMA = "urn:sadupanorama:scim:api:messages:2.0:AppartenancesOrganisationnelles"
    
    SCIM_ATTRS = ['schemas', 'id', 'externalId', 'meta', 'idaasCreatedBy',
    'idaasLastModifiedBy']
    CORE_ATTRS = ['userName', 'name', 'displayName', 'nickName', 'profileUrl',
    'title', 'userType', 'locale', 'preferredLanguage', 'timezone', 'active',
    'password', 'emails', 'phoneNumbers', 'ims', 'photos', 'addresses',
    'groups', 'entitlements', 'roles', 'x509certificates']
    ENTERPRISE_ATTRS = ['employeeNumber', 'costCenter', 'organization',
    'division', 'department', 'manager']
    IDCS_ATTRS = ['isFederatedUser', 'status', 'internalName', 'provider',
    'creationMechanism', 'appRoles', 'doNotShowGettingStarted']
    PASSWORDSTATE_ATTRS = ['lastSuccessfulSetDate', 'cantChange', 'cantExpire',
            'mustChange', 'expired', 'passwordHistory']
    USERSTATE_ATTRS = ['lastSuccessfulLoginDate', 'lastFailedLoginDate',
    'loginAttempts', 'locked']
    
    APPARTENANCEORG_ATTRS = ["urn:sadupanorama:scim:api:messages:2.0:AppartenancesOrganisationnelles"]

    def __init__(self, *initial_data, **kwargs):
        self.schemas = [User.CORE_USER_SCHEMA]

        super(SCIMObject, self).__init__()

        for dictionary in initial_data:
            for key in dictionary:
                if key in User.APPARTENANCEORG_ATTRS:
                    for appOrgKey in dictionary[key]:
                        setattr(self, appOrgKey, dictionary[key][appOrgKey])
                else:
                    setattr(self, key, dictionary[key])
        for key in kwargs:
            if key in User.APPARTENANCEORG_ATTRS:
                for appOrgKey in kwargs[key]:
                    setattr(self, appOrgKey, kwargs[key][appOrgKey])
            else:
                setattr(self, key, kwargs[key])

    def __setattr__(self, name, value):
        if name in User.ENTERPRISE_ATTRS:
            self.schemas += [User.ENTERPRISE_USER_SCHEMA]
        elif name in User.IDCS_ATTRS:
            self.schemas += [User.IDCS_USER_SCHEMA]
        elif name in User.PASSWORDSTATE_ATTRS:
            self.schemas += [User.PASSWORDSTATE_USER_SCHEMA]
        elif name in User.USERSTATE_ATTRS:
            self.schemas += [User.USERSTATE_USER_SCHEMA]
        elif name in User.APPARTENANCEORG_ATTRS:
            self.schemas += [User.APPARTENANCEORG_SCHEMA]
            
        self.__dict__[name] = value
    
    def update(self, user):
        updates = json.loads(user.to_json())
        actual = json.loads(self.to_json())
        updated = dict()
        updated.update(actual)
        updated.update(updates)
        return self.from_json(json.dumps(updated))
    
class Group(SCIMObject):
    URI = "/Groups"

    CORE_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:Group"
    IDCS_GROUP_SCHEMA = "urn:ietf:params:scim:schemas:oracle:idcs:extension:group:Group"

    SCIM_ATTRS = ['schemas', 'id', 'externalId', 'meta', 'idaasCreatedBy',
    'idaasLastModifiedBy']
    CORE_ATTRS = ['displayName', 'members']
    IDCS_ATTRS = ['internalName', 'description', 'creationMechanism', 'appRoles']

    def __init__(self, *initial_data, **kwargs):
        self.schemas = [Group.CORE_GROUP_SCHEMA]

        super(SCIMObject, self).__init__()

        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __setattr__(self, name, value):
        if name in Group.IDCS_ATTRS:
            self.schemas += [Group.IDCS_GROUP_SCHEMA]

        self.__dict__[name] = value        

class SCIMClient(object):
    base_url = ""
    access_token = ""
    headers = ""
    validate_certs = True
    
    def __init__(self, base_url="", access_token="", additionnal_headers={}):
        self.base_url = base_url
        self.access_token = access_token
        self.headers = {
            'Content-Type': 'application/scim+json'
        }
        if access_token is not None and len(access_token) > 0:
            self.headers["Authorization"] = "bearer " + access_token
        if additionnal_headers is not None and len(additionnal_headers.keys()) > 0:
            for header in additionnal_headers.keys():
                self.headers[header] = additionnal_headers[header]
        
    def searchUserByUserName(self, userName):
        userSearchUrl = self.base_url + User.URI + '/.search'
        data = '{"filter":"userName eq \\\"' + userName + '\\\""}"'
        try:
            response = requests.post(url=userSearchUrl, headers=self.headers, data=data)
            users = response.json()
            if response.status_code != 200:
                raise SCIMException(
                'Could not search for user %s at %s: %s' % (userName, userSearchUrl, str(response.status_code)))
            if "Resources" in users and len(users["Resources"]) > 0:
                return User.from_json(json.dumps(users["Resources"][0]))
            return None
        except Exception as e:
            raise SCIMException(
                'Could not search for user %s at %s: %s' % (userName, userSearchUrl, str(e)))
        
    def getMe(self):
        meUrl = self.base_url + '/Me'
        try:
            response = requests.get(url=meUrl, headers=self.headers)
            if response.status_code == 200: 
                return User.from_json(response.content)
            raise SCIMException('Could not get Me at %s: %s' % (meUrl, response.json()))
        except Exception as e:
            raise SCIMException('Could not get Me at %s: %s' % (meUrl, str(e)))

    def getUserById(self, id):
        userUrl = self.base_url + User.URI + '/' + id
        try:
            response = requests.get(url=userUrl, headers=self.headers)
            if response.status_code == 200: 
                return User.from_json(response.content)
            raise SCIMException('Could not get user id %s at %s: %s' % (id, userUrl, response.json()))
        except Exception as e:
            raise SCIMException('Could not get user id %s at %s: %s' % (id, userUrl, str(e)))

    def createUser(self, user):
        userUrl = self.base_url + User.URI + '/'
        try:
            if "externalId" not in json.loads(user.to_json()):
                user.externalId = str(uuid.uuid1())
            data = user.to_json()
            response = requests.post(url=userUrl, headers=self.headers, data=data)
            if response.status_code == 201 or response.status_code == 200: 
                return User.from_json(response.content)
            raise SCIMException('Could not create user %s at %s: %s' % (user.userName, userUrl, response.json()))        
        except Exception as e:
            raise SCIMException('Could not create user %s at %s: %s' % (user.userName, userUrl, str(e)))
    
    
    def deleteUser(self, user):
        userUrl = self.base_url + User.URI + '/' + user.id
        try:
            response = requests.delete(url=userUrl, headers=self.headers)
            return response
        except Exception as e:
            raise SCIMException('Could not delete user %s at %s: %s' % (user.userName, userUrl, str(e)))
        
    def updateUser(self, user):
        userUrl = self.base_url + User.URI + '/' + user.id
        try:
            data = user.to_json()
            response = requests.put(url=userUrl, headers=self.headers, data=data)
            if response.status_code == 200: 
                return User.from_json(response.content)
            raise SCIMException('Could not create user %s at %s: %s' % (user.userName, userUrl, response.json()))
        except Exception as e:
            raise SCIMException('Could not update user %s at %s: %s' % (user.userName, userUrl, str(e)))
            
class SCIMException(Exception):
    """ Exception SCIM """
