
class PyOpenCellHTTPException(Exception):
    message = "Network problem accessing OpenCell API. Exception: \n {}"

    def __init__(self, error_msg):
        self.message = self.message.format(error_msg)
        super(PyOpenCellHTTPException, self).__init__(self.message)


class PyOpenCellAPIException(Exception):
    message = """OpenCell API returned an error response. \n
    Request: {verb} {url} \n
    Response: status={status} body={body}
    """

    def __init__(self, verb, url, status, body):
        self.message = self.message.format(verb=verb, url=url, status=status, body=body)
        self.api_error = body
        super(PyOpenCellAPIException, self).__init__(self.message)
