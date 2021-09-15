import os
from antidote import Constants, const


class Config(Constants):
    HOST = const[str](os.environ.get("MONGODB_HOST", "192.168.0.85"))
    PORT = const[int](os.environ.get("MONGODB_PORT", 27017))
    DATABASE = const[str](os.environ.get("MONGODB_DATABASE", "asterisk"))
    USER = const[str]("")
    PASSWORD = const[str]("")
