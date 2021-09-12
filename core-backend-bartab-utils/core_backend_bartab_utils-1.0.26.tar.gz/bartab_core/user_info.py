from .lambda_client import AbstractLambdaClient
from rest_framework.serializers import ValidationError
from .cache_manager import CacheManager
from bartab_core.validate import is_valid_uuid
class UserInfoCacheManager:    
    USERNAME_BY_UNIQUE_IDENTIFER_KEY_NAME = "user_info_username_by_unique_identifier_map"

    USER_INFO_BY_USERNAME_KEY_NAME = 'user_info_user_info_map_by_username_map'

    def __init__(self):
        self.cache_manager = CacheManager.get_instance()

    def get_user_info_or_none(self, username:str):
        user_info_map_by_username = self.cache_manager.set_or_get(
            self.USER_INFO_BY_USERNAME_KEY_NAME, {})

        return None if username not in user_info_map_by_username else user_info_map_by_username[username]

    def get_username_or_none(self, unique_user_identifier: str):
        username_by_unique_identifier = self.cache_manager.set_or_get(
            self.USERNAME_BY_UNIQUE_IDENTIFER_KEY_NAME, {})

        return None if unique_user_identifier not in username_by_unique_identifier else username_by_unique_identifier[unique_user_identifier]

    def set_user_info(self, user_info):
        user_info_map_by_username = self.cache_manager.set_or_get(
            self.USER_INFO_BY_USERNAME_KEY_NAME, {})
        
        user_info_map_by_username[user_info['username']] = user_info

        self.cache_manager.set(
            self.USER_INFO_BY_USERNAME_KEY_NAME, user_info_map_by_username
        )

    def set_username_map(self, unique_user_identifier, username):
        username_by_unique_identifier = self.cache_manager.set_or_get(
            self.USERNAME_BY_UNIQUE_IDENTIFER_KEY_NAME, {})

        username_by_unique_identifier[unique_user_identifier] = username

        self.cache_manager.set(
            self.USERNAME_BY_UNIQUE_IDENTIFER_KEY_NAME, username_by_unique_identifier
        )


class UserInfoClient(AbstractLambdaClient):

    USER_INFO = 'user_info'
    USERNAME = 'username'
    GET_USER_POOL_INFO = 'get_user_pool_info'
    GET_USER_ATTRIBUTE_INFO = 'get_user_attribute_info'

    valid_triggers = [USERNAME, USER_INFO,
                      GET_USER_POOL_INFO, GET_USER_ATTRIBUTE_INFO]

    def __init__(self):
        super().__init__("us-east-2", "UserInfo", True, True)
        self.user_info_cache_manager = UserInfoCacheManager()

    def get_user_info(self, unique_user_identifier, use_cache: bool = True):
        if use_cache:
            if is_valid_uuid(unique_user_identifier):
                username = unique_user_identifier
            else:
                username = self.get_username(unique_user_identifier, True)

            user_info = self.user_info_cache_manager.get_user_info_or_none(
                username)
            
            if user_info != None:
                return user_info

        user_info = super().invoke(self.USER_INFO, {
            "value": unique_user_identifier
        })['body']

        self.user_info_cache_manager.set_user_info(user_info)
        
        return user_info

    def get_username(self, unique_user_identifier, use_cache: bool = True):
        if use_cache:
            username = self.user_info_cache_manager.get_username_or_none(
                unique_user_identifier)
            if username != None:
                return username

        username = super().invoke(self.USERNAME, {
            "value": unique_user_identifier
        })['body']['value']

        self.user_info_cache_manager.set_username_map(
            unique_user_identifier, username)
        
        return username

    def get_user_pool_info(self):
        return super().invoke(self.GET_USER_POOL_INFO)['body']

    def get_user_attribute_info(self):
        return super().invoke(self.GET_USER_ATTRIBUTE_INFO)['body']

    def get_user_display_name(self, unique_user_identifier_or_user_info, fail_on_unknown: bool = False, use_cache: bool = True):
        name = ''

        if isinstance(unique_user_identifier_or_user_info, dict):
            user_info = unique_user_identifier_or_user_info
        else:
            user_info = self.get_user_info(
                unique_user_identifier_or_user_info, use_cache)

        if 'first_name' in user_info and len(user_info['first_name']) > 0:
            name = user_info['first_name']

        if 'last_name' in user_info and len(user_info['last_name']) > 0:
            if len(name) > 0:
                name = name + " "

            name = name + user_info['last_name']

        if name != '':
            return name
        elif fail_on_unknown:
            raise ValidationError("User has invalid name")
        else:
            return "Unknown User"

    def is_staff(self, unique_user_identifier, use_cache: bool = True):
        return self.get_user_info(unique_user_identifier, use_cache)['is_staff']

    def is_sales(self, unique_user_identifier, use_cache: bool = True):
        user_info = self.get_user_info(unique_user_identifier, use_cache)
        
        return user_info['is_staff'] or user_info['is_sales']
