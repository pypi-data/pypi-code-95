from jsonrpc2_base.plugins.client.client_plugin_base import ClientPluginBase

class ApiExceptionFilter(ClientPluginBase):
    def exceptionCatch(self, exception):
        if exception.getCode() >= 0:
            raise Exception(exception.getMessage(), exception.getCode())
        else:
            raise exception
