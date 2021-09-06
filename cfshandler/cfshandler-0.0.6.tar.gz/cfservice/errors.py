class OperationError(Exception):
    pass


class ConnectionTimeout(Exception):
    pass


class ProxyError(Exception):
    pass


class ParameterError(Exception):
    pass


class ServiceError(Exception):
    pass


class ServiceUnavailable(Exception):
    pass
