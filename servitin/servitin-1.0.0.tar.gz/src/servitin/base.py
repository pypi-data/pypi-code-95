class BaseService:
    def __init__(self, loop, app_name, version, logger, log):
        self.loop = loop
        self.app_name = app_name
        self.version = version
        self.logger = logger
        self.log = log

    def stop(self):
        for cls in self.__class__.__bases__:
            if getattr(cls, 'close', None):
                cls.close(self)

