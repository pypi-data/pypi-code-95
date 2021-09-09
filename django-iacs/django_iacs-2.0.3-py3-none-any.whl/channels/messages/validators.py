from rest_framework import validators


class ResultCodeValidator:
    def __init__(self, codes_cls):
        self.codes_cls = codes_cls

    def __call__(self, value):
        attrs = {}
        for key in dir(self.codes_cls):
            if not str(key).startswith('__'):
                attrs[key] = getattr(self.codes_cls, key)
        if value not in attrs.values():
            raise validators.ValidationError(f'错误的返回码:{value}')
