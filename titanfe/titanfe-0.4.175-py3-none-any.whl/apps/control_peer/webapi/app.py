# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Provide a RESTlike interface to manage the ControlPeer remotely"""

import socket

from fastapi import FastAPI
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from uvicorn import Server, Config

from titanfe.config import configuration
from .bricks import create_brick_router
from .flows import create_flow_router


class HelloWorld(BaseModel):  # pylint: disable=too-few-public-methods
    message: str = "Hello, World!"


class WebApi:
    """Provide a RESTlike interface to manage the ControlPeer remotely

    Arguments:
        control_peer (ControlPeer): an instance of the ControlPeer

    Usage:
        create an Instance of the WebAPI (glued together with FastAPI/Starlette and uvicorn)
        and use `run` to create an endlessly running asyncio task
        or use the `serve` coroutine to run it manually
    """

    def __init__(self, control_peer):
        self.server = None

        self.api = FastAPI(
            title="Titan ControlPeer WebApi",
            version="1.0",
            description="A RESTlike interface to manage the ControlPeer remotely",
        )

        self.api.get("/hello", response_model=HelloWorld)(
            lambda: HelloWorld()  # pylint: disable=unnecessary-lambda  # it's necessary!
        )

        brick_router = create_brick_router(control_peer)
        self.api.router.include_router(brick_router, prefix="/api/v1/bricks", tags=["Bricks"])

        flow_router = create_flow_router(control_peer)
        self.api.router.include_router(flow_router, prefix="/api/v1/flows", tags=["Flows"])

        ip_address = configuration.IP or socket.gethostbyname(socket.gethostname())
        self.server = Server(config=Config(self.api, host=ip_address))

        # we will handle signals ourselves. thank you.
        self.server.install_signal_handlers = lambda: None

    @property
    def address(self):
        return self.server.config.host + ":" + str(self.server.config.port)

    async def stop(self):
        self.server.should_exit = True
        await self.server.shutdown()

    async def serve(self):
        """serve the api using uvicorn"""
        await self.server.serve()
