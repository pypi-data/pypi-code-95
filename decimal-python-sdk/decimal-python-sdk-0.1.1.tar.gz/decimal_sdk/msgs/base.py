class BaseMsg:
    type: str

    def get_message(self):
        return self.__dict__()

    def get_value(self):
        return self.__dict__()["value"]

    def get_type(self):
        return self.type
