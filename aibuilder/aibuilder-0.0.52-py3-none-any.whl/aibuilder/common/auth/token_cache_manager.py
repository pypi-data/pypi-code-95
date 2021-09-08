#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import json
import logging
import os
import time

import jwt

from aibuilder.common.auth.constants import _AccessTokenType, _AccessTokenFileNames, _AccessConfig, \
    _ConfigFileConstants, _AccessTokenResponseFields
from aibuilder.common.auth.exceptions import ConfigDirectoryCreationException, ConfigFileNotFoundException

logger = logging.getLogger(__name__)


class TokenCacheManager:
    """
    Class to manage access tokens

    """

    def __init__(self):
        """
        Sets ARM and CRM token file path

        """
        config_directory_path = TokenCacheManager.get_config_directory()

        # File path where access tokens are saved
        # TODO: GET SECURITY REVIEW. Task: 8982879
        self.arm_token_file = os.path.join(config_directory_path, _AccessTokenFileNames.ARM_TOKEN_FILE.value)
        self.crm_token_file = os.path.join(config_directory_path, _AccessTokenFileNames.CRM_TOKEN_FILE.value)

    def get_token(self, token_type: _AccessTokenType) -> dict:
        """
        Returns token dictionary from token file based on access token type.
        This method assumes that only one token is saved in a file

        :param token_type: access token type
        :return: returns a dictionary containing access token, expiry date and other token information
        """
        token_file_path = self._get_token_file_path(token_type=token_type)
        token_dict = {}
        try:
            token_dict = TokenCacheManager._read_file(token_file_path=token_file_path)
        except ConfigFileNotFoundException as e:
            logger.warning(f"Token file not found for token type {token_type}.\n Full Error: {e}")
        return token_dict

    def save_token(self, token_dict: dict, token_type: _AccessTokenType) -> None:
        """
        Writes token dictionary to token file based on token type

        :param token_dict: A dictionary of token, expiry date and other token information
        :param token_type: access token type enum
        :return: None
        """
        token_file_path = self._get_token_file_path(token_type=token_type)
        TokenCacheManager._write_file(token_dict=token_dict, token_file_path=token_file_path)

    @staticmethod
    def is_valid_token(token_dict: dict) -> bool:
        """
        Checks if access token is valid and returns a boolean representing token validity.

        :param token_dict: A dictionary containing token, expiry date and other token information
        :return: Returns True if the token is valid else returns True
        """
        is_valid_token = False
        access_token = token_dict.get(_AccessTokenResponseFields.ACCESS_TOKEN.value) if token_dict else None
        if access_token:
            token_dict = TokenCacheManager._decode_token(access_token=access_token)
            expiration_time = time.time() + _AccessConfig.TOKEN_BUFFER_SECONDS.value
            is_valid_token = token_dict.get(_AccessTokenResponseFields.ACCESS_TOKEN_EXPIRY.value) >= expiration_time
        return is_valid_token

    def _get_token_file_path(self, token_type: _AccessTokenType) -> str:
        """
        Returns token file path based on token type

        :param token_type: the access token type enum
        :return: token file path
        """
        if token_type == _AccessTokenType.CRM_TOKEN:
            return self.crm_token_file
        elif token_type == _AccessTokenType.ARM_TOKEN:
            return self.arm_token_file
        else:
            raise ValueError(f"Not supported token type {token_type}")

    @staticmethod
    def _read_file(token_file_path: str) -> dict:
        """
        Returns token dictionary from token file path

        :param token_file_path: Absolute local path to token file
        :return: Json deserialized dictionary from token file
        """
        token_dict = None

        if not os.path.isfile(token_file_path):
            raise ConfigFileNotFoundException(f"Failed to find token file {token_file_path}")

        with open(token_file_path, 'r') as file:
            try:
                token_dict = json.load(file)
            except ValueError as e:
                raise ValueError(f"Failed to load token file from {token_file_path}.\nInner Error: {e}")

        return token_dict

    @staticmethod
    def _write_file(token_dict: dict, token_file_path: str) -> None:
        """
        Writes token dictionary to a token file

        :param token_dict: A dictionary of token, expiry date and other token information
        :param token_file_path: Absolute local path to token file
        :return: None
        """
        try:
            token_json = json.dumps(token_dict)
        except TypeError as e:
            raise TypeError(f"Credentials passed is not json serializable.\nInner Error: {e}")

        token_file = os.open(token_file_path, _AccessConfig.TOKEN_FILE_FLAGS.value,
                             _AccessConfig.TOKEN_FILE_PERMISSIONS.value)
        with os.fdopen(token_file, 'w+') as token_file:
            token_file.write(token_json)

    @staticmethod
    def get_config_directory() -> str:
        """
        Returns AI Builder config directory path. Creates directory if it doesn't exist

        """
        directory_name = _ConfigFileConstants.DIRECTORY_NAME.value
        user_home_directory_path = os.path.expanduser("~")
        config_directory_path = os.path.join(user_home_directory_path, f'.{directory_name}')

        if not os.path.isdir(config_directory_path):
            TokenCacheManager._create_config_directory(config_directory_path)

        return config_directory_path

    @staticmethod
    def _create_config_directory(config_directory_path: str) -> None:
        """
        Creates config directory if it doesn't exist

        """
        if not os.path.isdir(config_directory_path):
            try:
                os.mkdir(config_directory_path)
            except OSError as e:
                error_message = f"Failed to create config directory {config_directory_path}.\nInner Error: {e}"
                raise ConfigDirectoryCreationException(error_message)

    @staticmethod
    def _decode_token(access_token: str) -> dict:
        """
        :param access_token: Azure active directory access token
        :return: A dictionary containing token, expiry date and other token information
        """
        return jwt.decode(access_token, verify=False)
