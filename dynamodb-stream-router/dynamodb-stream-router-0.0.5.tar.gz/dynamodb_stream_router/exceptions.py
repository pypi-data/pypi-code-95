

class DynamodbStreamRouterException(Exception):
    pass


class SyntaxError(DynamodbStreamRouterException):
    pass


class KeywordError(DynamodbStreamRouterException):
    pass


class ConditionError(DynamodbStreamRouterException):
    pass


class MultipleRouteMatches(DynamodbStreamRouterException):
    pass


class HandledRouteException(DynamodbStreamRouterException):
    pass


class UnhandledRouteException(DynamodbStreamRouterException):
    pass
