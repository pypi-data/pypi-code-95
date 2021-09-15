class JelasticClientException(Exception):

    def __init__(self, message: str, response: dict = None):
        super().__init__(message)
        self.response = response
