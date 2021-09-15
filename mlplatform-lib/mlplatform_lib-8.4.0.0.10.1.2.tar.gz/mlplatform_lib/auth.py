class Auth():
    SECRET_LIST = ["projectId", "userId", "accessToken", "refreshToken", "authorizationType"]

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance

    def __init__(self, *args, **kwargs):
        self.secret_mount_path = os.environ["secretMountPath"]
        self.load_env(secret_mount_path)

    def load_env(self, secret_mount_path):
        file_list = [f for f in os.listdir(self.secret_mount_path)]
        for secret in self.SECRET_LIST:
            if secret not in file_list:
                print(f'Cannot found "{secret}" in secret path "{self.secret_mount_path}".')
                exit(1)

        for file in file_list:
            if file in self.SECRET_LIST:
                setattr(self, file, open(os.path.join(self.secret_mount_path, file), "r").read())