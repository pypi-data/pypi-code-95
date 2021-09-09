import requests
def uploadImage(url, token, payload):
    '''
    url : IoT.own Server Address
    token : IoT.own API Token
    payload : Image + Annotation Json Data (check format in README.md)
    '''
    apiaddr = url + "/api/v1.0/nn/image"
    header = {'Content-Type': 'application/json', 'Token': token}
    try:
        r = requests.post(apiaddr, data=payload, headers=header)
        if r.status_code == 200:
            return True
        else:
            print(r)
            return False
    except Exception as e:
        print(e)
        return False
def data(url, token, nid, data):
    '''
    url : IoT.own Server Address
    token : IoT.own API Token
    type: Message Type
    nid: Node ID
    data: data to send (JSON object)
    '''
    typenum = "2" # 2 static 
    apiaddr = url + "/api/v1.0/data"
    header = {'Accept':'application/json', 'token':token} 
    payload = { "type" : typenum, "nid" : nid, "data": data }
    try:
        r = requests.post(apiaddr, json=payload, headers=header)
        if r.status_code == 200:
            return True
        else:
            print(r)
            return False
    except Exception as e:
        print(e)
        return False

    