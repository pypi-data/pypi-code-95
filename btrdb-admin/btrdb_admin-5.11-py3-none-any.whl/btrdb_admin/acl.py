# btrdb_admin.acl
# API interactions for working with access control
#
# Author:   PingThings
# Created:  Tue Dec 18 14:50:05 2018 -0500
#
# For license information, see LICENSE.txt
# ID: acl.py [] allen@pingthings.io $

"""
API interactions for working with access control
"""

##########################################################################
## Imports
##########################################################################

from btrdb_admin.grpcinterface import admin_pb2
from btrdb_admin.exceptions import AdminAPIError, NotFoundError


##########################################################################
## Helpers
##########################################################################

def _group_to_dict(group):
    return {
        "name": group.name,
        "prefixes": [pref for pref in group.prefixes],
        "capabilities": [cap for cap in group.capabilities]
    }


def _user_to_dict(user):
    return {
        "username": user.username,
        "first_name": user.firstName,
        "last_name": user.lastName,
        "email": user.email,
        "comment": user.comment,
        "groups": [_group_to_dict(g) for g in user.groups],
    }


##########################################################################
## Classes
##########################################################################

class ACLAPI(object):
    """
    API interactions for working with access control
    """

    def get_identity_provider(self):
        """
        Returns the name of the identity provider currently set

        gRPC call:
            rpc GetIdentityProvider(GetIdentityProviderParams) returns (GetIdentityProviderResponse)

        Returns
        -------
        str
            The name of the identity provider currently being used
        """
        params = admin_pb2.GetIdentityProviderParams()
        response = self.client.GetIdentityProvider(params)
        AdminAPIError.check_error(response)
        return response.provider


    def set_identity_provider(self, provider):
        """
        Sets the identity provider used by the authenticator

        gRPC call:
            rpc SetIdentityProvider(SetIdentityProviderParams) returns (SetIdentityProviderResponse)

        Parameters
        ----------
        provider : str
            The name of the configured provider to set
        """
        params = admin_pb2.SetIdentityProviderParams(provider=provider)
        response = self.client.SetIdentityProvider(params)
        AdminAPIError.check_error(response)


    def get_all_users(self):
        """
        Returns a list of usernames for all BTrDB accounts

        gRPC call:
            rpc GetAllUsers(GetAllUsersParams) returns (GetAllUsersResponse)

        Returns
        -------
        list(str)
            list of strings representing users in the system

        """
        params = admin_pb2.GetAllUsersParams()
        response = self.client.GetAllUsers(params)
        return [user for user in response.user]


    def get_public_user(self):
        """
        Get the public user associated with the BTrDB server

        gRPC call:
            rpc GetPublicUser(GetPublicUserParams) returns (GetPublicUserResponse)

        Returns
        -------
        dict
            a dictionary representing the user
        """
        params = admin_pb2.GetPublicUserParams()
        response = self.client.GetPublicUser(params)
        AdminAPIError.check_error(response)

        return _user_to_dict(response.public)

    def user_exists(self, username):
        """
        Determines whether a user account exists in BTrDB

        gRPC call:
            rpc UserExists(UserExistsParams) returns (UserExistsResponse)

        Parameters
        ----------
        username: str
            username for account

        Returns
        -------
        bool : whether the user exists

        """
        params = admin_pb2.UserExistsParams(username=username)
        response = self.client.UserExists(params)
        AdminAPIError.check_error(response)
        return response.exists


    def create_user(self, username, password, first_name="", last_name="", email="", comment=""):
        """
        Creates a new user in BTrDB

        gRPC call:
            rpc CreateUser(CreateUserParams) returns (CreateUserResponse)

        Parameters
        ----------
        username: str
            username for new account
        password: str
            password for new account
        first_name: str
            first name for new account
        last_name: str
            last name for new account
        email: str
            email address for new account
        comment: str
            general comment for new account

        """
        params = admin_pb2.CreateUserParams(
            username=username, 
            password=password,
            firstName=first_name,
            lastName=last_name,
            email=email,
            comment=comment,
        )
        response = self.client.CreateUser(params)
        AdminAPIError.check_error(response)


    def set_user_password(self, username, password):
        """
        Change the password for a user in BTrDB

        gRPC call:
            rpc SetUserPassword(SetUserPasswordParams) returns (SetUserPasswordResponse)

        Parameters
        ----------
        username: str
            username for account
        password: str
            password for account

        """
        params = admin_pb2.SetUserPasswordParams(username=username, password=password)
        response = self.client.SetUserPassword(params)
        AdminAPIError.check_error(response)


    def get_api_key(self, username):
        """
        Retrieve a user's API key from BTrDB

        gRPC call:
            rpc GetAPIKey(GetAPIKeyParams) returns (GetAPIKeyResponse)

        Parameters
        ----------
        username: str
            username for account

        """
        params = admin_pb2.GetAPIKeyParams(username=username)
        response = self.client.GetAPIKey(params)
        AdminAPIError.check_error(response)

        return response.apikey


    def reset_api_key(self, username):
        """
        Reset and return a user's API key from BTrDB

        gRPC call:
            rpc ResetAPIKey(ResetAPIKeyParams) returns (ResetAPIKeyResponse)

        Parameters
        ----------
        username: str
            username for account

        """
        params = admin_pb2.ResetAPIKeyParams(username=username)
        response = self.client.ResetAPIKey(params)
        AdminAPIError.check_error(response)

        return response.apikey


    def delete_user(self, username):
        """
        Delete a user from BTrDB

        gRPC call:
            rpc DeleteUser(DeleteUserParams) returns (DeleteUserResponse)

        Parameters
        ----------
        username: str
            username for account to delete

        """
        params = admin_pb2.DeleteUserParams(username=username)
        response = self.client.DeleteUser(params)
        AdminAPIError.check_error(response)


    def authenticate_user_by_key(self, apikey):
        """
        Authenticate a user via their API key.

        gRPC call:
            rpc AuthenticateUserByKey(AuthenticateUserByKeyParams) returns (AuthenticateUserByKeyResponse)

        Parameters
        ----------
        apikey: str
            apikey for an account

        Returns
        -------
        dict
            a dictionary representing the user

        """
        params = admin_pb2.AuthenticateUserByKeyParams(apikey=apikey)
        response = self.client.AuthenticateUserByKey(params)
        AdminAPIError.check_error(response)

        return _user_to_dict(response.user)


    def authenticate_user(self, username, password):
        """
        Authenticate a user via their username and password.

        gRPC call:
            rpc AuthenticateUser(AuthenticateUserParams) returns (AuthenticateUserResponse)

        Parameters
        ----------
        username: str
            username for account
        password: str
            password for account

        Returns
        -------
        dict
            a dictionary representing the user

        """
        params = admin_pb2.AuthenticateUserParams(username=username, password=password)
        response = self.client.AuthenticateUser(params)
        AdminAPIError.check_error(response)

        return _user_to_dict(response.user)


    def get_all_groups(self):
        """
        Get all of the groups currently specified in BTrDB.

        gRPC call:
            rpc GetAllGroups(GetAllGroupsParams) returns (GetAllGroupsResponse)

        Returns
        -------
        list(str)
            A list of group names

        """
        params = admin_pb2.GetAllGroupsParams()
        response = self.client.GetAllGroups(params)
        AdminAPIError.check_error(response)

        return [group for group in response.group]


    def get_group(self, name):
        """
        Retreive group details from BTrDB

        gRPC call:
            rpc GetGroup(GetGroupParams) returns (GetGroupResponse)

        Parameters
        ----------
        name: str
            name of the group

        Returns
        -------
        dict
            a dictionary representing the group

        """
        params = admin_pb2.GetGroupParams(name=name)
        response = self.client.GetGroup(params)

        if response.error.code == 445:
            raise NotFoundError.from_response(response.error)
        AdminAPIError.check_error(response)

        return _group_to_dict(response.group)


    def get_builtin_user(self, username):
        """
        Retreive group details from BTrDB

        gRPC call:
            rpc GetBuiltinUser(GetBuiltinUserParams) returns (GetBuiltinUserResponse)

        Parameters
        ----------
        username: str
            username of the user

        Returns
        -------
        dict
            a dictionary representing the user
        """
        params = admin_pb2.GetBuiltinUserParams(username=username)
        response = self.client.GetBuiltinUser(params)
        AdminAPIError.check_error(response)

        return _user_to_dict(response.user)


    def add_user_to_group(self, username, group):
        """
        Adds a user to a group

        gRPC call:
            rpc AddUserToGroup(AddUserToGroupParams) returns (AddUserToGroupResponse)

        Parameters
        ----------
        username: str
            username of the user
        group: str
            name of the group

        """
        params = admin_pb2.AddUserToGroupParams(username=username, group=group)
        response = self.client.AddUserToGroup(params)
        AdminAPIError.check_error(response)


    def remove_user_from_group(self, username, group):
        """
        Removes a user from a group

        gRPC call:
            rpc RemoveUserFromGroup(RemoveUserFromGroupParams) returns (RemoveUserFromGroupResponse)

        Parameters
        ----------
        username: str
            username of the user
        group: str
            name of the group

        """
        params = admin_pb2.RemoveUserFromGroupParams(username=username, group=group)
        response = self.client.RemoveUserFromGroup(params)
        AdminAPIError.check_error(response)


    def set_group_prefixes(self, group, prefixes):
        """
        Removes a user from a group

        gRPC call:
            rpc SetGroupPrefixes(SetGroupPrefixesParams) returns (SetGroupPrefixesResponse)

        Parameters
        ----------
        group: str
            name of the group
        prefixes: list(str)
            list of strings representing the group prefixes

        """
        params = admin_pb2.SetGroupPrefixesParams(group=group, prefixes=prefixes)
        response = self.client.SetGroupPrefixes(params)
        AdminAPIError.check_error(response)


    def set_group_capabilities(self, group, capabilities):
        """
        Replaces group capabilities

        gRPC call:
            rpc SetGroupCapabilities(SetGroupCapabilitiesParams) returns (SetGroupCapabilitiesResponse)

        Parameters
        ----------
        group: str
            name of the group
        capabilities: list(?)
            list of ? representing the group capabilities

        """
        params = admin_pb2.SetGroupCapabilitiesParams(group=group, capabilities=capabilities)
        response = self.client.SetGroupCapabilities(params)
        AdminAPIError.check_error(response)


    def create_group(self, name):
        """
        Creates a new group in BTrDB

        gRPC call:
            rpc AddGroup(AddGroupParams) returns (AddGroupResponse)

        Parameters
        ----------
        name: str
            name of the name

        """
        params = admin_pb2.AddGroupParams(name=name)
        response = self.client.AddGroup(params)
        AdminAPIError.check_error(response)


    def delete_group(self, name):
        """
        Deletes a group in BTrDB

        gRPC call:
            rpc DeleteGroup(DeleteGroupParams) returns (DeleteGroupResponse)

        Parameters
        ----------
        name: str
            name of the name

        """
        params = admin_pb2.DeleteGroupParams(name=name)
        response = self.client.DeleteGroup(params)
        AdminAPIError.check_error(response)
