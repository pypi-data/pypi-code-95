class FinalException(Exception):

    def __init__(self, message="Failed on running function"):
        super(FinalException, self).__init__(message)
