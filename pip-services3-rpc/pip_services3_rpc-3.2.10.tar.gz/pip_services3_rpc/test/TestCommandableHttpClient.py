# -*- coding: utf-8 -*-
from typing import Optional, Any

from pip_services3_rpc.clients import CommandableHttpClient


class TestCommandableHttpClient(CommandableHttpClient):
    def __init__(self, base_route: str):
        super(TestCommandableHttpClient, self).__init__(base_route)

    def call_command(self, name:str, correlation_id: Optional[str], params: Any) -> Any:
        """
        Calls a remote method via HTTP commadable protocol.
        The call is made via POST operation and all parameters are sent in body object.
        The complete route to remote method is defined as baseRoute + "/" + name.

        :param name: a name of the command to call.
        :param correlation_id: (optional) transaction id to trace execution through the call chain.
        :param params: command parameters.
        :returns: a command execution result.
        """
        return super(TestCommandableHttpClient, self).call_command(name, correlation_id, params)
