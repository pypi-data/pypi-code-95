import json
import urllib


class RequestError(Exception):
    """Basic Request Exception
    More detailed exception that returns the original requests object
    for inspection. Along with some attributes with specific details
    from the requests object. If return is json we decode and add it
    to the message.
    :Example:
    >>> try:
    ...   ss.Secrets.create_item(data={"bad_key":"bad_value"}
    ... except pysecretserver.RequestError as e:
    ...   print(e.error)
    """

    def __init__(self, message):
        req = message

        if req.status_code == 404:
            message = "The requested url: {} could not be found.".format(req.url)
        else:
            try:
                message = "The request failed with code {} {}: {}".format(
                    req.status_code, req.reason, req.json()
                )
            except ValueError:
                message = (
                    f"The request failed with code {req.status_code}: "
                    f"{req.reason} but more specific  details were not returned "
                    "in json. Check the SecretServer logs or investigate this "
                    "exception's error attribute."
                )

        super(RequestError, self).__init__(message)
        self.req = req
        self.request_body = req.request.body
        self.base = req.url
        self.error = req.text


class ContentError(Exception):
    """Content Exception
    If the API URL does not point to a valid SecretServer API, the server may
    return a valid response code, but the content is not json. This
    exception is raised in those cases.
    """

    def __init__(self, message):
        req = message

        message = (
            "The server returned invalid (non-json) data. Maybe it's not "
            "a SecretServer server?"
        )

        super(ContentError, self).__init__(message)
        self.req = req
        self.request_body = req.request.body
        self.base = req.url
        self.error = message


class Request(object):

    def __init__(self, base, http_session, token=None):

        self.base = self.normalize_url(base)
        self.http_session = http_session
        self.token = token
        self.url = self.base + "api/v1"
        self.auth_url = self.base + 'oauth2/token'

    def _make_request(self, verb="get", endpoint=None, data=None):

        if verb in ("post", "put"):
            headers = {"content-type": "application/json"}
        else:
            headers = {"accept": "application/json;"}

        headers["Authorization"] = "Bearer " + self.token

        resp = getattr(self.http_session, verb)(
            self.url+str(endpoint), headers=headers, json=data
        )

        if resp.ok:
            try:
                return resp.json()
            except json.JSONDecodeError:
                raise ContentError(resp)
        else:
            raise RequestError(resp)

    def get_session_token(self, data=None):

        headers = {
            'accept':'application/json',
            'content-type':'application/x-www-form-urlencoded'
        }

        resp = self.http_session.post(
            self.auth_url, headers=headers, data=data
        )

        if resp.ok:
            try:
                return resp.json()["access_token"]
            except json.JSONDecodeError:
                raise ContentError(resp)
        else:
            raise RequestError(resp)

    def normalize_url(self, url):
        """
        Builds a url for POST actions.
        """
        if url[-1] != "/":
            return "{}/".format(url)

        return url

    def get_item(self, item, item_id, params={}):

        return self._make_request(verb='get', endpoint=f"/{item}/{item_id}")

    def search_item(self, item, data):

        query = urllib.parse.urlencode(data, doseq=False)
        return self._make_request(verb='get', endpoint=f"/{item}/?{query}")

    def get_fields(self, item):

        return self._make_request(verb="get", endpoint=f"/{item}/fields")

    def get_field_sections(self, item, data):

        query = urllib.parse.urlencode(data, doseq=False)
        return self._make_request(verb="get", endpoint=f"/{item}/field-sections/?{query}")

    def create_item(self, item, data={}):

        return self._make_request(verb="post", endpoint=f"/{item}", data=data)

    def update_item(self, item, item_id, data={}):

        return self._make_request(verb="put", endpoint=f"/{item}/{item_id}", data=data)

    def delete_item(self, item, item_id):

        return self._make_request(verb="delete", endpoint=f"/{item}/{item_id}")

    def get_item_metadata(self, item, item_id, data):

        query = urllib.parse.urlencode(data, doseq=False)
        return self._make_request(verb="get", endpoint=f"/{item}/?{query}")
    
    def create_item_metadata(self, item, item_id, data={}):
        
        return self._make_request(verb="post", endpoint=f"/metadata/{item}/{item_id}", data=data)
    
    def update_item_metadata(self, item, item_id, data={}):
        
        return self._make_request(verb="patch", endpoint=f"/metadata/{item}/{item_id}", data=data)
    
    def delete_item_metadata(self, item, item_id, meta_id):
        
        return self._make_request(verb="delete", endpoint=f"/metadata/{item}/{item_id}/{meta_id}")
