import urllib.parse


class Path:
    """Represents a path to a storage.

    The path can represent one or more physical paths, which can be accessed through various schemes. Schemes can be
    file, http, https, ftp, s3, etc.
    """

    def __init__(self, plainPath):
        self.raw = plainPath
        self.parsed = urllib.parse.urlparse(plainPath)
