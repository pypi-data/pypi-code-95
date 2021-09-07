from requests.auth import HTTPBasicAuth
import requests

def get_auth(username, password):
    auth = HTTPBasicAuth(username, password)
    uri = 'https://edtsystems-webtest.azurewebsites.net/api/v2/Authentication'

    data = {'username': username,
            'password': password
            }
    r = requests.post(uri, auth=auth, data=data)
    user_auth = r.json()
    m_id = user_auth['MACId']
    m_token = user_auth['MACToken']
    return m_id, m_token

if __name__ == '__main__':
    get_auth('fraserda', 'Medved3#')
