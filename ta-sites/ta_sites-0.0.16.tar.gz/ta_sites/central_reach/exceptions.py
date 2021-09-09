class CentralReachException(Exception):
    pass


class ScheduledMaintenance(CentralReachException):
    pass


class EmptyPage(CentralReachException):
    pass


class BadRequest(CentralReachException):
    pass
