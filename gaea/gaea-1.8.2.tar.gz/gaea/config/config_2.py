import os


class Config:
    LOGS_FOLDER_NAME = "log"
    IMAGES_FOLDER_NAME = "images"
    FLASK_SESSIONS_FOLDER_NAME = "flask_session"

    PATH_PROJECT = os.getcwd()
    PATH_LOGS = os.path.join(PATH_PROJECT, LOGS_FOLDER_NAME)
    PATH_IMAGES = os.path.join(PATH_PROJECT, IMAGES_FOLDER_NAME)
    PATH_FLASK_SESSIONS = os.path.join(PATH_PROJECT, FLASK_SESSIONS_FOLDER_NAME)

    URL_PREFIX = ""

    ENV = os.environ.get("ENV", "TEST")
    IDENTIFIER = os.environ.get("IDENTIFIER", "")
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "Unidentified")

    SECRET_KEY = "DEV"
    PASSWORD_REQUESTED = True

    FLASK_DEBUG = False

    DATABASE_PORT = 3306
    DATABASE_HOST = None
    DATABASE_USER = None
    DATABASE_PASSWORD = None
    DATABASE_DBNAME = "akb"

    def __init__(self):
        self.load_env_variables()
        self.create_missing_folders()
        self.validate()

    def validate(self):
        assert self.ENV in ("TEST", "PROD", "SIMU")

    @staticmethod
    def load_env_file(filename):
        for line in open(filename):
            data = line.strip().split("=")
            if len(data) != 2:
                continue
            if data[0] not in os.environ:
                os.environ[data[0]] = data[1]

    def load_env_variables(self):
        if os.path.exists(".env"):
            self.load_env_file(".env")

        identifier = f"{self.IDENTIFIER}_"

        for key, value in os.environ.items():
            if not key.startswith(identifier):
                continue

            key = key.replace(identifier, "")
            value = True if value == "true" else value
            value = False if value == "false" else value

            setattr(self, key, value)

    def create_missing_folders(self):
        paths = (self.PATH_LOGS, self.PATH_FLASK_SESSIONS)

        for path in paths:
            if not os.path.exists(path):
                os.mkdir(path)

    @property
    def DATABASE(self):
        if self.ENV not in ("SIMU", "PROD"):
            return {}

        return {
            "port": self.DATABASE_PORT,
            "host": self.DATABASE_HOST,
            "user": self.DATABASE_USER,
            "password": self.DATABASE_PASSWORD,
            "database": f"{self.IDENTIFIER}_{self.ENV}".lower(),
        }
