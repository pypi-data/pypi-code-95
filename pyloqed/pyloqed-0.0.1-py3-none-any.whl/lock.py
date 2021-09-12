# lock.py

import requests

def lock(lock_id, lock_api_key, api_token, local_key_id):
    """Lock the lock

    Parameters:
    -----------
    lock_id : string
        Your LOQED lock id
    lock_api_key : string
        Your LOQED lock api key
    api_token : string
        Your LOQED api token
    local_key_id :
        Your LOQED local key id
    """

    url = 'https://production.loqed.com:8080/v1/locks/{l}/state?lock_api_key={k}&api_token={t}&lock_state=NIGHT_LOCK&local_key_id={i}'.format(l=lock_id,
                                                                                                                                                k=lock_api_key,
                                                                                                                                                t=api_token,
                                                                                                                                                i=local_key_id)

    print(url)

    return requests.get(url)

def unlock(lock_id, lock_api_key, api_token, local_key_id):
    """Unlock the lock

    Parameters:
    -----------
    lock_id : string
        Your LOQED lock id
    lock_api_key : string
        Your LOQED lock api key
    api_token : string
        Your LOQED api token
    local_key_id :
        Your LOQED local key id
    """

    url = 'https://production.loqed.com:8080/v1/locks/{l}/state?lock_api_key={k}&api_token={t}&lock_state=DAY_LOCK&local_key_id={i}'.format(l=lock_id,
                                                                                                                                                k=lock_api_key,
                                                                                                                                                t=api_token,
                                                                                                                                                i=local_key_id)
    return requests.get(url)

def open(lock_id, lock_api_key, api_token, local_key_id):
    """OPEN the lock

    Parameters:
    -----------
    lock_id : string
        Your LOQED lock id
    lock_api_key : string
        Your LOQED lock api key
    api_token : string
        Your LOQED api token
    local_key_id :
        Your LOQED local key id
    """

    url = 'https://production.loqed.com:8080/v1/locks/{l}/state?lock_api_key={k}&api_token={t}&lock_state=OPEN&local_key_id={i}'.format(l=lock_id,
                                                                                                                                                k=lock_api_key,
                                                                                                                                                t=api_token,
                                                                                                                                                i=local_key_id)
    return requests.get(url)