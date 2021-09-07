#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#
"""Install a Brick"""
import asyncio
import json
from http import HTTPStatus
from abc import ABC, abstractmethod

from aiohttp.client_exceptions import ClientError
from aiohttp_requests import Requests  # initiate a new client every time,
# because we don't know how many threads are used and each will have it's own asyncio loop
# there must be a better way, but right now I'm short on time...

from titanfe import log as logging
from titanfe.config import configuration

log = logging.getLogger(__name__)


class ServiceError(Exception):
    pass


class ControlPeerServiceRegistration(ABC):
    """BaseClass to handle control peer registration of various services"""
    @property
    @abstractmethod
    def control_peer_endpoint(self):
        pass

    async def register(self, own_api_address):
        """Inquire registration at target_address"""
        while True:
            try:
                requests = Requests()
                response = await requests.post(self.control_peer_endpoint,
                                               json=json.dumps(own_api_address).strip('"'))
                if response.status not in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.ACCEPTED):
                    raise ServiceError(
                        "Failed to register own API <%s> at <%s>: %s"
                        % (
                            own_api_address,
                            self.control_peer_endpoint,
                            HTTPStatus(response.status),  # pylint: disable=no-value-for-parameter
                        )
                    )

                log.info("Successfully registered own API <%s> at <%s>", own_api_address,
                         self.control_peer_endpoint)
                return
            except ClientError:
                log.warning("Failed to register at <%s> - Retry",
                            self.control_peer_endpoint)
                await asyncio.sleep(1)

    async def deregister(self, own_api_address):
        """Cancel registration at target_address"""
        try:
            requests = Requests()
            response = await requests.delete(self.control_peer_endpoint,
                                             json=json.dumps(own_api_address).strip('"'))
        except ClientError:
            log.warning("Removing registration from <%s> - Failed!", self.control_peer_endpoint)
        else:
            if response.status not in (HTTPStatus.OK, HTTPStatus.ACCEPTED):
                log.error(
                    "Removing registration from <%s> failed: %s",
                    self.control_peer_endpoint,
                    HTTPStatus(response.status),  # pylint: disable=no-value-for-parameter
                )
            else:
                log.info("Successfully removed registration from <%s>", self.control_peer_endpoint)


class PackageManager(ControlPeerServiceRegistration):
    """ handle all requests to the package manager """

    @property
    def address(self):
        return f"{configuration.packagemanager_address}"

    @property
    def brick_endpoint(self):
        return f"{self.address}/bricks"

    @property
    def brick_code_endpoint(self):
        return f"{self.address}/source"

    @property
    def control_peer_endpoint(self):
        return f"{self.address}/controlpeers"

    async def get(self, endpoint, context):
        """get endpoint"""
        requests = Requests()

        response = await requests.get(endpoint)
        if response.status != HTTPStatus.OK:
            raise ServiceError(f"{context} failed: {response!r}")

        return await response.read()

    async def get_bricks(self):
        """get bricks"""
        requests = Requests()
        response = await requests.get(self.brick_endpoint)
        if response.status != HTTPStatus.OK:
            raise ServiceError(f"Getting bricks failed: {response!r}")

        return await response.json()

    async def get_source_files(self, brick_id):
        """get the source files archive from the package manager"""
        return await self.get(self.brick_code_endpoint + "/" + brick_id + ".zip",
                              "Downloading source files")


class GridManager(ControlPeerServiceRegistration):
    """handle all requests to the grid manager"""
    @property
    def address(self):
        return f"{configuration.gridmanager_address}"

    @property
    def control_peer_endpoint(self):
        return f"{self.address}/controlpeers"


package_manager = PackageManager()  # pylint: disable=invalid-name
grid_manager = GridManager()  # pylint: disable=invalid-name
