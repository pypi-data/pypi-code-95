class BaseModelAdmin:
    readonly_fields = []
    list_headers = []

    def __init__(self, *args, **kwargs):
        raise NotImplementedError('Implement in subclass')

    def get_list_headers(self):
        raise NotImplementedError('Implement in subclass')

    async def get_list(self, request_handler):
        raise NotImplementedError('Implement in subclass')

    async def get_object(self, request, id):
        raise NotImplementedError('Implement in subclass')

    async def get_form_data(self, obj):
        raise NotImplementedError('Implement in subclass')

    def get_form(self, request_handler):
        raise NotImplementedError('Implement in subclass')

    async def save_model(self, request_handler, form, obj=None):
        raise NotImplementedError('Implement in subclass')
