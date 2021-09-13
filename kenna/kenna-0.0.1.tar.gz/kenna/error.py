class _CredentialError(ValueError):
    pass


class MissingCredentialsError(_CredentialError):
    pass


class InvalidCredentialsError(_CredentialError):
    pass


class InvalidRegionError(ValueError):
    pass
