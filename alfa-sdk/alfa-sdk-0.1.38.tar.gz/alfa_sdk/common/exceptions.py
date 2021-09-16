class AlfaError(Exception):
    template = "An unspecified error occurred"
    code = "UNKNOWN_ERROR"
    status = 500

    def __init__(self, **kwargs):
        if "template" in kwargs:
            self.template = kwargs.get("template")

        message = self.template.format(**kwargs)
        Exception.__init__(self, message)
        self.kwargs = kwargs

    def __reduce__(self):
        return _unpickle_exception, (self.__class__, (), self.kwargs)


def _unpickle_exception(exception_class, args=(), kwargs={}):
    return exception_class(*args, **kwargs)


#


class ResourceError(AlfaError):
    template = "Error encountered for resource {resource}: {error}"
    code = "RESOURCE_NOT_FOUND"
    status = 400


class ValidationError(AlfaError):
    template = "Error during validation: {error}"
    code = "VALIDATION_FAILED"
    status = 400


class PermissionError(AlfaError):
    template = "Not authorized: {error}"
    code = "ACCESS_DENIED"
    status = 403


class AuthenticationError(AlfaError):
    template = "Error encountered during authentication: {error}"
    code = "INVALID_TOKEN"
    status = 401


class AuthorizationError(PermissionError):
    template = "Not authorized for request to {url}: {error}"
    code = "UNAUTHORIZED"
    status = 401


class RequestError(AlfaError):
    template = "Error encountered during request to {url} ({status}): {error}"
    code = "REQUEST_FAILED"


#


class ResourceNotFoundError(ResourceError):
    template = "Resource not found in {url}: {error}"


class ResourceDeletionError(ValidationError):
    template = "Cannot delete {resource}: {error}"


class CredentialsError(ValidationError):
    template = "Authentication credentials not found / invalid"


class TokenNotFoundError(CredentialsError):
    template = "Authentication tokens not found"


class UnknownServiceError(ValidationError):
    template = "Unknown service: '{service_name}'. Valid service names are: {known_service_names}"


class ServiceEnvironmentError(ValidationError):
    template = "Environment '{environment}' does not exist for service '{service_name}'"


class SemanticVersionError(ValidationError):
    template = "Version '{version}' does not comply with Semantic Versioning."


class AlfaConfigError(ValidationError):
    template = "{message} ({error})"
