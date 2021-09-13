class BNetError(Exception):
    pass


class BNetRegionNotFoundError(BNetError):
    pass


class BNetDataNotFoundError(BNetError):
    pass


class BNetAccessForbiddenError(BNetError):
    pass


class BNetClientError(BNetError):
    pass
