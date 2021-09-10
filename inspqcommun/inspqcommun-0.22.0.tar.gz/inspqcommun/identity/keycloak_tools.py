import os
import socket
from inspqcommun.identity.keycloak import KeycloakAPI, get_service_account_token, get_token
from distutils.util import strtobool

class KeycloakEnvironment():
    
    def __init__(self,
                 defaultKeycloakPort=18081,
                 defaultAuthClientId="admin-cli",
                 defaultAuthClientSecret = None,
                 defaultProtocol="http",
                 defaultAuthRealm="master",
                 defaultAuthUser='admin',
                 defaultAuthPassword='admin',
                 defaultAdminAuthUser='admin',
                 defaultAdminAuthPassword='admin',
                 defaultValidateCert = False
                 ):
        self.defaultKeycloakPort = defaultKeycloakPort
        self.defaultAuthClientId = defaultAuthClientId
        self.defaultAuthClientSecret = defaultAuthClientSecret
        self.defaultProtocol = defaultProtocol
        self.defaultAuthRealm = defaultAuthRealm
        self.defaultAuthUser = defaultAuthUser
        self.defaultAuthPassword = defaultAuthPassword
        self.defaultAdminAuthUser = defaultAdminAuthUser
        self.defaultAdminAuthPassword = defaultAdminAuthPassword
        self.defaultValidateCert = defaultValidateCert
        self.keycloak_enabled = True
        if 'KEYCLOAK_ENABLED' in os.environ:
            self.keycloak_enabled = bool(strtobool(os.environ['KEYCLOAK_ENABLED']))
        if 'KEYCLOAK_BASE_URL' in os.environ:
            self.keycloak_url = "{0}/auth".format(os.environ['KEYCLOAK_BASE_URL'])
        else:
            self.keycloak_url = "{protocol}://{host}:{port}/auth".format(
                protocol=self.defaultProtocol,
                host=socket.getfqdn(),
                port=self.defaultKeycloakPort)
            print("URL Keycloak non specifie: Utilisation de l'URL par defaut")
        self.keycloak_auth_realm = os.environ['KEYCLOAK_AUTH_REALM'] if 'KEYCLOAK_AUTH_REALM' in os.environ else self.defaultAuthRealm
        self.keycloak_auth_client_id = os.environ['KEYCLOAK_AUTH_CLIENT_ID'] if 'KEYCLOAK_AUTH_CLIENT_ID' in os.environ else self.defaultAuthClientId
        self.keycloak_auth_client_secret = os.environ['KEYCLOAK_AUTH_CLIENT_SECRET'] if 'KEYCLOAK_AUTH_CLIENT_SECRET' in os.environ else self.defaultAuthClientSecret
        self.keycloak_auth_user = os.environ['KEYCLOAK_AUTH_USER'] if 'KEYCLOAK_AUTH_USER' in os.environ else self.defaultAuthUser
        self.keycloak_auth_password = os.environ['KEYCLOAK_AUTH_PASSWORD'] if 'KEYCLOAK_AUTH_PASSWORD' in os.environ else self.defaultAuthPassword
        self.keycloak_admin_auth_user = os.environ['KEYCLOAK_ADMIN_AUTH_USER'] if 'KEYCLOAK_ADMIN_AUTH_USER' in os.environ else self.defaultAdminAuthUser
        self.keycloak_admin_auth_password = os.environ['KEYCLOAK_ADMIN_AUTH_PASSWORD'] if 'KEYCLOAK_ADMIN_AUTH_PASSWORD' in os.environ else self.defaultAdminAuthPassword
        self.validate_certs = os.environ['VALIDATE_CERTS'] if 'VALIDATE_CERTS' in os.environ else self.defaultValidateCert
        
    def authenticateByServiceAccount(self):
        headers = {}
        if self.keycloak_enabled:
            kc = KeycloakAPI(auth_keycloak_url=self.keycloak_url,
                         auth_client_id="admin-cli",
                         auth_username=self.keycloak_admin_auth_user,
                         auth_password=self.keycloak_admin_auth_password,
                         auth_realm=self.keycloak_auth_realm,
                         auth_client_secret=None,
                         validate_certs=self.validate_certs)
            client = kc.get_client_by_clientid(client_id=self.keycloak_auth_client_id, realm=self.keycloak_auth_realm)
            keycloak_auth_client_secret = kc.get_client_secret_by_id(client["id"], realm=self.keycloak_auth_realm)["value"]
            
            headers = get_service_account_token(
                base_url=self.keycloak_url,
                auth_realm=self.keycloak_auth_realm,
                client_id=self.keycloak_auth_client_id,
                client_secret=keycloak_auth_client_secret,
                validate_certs=self.validate_certs)
        self.headers = headers
        return headers

    def authenticateByUsernamePassword(self):
        headers = {}
        if self.keycloak_enabled:
            headers = get_token(
                base_url=self.keycloak_url,
                validate_certs=self.validate_certs,
                auth_realm=self.keycloak_auth_realm,
                client_id=self.keycloak_auth_client_id,
                auth_username=self.keycloak_auth_user,
                auth_password=self.keycloak_auth_password,
                client_secret=self.keycloak_auth_client_secret)
        self.headers = headers
        return headers
