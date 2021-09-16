

class CustomException(Exception):
    def __init__(self, code, message):
        super(CustomException, self).__init__()
        self.message = message
        self.code = code
