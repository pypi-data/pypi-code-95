class lookupError(Exception):
    def __init__(self):
        super(Exception, self).__init__("It is not a IPV4 or IPv6 address")


class tinyUrlError(Exception):
    def __init__(self):
        super(Exception, self).__init__("Unable to shorten the URL ")
