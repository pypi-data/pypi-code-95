import os


class ConfigKeys:
    ACCESS_TOKEN = "accesstoken"
    ID_TOKEN = "idtoken"
    TENANT_ID = "tenantid"
    EMAIL = "email"
    USER_POOL_ID = "userpoolid"
    CLIENT_ID = "clientid"
    USER_ID = "userid"
    IDENTIFIER = "identifier"


class ResponseAuthTokens:
    ACCESS_TOKEN = "accessToken"
    ID_TOKEN = "idToken"


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
