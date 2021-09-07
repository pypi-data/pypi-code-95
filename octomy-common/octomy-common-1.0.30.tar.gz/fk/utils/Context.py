class Context:
    def __init__(self, config):
        self.config = config

    def setting(self, key):
        return self.config.get(key, None)
