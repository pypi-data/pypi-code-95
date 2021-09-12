class Request:

    def __init__(self, headers: dict = None, data: dict = None):
        if headers is None:
            headers = {}
        else:
            assert isinstance(headers, dict), 'Unsupported type {0} for headers, dict required.' \
                .format(type(headers))
        self.headers = headers

        if data is None:
            data = {}
        else:
            assert isinstance(data, dict), 'Unsupported type {0} for data, dict required.' \
                .format(type(data))
        self.data = data

    def __repr__(self):
        return "<Response(data='{0}', headers='{1}')>".format(
            self.data, self.headers
        )
