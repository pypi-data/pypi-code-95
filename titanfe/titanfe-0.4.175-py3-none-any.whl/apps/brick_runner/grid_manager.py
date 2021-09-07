#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#
"""GridManager communication"""

import json
from http import HTTPStatus

from aiohttp.client_exceptions import ClientError
from aiohttp_requests import requests

from titanfe import log as logging
from titanfe.config import configuration


class GridManager:
    """GridManager """

    def __init__(self, runner_uid, brick_uid):
        self.runner_uid = runner_uid
        self.brick_uid = brick_uid
        self.log = logging.TitanPlatformLogger(__name__)

    @property
    def address(self):
        return configuration.gridmanager_address

    async def register_runner(self, runner_address):
        """register brick runner at grid manager"""
        payload = {
            "runnerID": self.runner_uid,
            "address": "%s:%s" % runner_address,
            "brickId": self.brick_uid,
        }
        response = await requests.post(f"{self.address}/brickrunners/", data=json.dumps(payload))
        if response.status != HTTPStatus.OK:
            error = ClientError(f"Failed to register at GridManager: {response!r}")
            self.log.with_context.error(error)
            raise error

        return await response.json()

    async def deregister_runner(self):
        """deregister brick runner at grid manager"""
        payload = {"runnerId": self.runner_uid, "brickId": self.brick_uid}
        await requests.post(f"{self.address}/brickrunners/deregister", data=json.dumps(payload))
        self.log.debug("Deregister: %r", payload)

    async def request_scaling(self, consumer_uid):
        """send brick scaling request"""
        payload = {"brickId": self.brick_uid, "consumerId": consumer_uid}
        try:
            await requests.post(f"{self.address}/brickrunners/scaling", data=json.dumps(payload))
            self.log.debug("Requested scaling: %r", payload)
        except ClientError as error:
            self.log.warning("ScalingRequest failed %s: %s", error, payload)
