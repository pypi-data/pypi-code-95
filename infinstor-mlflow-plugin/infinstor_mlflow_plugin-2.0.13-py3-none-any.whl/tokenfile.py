import requests
from requests.exceptions import HTTPError
import json
import time
import os

verbose = False

def read_token_file(tokfile):
    fclient_id = None
    ftoken = None
    frefresh_token = None
    ftoken_time = None
    fservice = None
    token_type = None
    with (open(tokfile)) as fp:
        for count, line in enumerate(fp):
            if (line.startswith('ClientId=')):
                fclient_id = line[len('ClientId='):].rstrip()
            if (line.startswith('Token=')):
                ftoken = line[len('Token='):].rstrip()
            if (line.startswith('RefreshToken=')):
                frefresh_token = line[len('RefreshToken='):].rstrip()
            if (line.startswith('TokenTimeEpochSeconds=')):
                ftoken_time = int(line[len('TokenTimeEpochSeconds='):].rstrip())
            if (line.startswith('Service=')):
                fservice = line[len('Service='):].rstrip()
            if (line.startswith('TokenType=')):
                token_type = line[len('TokenType='):].rstrip()
    if (token_type == None):
        if (ftoken != None and ftoken.startswith('Custom ')):
            token_type = 'Custom'
        else:
            token_type = 'Bearer'
    return ftoken, frefresh_token, ftoken_time, fclient_id, fservice, token_type

def write_token_file(tokfile, token_time, token, refresh_token, client_id, service):
    os.makedirs(os.path.dirname(tokfile), exist_ok=True)
    with open(tokfile, 'w') as wfile:
        wfile.write("Token=" + token + "\n")
        wfile.write("RefreshToken=" + refresh_token + "\n")
        wfile.write("ClientId=" + client_id + "\n")
        wfile.write("TokenTimeEpochSeconds=" + str(token_time) + "\n")
        wfile.write("Service=" + service + "\n")
        wfile.close()

def renew_token(tokfile, refresh_token, client_id, service):
    payload = "{\n"
    payload += "    \"AuthParameters\" : {\n"
    payload += "        \"REFRESH_TOKEN\" : \"" + refresh_token + "\"\n"
    payload += "    },\n"
    payload += "    \"AuthFlow\" : \"REFRESH_TOKEN_AUTH\",\n"
    payload += "    \"ClientId\" : \"" + client_id + "\"\n"
    payload += "}\n"

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
    else:
        authres = response.json()['AuthenticationResult']
        token = authres['AccessToken']
        token_time = int(time.time())
        write_token_file(tokfile, token_time, token, refresh_token, client_id, service)

def get_token(tokfile, force_renew):
    token = None
    refresh_token = None
    token_time = None
    client_id = None
    service = None

    token, refresh_token, token_time, client_id, service, token_type = read_token_file(tokfile)

    if (token_type == "Custom"):
        if (verbose):
            print("Custom Infinstor token")
        return token, service

    if (force_renew == True):
        if (verbose):
            print("Forcing renewal of infinstor token")
        renew_token(tokfile, refresh_token, client_id, service)
        token, refresh_token, token_time, client_id, service, token_type = read_token_file(tokfile)
        return token, service

    time_now = int(time.time())
    if ((token_time + (30 * 60)) < time_now):
        print('InfinStor token has expired. Calling renew ' + str(token_time)\
                    + ', ' + str(time_now))
        renew_token(tokfile, refresh_token, client_id, service)
        token, refresh_token, token_time, client_id, service, token_type = read_token_file(tokfile)
        return token, service
    else:
        if (verbose):
            print('InfinStor token has not expired ' + str(token_time) + ', ' + str(time_now))
        return token, service
