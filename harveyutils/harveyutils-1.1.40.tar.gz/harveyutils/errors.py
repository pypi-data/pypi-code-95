class BadStatusCodeError(Exception):
    """Exception raised when a bad status code is recieved.

    Attributes:
        status_code -- The status code response
    """

    def __init__(self, status_code, extra_message="Bad status code."):
        self.status_code = status_code
        self.message = f"STATUS {self.status_code}: {extra_message}"
        super().__init__(self.message)
