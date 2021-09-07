class I2AOauth2ClientException(Exception):

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data

    def __str__(self):
        return str(self.data)


class I2AOauth2ClientUnauthorizedException(I2AOauth2ClientException):
    pass


class I2AOauth2ClientValidationError(I2AOauth2ClientException):
    pass


class I2AOauth2ClientNotFoundError(I2AOauth2ClientException):
    pass
