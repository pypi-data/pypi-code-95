
class FileFormatError(Exception):

    def __init__(self):
        super().__init__("File is not of format yml or json. Please recheck")

class OAPI_Info_NotFound(Exception):

    def __init__(self):
        super().__init__("Info Object Not Found in OPEN API Documentation")

class OAPI_Version_NotFound(Exception):

    def __init__(self):
        super().__init__("Version Object Not Found in OPEN API Documentation Under Info ")
