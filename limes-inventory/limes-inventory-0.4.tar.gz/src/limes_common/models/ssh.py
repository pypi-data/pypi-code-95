from limes_common.models import Model

class Message(Model):
    MessageID: str
    Body: str
    IsError: bool
    
    def __init__(self, mid: str='', body: str='', isError:bool=False) -> None:
        self.MessageID = mid
        self.Body = body
        self.IsError = isError