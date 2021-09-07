# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Routes for Flow management"""

import asyncio
from fastapi import APIRouter
from pydantic import BaseModel  # pylint: disable=no-name-in-module

# Request Parameter
from titanfe.apps.control_peer.brick import BrickInstanceDefinition, BrickBaseDefinition
from titanfe import log as logging


log = logging.getLogger(__name__)


class RequestBrickStart(BaseModel):  # pylint: disable=too-few-public-methods
    brick: dict


class RequestInstallBricks(BaseModel):  # pylint: disable=too-few-public-methods
    bricks: list


# Routes
def create_brick_router(control_peer):
    """Setup the routing for flow management

    Arguments:
        control_peer (ControlPeer): an instance of the ControlPeer

    Returns:
        APIRouter: router/routes to manage the control peer's flows
    """

    router = APIRouter()

    @router.put("/{brick_uid}")
    async def change_state(  # pylint: disable=unused-variable
        brick_uid: str, request: RequestBrickStart  # pylint: disable=unused-argument
    ):
        await control_peer.start_new_runner(
            brick=BrickInstanceDefinition.from_gridmanager(request.brick)
        )

    @router.post("/install")
    async def install_bricks(  # pylint: disable=unused-variable
        request: RequestInstallBricks,  # pylint: disable=unused-argument
    ):
        for brick in request.bricks:
            brick_id = brick.get("id")

            task = asyncio.create_task(
                BrickBaseDefinition(
                    uid=brick_id, name=brick.get("name"), logger=log
                ).install_or_update(force_update=True)
            )
            task.brick_id = brick_id

            control_peer.tasks[brick_id] = task
            task.add_done_callback(lambda t: control_peer.tasks.pop(t.brick_id))

    return router
