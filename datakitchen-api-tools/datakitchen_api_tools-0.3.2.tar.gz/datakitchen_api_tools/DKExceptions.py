
class DKOrderRunErrorException(Exception):
    pass

class DKOrderRunFailedTestException(Exception):
    pass

class DKOrderRunWarningTestException(Exception):
    pass

class DKLoginError(Exception):
    pass

class DKApiToolConfigError(Exception):
    pass


class DKOrderStartException(Exception):
    pass

class DKTimeoutException(Exception):
    pass