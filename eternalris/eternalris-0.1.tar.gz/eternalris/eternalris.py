import requests

class InvalidKeyError(Exception):
    pass

class EmptyURLError(Exception):
    pass

class OutOfUsesError(Exception):
    pass

class ImageSearchResult:
    def __init__(self,result):
        self.full_matches = result.get('full_matches')
        self.partial_matches = result.get('partial_matches')
        self.partial_pages = result.get('pages_with_matching_images')
        self.probabilities = result.get('probabilities')

class Api:
    def __init__(self,key,server="http://eternaltesting.xyz:8880/api/ris/v1/search"):
        self.api = requests.Session()
        self.api.headers.update({'Authorization': key})
        self.server = server
    def search(self,url):
        resp = self.api.get(self.server,params={'url':imageurl}).json()
        if resp.get('code') == 1099:
            raise EmptyURLError("Empty or invalid URL provided!")
        elif resp.get('code') == 1098:
            raise InvalidKeyError("Key is invalid!")
        else:
            return ImageSearchResult(resp)