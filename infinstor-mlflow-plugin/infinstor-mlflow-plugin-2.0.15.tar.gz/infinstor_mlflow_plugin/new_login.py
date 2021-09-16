#!/usr/bin/env python
import sys
import getpass
import json
import builtins
from . import servicedefs
from infinstor_mlflow_plugin.tokenfile import read_token_file, write_token_file, get_token
from requests.exceptions import HTTPError
import requests
from os.path import expanduser
from os.path import sep as separator
import time
import configparser
from urllib.parse import unquote, urlparse
import os

def print_version(token):
    headers = { 'Authorization': token }
    url = 'https://mlflow.' + builtins.service + '/api/2.0/mlflow/infinstor/get_version'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred while getting version: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred while getting version: {err}')
        raise

def get_creds():
    if sys.stdin.isatty():
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    else:
        username = sys.stdin.readline().rstrip()
        password = sys.stdin.readline().rstrip()
    return username, password

def login_and_update_token_file(username, password):
    postdata = dict()
    auth_parameters = dict()
    auth_parameters['USERNAME'] = username
    auth_parameters['PASSWORD'] = password
    postdata['AuthParameters'] = auth_parameters
    postdata['AuthFlow'] = "USER_PASSWORD_AUTH"
    postdata['ClientId'] = builtins.clientid

    payload = json.dumps(postdata)

    url = 'https://cognito-idp.us-east-1.amazonaws.com:443/'
    headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
            }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise


    authres = response.json()['AuthenticationResult']
    idToken = authres['IdToken']
    accessToken = authres['AccessToken']
    refresh_token = authres['RefreshToken']

    ##Refresh token once############################
    postdata = dict()
    auth_parameters = dict()
    auth_parameters['REFRESH_TOKEN'] = refresh_token
    postdata['AuthParameters'] = auth_parameters
    postdata['AuthFlow'] = "REFRESH_TOKEN_AUTH"
    postdata['ClientId'] = builtins.clientid

    payload = json.dumps(postdata)

    url = 'https://cognito-idp.us-east-1.amazonaws.com:443/'
    headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
            }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise

    authres = response.json()['AuthenticationResult']
    idToken = authres['IdToken']
    accessToken = authres['AccessToken']

    #########

    token_time = int(time.time())
    tokfile = expanduser("~") + separator + '.infinstor' + separator + 'token'
    write_token_file(tokfile, token_time, accessToken, refresh_token, builtins.clientid,\
                builtins.service)

    payload = ("ProductCode=" + builtins.prodcode)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': idToken
        }

    url = 'https://' + builtins.apiserver + '/customerinfo'
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise

    # print('customerinfo success')
    response_json = response.json()
    infinStorAccessKeyId = unquote(response_json.get('InfinStorAccessKeyId'))
    infinStorSecretAccessKey = unquote(response_json.get('InfinStorSecretAccessKey'))
    setup_credentials(infinStorAccessKeyId, infinStorSecretAccessKey)

    print('Login to service ' + builtins.service + ' complete')
    print_version(accessToken)
    return True

def setup_credentials(infinStorAccessKeyId, infinStorSecretAccessKey):
    home = expanduser("~")
    config = configparser.ConfigParser()
    newconfig = configparser.ConfigParser()
    credsfile = home + separator + ".aws" + separator + "credentials"
    if (os.path.exists(credsfile)):
        credsfile_save = home + separator + ".aws" + separator + "credentials.save"
        try:
            os.remove(credsfile_save)
        except Exception as err:
            print()
        try:
            os.rename(credsfile, credsfile_save)
        except Exception as err:
            print()
        config.read(credsfile_save)
        for section in config.sections():
            if (section != 'infinstor'):
                newconfig[section] = {}
                dct = dict(config[section])
                for key in dct:
                    newconfig[section][key] = dct[key]
    else:
        dotaws = home + "/.aws"
        if (os.path.exists(dotaws) == False):
            os.mkdir(dotaws, 0o755)
            open(credsfile, 'a').close()

    newconfig['infinstor'] = {}
    newconfig['infinstor']['aws_access_key_id'] = infinStorAccessKeyId
    newconfig['infinstor']['aws_secret_access_key'] = infinStorSecretAccessKey

    with open(credsfile, 'w') as configfile:
        newconfig.write(configfile)

# returns dict of service details if successful, None if unsuccessful
def bootstrap_from_mlflow_rest():
    muri = os.getenv('MLFLOW_TRACKING_URI')
    pmuri = urlparse(muri)
    if (pmuri.scheme.lower() != 'infinstor'):
        return None
    cognito_domain = pmuri.hostname[pmuri.hostname.index('.')+1:]
    url = 'https://' + pmuri.hostname + '/api/2.0/mlflow/infinstor/get_version'
    headers = { 'Authorization': 'None' }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        resp = response.json()
        return { 'clientid' : resp['cognitoCliClientId'],
                'appclientid' : resp['cognitoAppClientId'],
                'mlflowserver' : resp['mlflowDnsName'] + '.' + cognito_domain,
                'mlflowuiserver' : resp['mlflowuiDnsName'] + '.' + cognito_domain,
                'mlflowstaticserver' : resp['mlflowstaticDnsName'] + '.' + cognito_domain,
                'apiserver' : resp['apiDnsName'] + '.' + cognito_domain,
                'serviceserver' : resp['serviceDnsName'] + '.' + cognito_domain,
                'service' : cognito_domain}
    except HTTPError as http_err:
        return None
    except Exception as err:
        return None

def new_login(srvdct):
    builtins.clientid = srvdct['clientid']
    builtins.appclientid = srvdct['appclientid']
    builtins.mlflowserver = srvdct['mlflowserver']
    builtins.mlflowuiserver = srvdct['mlflowuiserver']
    builtins.mlflowstaticserver = srvdct['mlflowstaticserver']
    builtins.apiserver = srvdct['apiserver']
    builtins.serviceserver = srvdct['serviceserver']
    builtins.service = srvdct['service']

    try:
        tokfile = expanduser("~") + separator + '.infinstor' + separator + 'token'
        token, service = get_token(tokfile, False)
        if (service == builtins.service):
            print('Login to service ' + service + ' already completed')
            sys.exit(0)
        else:
            print('service mismatch between MLFLOW_TRACKING_URI and ~/.infinstor/token. Forcing login')
            raise Exception('service mismatch between MLFLOW_TRACKING_URI and ~/.infinstor/token. Forcing login')
    except Exception as err:
        pass

    username, password = get_creds()
    return login_and_update_token_file(username, password)
