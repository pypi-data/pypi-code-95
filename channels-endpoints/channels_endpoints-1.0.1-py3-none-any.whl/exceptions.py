class ResolvePathError(Exception):
    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return self.error

    def __str__(self):
        return self.error


class BadRequest(Exception):
    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return self.error

    def __str__(self):
        return self.error


class AccessForbidden(Exception):
    def __init__(self, request, permission, log_exc=True):
        self.path = request.path
        self.permission = permission
        self.log_exc = log_exc

    def __repr__(self):
        return f'AccessForbidden at {self.permission}'

    def __str__(self):
        return f'AccessForbidden at {self.permission}'
