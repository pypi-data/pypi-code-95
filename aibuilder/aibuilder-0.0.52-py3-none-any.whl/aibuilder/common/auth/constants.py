#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

import os
from enum import Enum


class _AccessTokenType(Enum):
    """Access token type"""
    ARM_TOKEN = "AzureAccessToken"
    CRM_TOKEN = "crmAccessToken"


class _AccessTokenResponseFields(Enum):
    """Access token response fields"""
    ACCESS_TOKEN = "accessToken"
    ACCESS_TOKEN_EXPIRY = "exp"
    USER_ID = "userId"
    TOKEN_TYPE = "tokenType"
    REFRESH_TOKEN = "refreshToken"
    TENANT_ID = "tenantId"


class _AccessTokenFileNames(Enum):
    """Access token file names in config directory"""
    ENVIRONMENT_FILE = "environments.json"
    ARM_TOKEN_FILE = "armAccessTokens.json"
    CRM_TOKEN_FILE = "crmAccessTokens.json"


class _AccessConfig(Enum):
    """Auth configurations"""
    RESOURCE = "https://management.core.windows.net/"
    GRAPH_RESOURCE = "https://graph.microsoft.com/"
    CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
    AUTHORITY = "https://login.microsoftonline.com/common"
    TOKEN_BUFFER_SECONDS = 600
    TOKEN_FILE_FLAGS = os.O_RDWR | os.O_CREAT | os.O_TRUNC
    TOKEN_FILE_PERMISSIONS = 0o600


class _ConfigFileConstants(Enum):
    """Constants for creating config"""
    DIRECTORY_NAME = "aibuilder"
