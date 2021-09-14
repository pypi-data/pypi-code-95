class OTRSClientException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
        self.message = message


class ErrorCreatingSession(OTRSClientException):
    def __init__(self, error_msg):
        message = "Error creating the session with the next error message: {}".format(error_msg)
        super(OTRSClientException, self).__init__(message)


class TicketNotCreated(OTRSClientException):
    def __init__(self, error_msg):
        message = "Error creating the ticket with the next error message: {}".format(error_msg)
        super(OTRSClientException, self).__init__(message)


class TicketNotFoundError(OTRSClientException):
    def __init__(self, ticket_id, error_msg=''):
        message = "Error searching the ticket with ID {} with the next error message: {}".format(ticket_id, error_msg)
        super(OTRSClientException, self).__init__(message)


class UserManagementResponseEmpty(OTRSClientException):
    def __init__(self, user_id, call):
        message = "Error in method {} from user {}".format(call, user_id)
        super(OTRSClientException, self).__init__(message)


class ServiceTypeNotAllowedError(OTRSClientException):
    def __init__(self, id, service_type):
        message = "Contract {} with service type not allowed: {}".format(id, service_type)
        super(OTRSClientException, self).__init__(message)
