class BaseResource:
    _name = ""
    _url_path = ""

    def __init__(self, **kwargs):
        for kwarg, value in kwargs.items():
            setattr(self, kwarg, value)
