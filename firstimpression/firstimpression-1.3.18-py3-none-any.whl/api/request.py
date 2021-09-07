import requests

status_codes_messages = {
    204: {'type': 'ERROR', 'message': 'The server successfully processed the request, and is not returning any content'},
    301: {'type': 'ERROR', 'message': 'This and all future requests should be directed to the given URI'},
    400: {'type': 'ERROR', 'message': 'The server cannot or will not process the request due to an apparent client error (e.g., malformed request syntax, size too large, invalid request message framing, or deceptive request routing).'},
    401: {'type': 'ERROR', 'message': 'Similar to 403 Forbidden, but specifically for use when authentication is required and has failed or has not yet been provided. The response must include a WWW-Authenticate header field containing a challenge applicable to the requested resource. See Basic access authentication and Digest access authentication. 401 semantically means unauthorised, the user does not have valid authentication credentials for the target resource.'},
    402: {'type': 'ERROR', 'message': 'Reserved for future use.'},
    403: {'type': 'ERROR', 'message': 'The request contained valid data and was understood by the server, but the server is refusing action. This may be due to the user not having the necessary permissions for a resource or needing an account of some sort, or attempting a prohibited action (e.g. creating a duplicate record where only one is allowed). This code is also typically used if the request provided authentication by answering the WWW-Authenticate header field challenge, but the server did not accept that authentication. The request should not be repeated.'},
    404: {'type': 'ERROR', 'message': 'The requested resource could not be found but may be available in the future. Subsequent requests by the client are permissible.'},
    405: {'type': 'ERROR', 'message': 'A request method is not supported for the requested resource; for example, a GET request on a form that requires data to be presented via POST, or a PUT request on a read-only resource.'},
    406: {'type': 'ERROR', 'message': 'he requested resource is capable of generating only content not acceptable according to the Accept headers sent in the request.'},
    407: {'type': 'ERROR', 'message': 'The client must first authenticate itself with the proxy.'},
    408: {'type': 'ERROR', 'message': 'The server timed out waiting for the request. According to HTTP specifications: The client did not produce a request within the time that the server was prepared to wait. The client MAY repeat the request without modifications at any later time.'},
    409: {'type': 'ERROR', 'message': 'Indicates that the request could not be processed because of conflict in the current state of the resource, such as an edit conflict between multiple simultaneous updates.'},
    411: {'type': 'ERROR', 'message': 'The request did not specify the length of its content, which is required by the requested resource.'},
    413: {'type': 'ERROR', 'message': 'The request is larger than the server is willing or able to process.'},
    423: {'type': 'ERROR', 'message': 'The resource that is being accessed is locked.'},
    429: {'type': 'ERROR', 'message': 'The user has sent too many requests in a given amount of time. Intended for use with rate-limiting schemes.'},
    451: {'type': 'ERROR', 'message': 'A server operator has received a legal demand to deny access to a resource or to a set of resources that includes the requested resource.'},
    500: {'type': 'ERROR', 'message': 'A generic error message, given when an unexpected condition was encountered and no more specific message is suitable.'},
    501: {'type': 'ERROR', 'message': 'The server either does not recognize the request method, or it lacks the ability to fulfil the request. Usually this implies future availability (e.g., a new feature of a web-service API).'},
    502: {'type': 'ERROR', 'message': 'The server was acting as a gateway or proxy and received an invalid response from the upstream server.'},
    503: {'type': 'ERROR', 'message': 'The server cannot handle the request (because it is overloaded or down for maintenance). Generally, this is a temporary state.'},
    504: {'type': 'ERROR', 'message': 'The server was acting as a gateway or proxy and did not receive a timely response from the upstream server.'},
    505: {'type': 'ERROR', 'message': 'The server does not support the HTTP protocol version used in the request.'},
    506: {'type': 'ERROR', 'message': 'Transparent content negotiation for the request results in a circular reference.'},
    507: {'type': 'ERROR', 'message': 'The server is unable to store the representation needed to complete the request.'},
    508: {'type': 'ERROR', 'message': 'The server detected an infinite loop while processing the request'},
    509: {'type': 'ERROR', 'message': 'Further extensions to the request are required for the server to fulfil it.'},
    510: {'type': 'ERROR', 'message': 'The client needs to authenticate to gain network access. Intended for use by intercepting proxies used to control access to the network'},
    110: {'type': 'WARN', 'message': 'A response provided by a cache is stale (the expiration time set for it has passed).'},
    111: {'type': 'WARN', 'message': 'An attempt to validate the response failed, due to an inability to reach the server.'},
    112: {'type': 'WARN', 'message': 'The cache is intentionally disconnected from the rest of the network.'},
}


def request(url, header=None, params=None, verify=None, method='get'):
    if method == 'get':
        response = requests.get(url, headers=header, params=params, verify=verify, timeout=6.0)
    elif method == 'post':
        response = requests.post(url, params, timeout=12.0)
    
    if check_request(response)['type'] == 'SUCCESS':
        return response, False
    else:
        return check_request(response), True


def request_json(url, header=None, params=None, verify=None, method='get'):
    response, is_error = request(url, header, params, verify, method)
    if is_error:
        return response, is_error
    else:
        return response.json(), is_error

def check_request(request):
    if request.status_code in status_codes_messages:
        message = status_codes_messages[request.status_code]
        message['reason'] = request.reason
        return message
    else:
        return {'type': 'SUCCESS'}