from requests.auth import AuthBase


class ApiTokenAuth(AuthBase):
    def __init__(self, apiToken):
        self.apiToken = apiToken

    def __call__(self, request):
        request.headers["X-API-TOKEN"] = self.apiToken
        return request
