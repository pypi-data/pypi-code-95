class UnattachedBucketError(Exception):
    """Raise on trying to perform actions on bucket without first attaching."""


class LocalFileExistsError(Exception):
    """Raise on trying to overwrite existing local file."""


class UnknownSourceTypeError(Exception):
    """Raise on trying to get size of unknown object type."""


class MismatchChecksumError(Exception):
    """Raise on local and remote checksums differing."""

class ConnectionError(Exception):
    """Raise on issue highly likely due to a non-functional connection"""

class MissingCredentialsError(Exception):
    """One or more credentials missing from json-file"""
