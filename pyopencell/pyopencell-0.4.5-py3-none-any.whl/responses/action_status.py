class ActionStatus:
    status = ""
    errorCode = ""
    message = ""

    def __init__(self, status="", errorCode="", message=""):
        self.status = status
        self.errorCode = errorCode
        self.message = message
