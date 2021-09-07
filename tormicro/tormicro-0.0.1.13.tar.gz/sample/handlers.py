import json
import logging
from abc import ABC
from typing import Dict

import tornado
from tormicro.rest import mediatypes
from tormicro.rest import get, post, put, delete
from tornado_swagger.model import register_swagger_model

from sample.service import AddressBookService
from tormicro import AppContext
from tormicro.app import BaseRestHandler

class AddressBookRestHandler(BaseRestHandler, ABC):
    URI_PATTERN = r'/addresses/?'

    def initialize(
            self,
            config: Dict,
            logger: logging.Logger
    ) -> None:
        super(AddressBookRestHandler, self).initialize(config, logger)
        self.service: AddressBookService = AppContext.get_service(AddressBookService, config, logger)

    @get(_path='/addresses', _produces=mediatypes.APPLICATION_JSON)
    async def getAddresses(self):
        all_addrs = {}
        async for nickname, addr in self.service.get_all_addresses():
            all_addrs[nickname] = addr

        self.set_status(200)
        await self.finish(all_addrs)

    @post(_path='/addresses', _types=[dict], _produces=mediatypes.APPLICATION_JSON)
    async def createAddress(self, addr):
        try:
            id = await self.service.create_address(addr)
            addr_uri = f'/addresses/{id}'
            self.set_status(201)
            self.set_header('Location', addr_uri)
            await self.finish()
        except (json.decoder.JSONDecodeError, TypeError):
            raise tornado.web.HTTPError(
                400, reason='Invalid JSON body'
            )
        except ValueError as e:
            raise tornado.web.HTTPError(400, reason=str(e))

    @get(_path='/addresses/{aid}', _types=[str], _produces=mediatypes.APPLICATION_JSON)
    async def getAddressById(self, aid: str):
        """
        ---
        tags:
          - AddressBookEntries
        summary: Get addressbook entry details
        description: addressbook entry full version
        produces:
          - application/json
        parameters:
          - name: aid
            in: path
            description: ID of addressbook entry to return
            required: true
            type: string
        responses:
          200:
            description: list of addressbook entries
            schema:
              type: object
              description: Post model representation
              properties:
                full_name:
                  type: string
                addresses:
                  type: array
                  items:
                    type: string
                phone_numbers:
                  type: array
                  items:
                    type: string
                fax_numbers:
                  type: array
                  items:
                    type: string
                emails:
                  type: array
                  items:
                    type: string
        """
        try:
            addr = await self.service.get_address(aid)
            self.set_status(200)
            await self.finish(addr)
        except KeyError as e:
            raise tornado.web.HTTPError(404, reason=str(e))

    @put(_path='/addresses/{aid}', _types=[str, dict], _produces=mediatypes.APPLICATION_JSON)
    async def updateAddressById(self, aid, addr):
        try:
            await self.service.update_address(aid, addr)
            self.set_status(204)
            await self.finish()
        except (json.decoder.JSONDecodeError, TypeError):
            raise tornado.web.HTTPError(
                400, reason='Invalid JSON body'
            )
        except KeyError as e:
            raise tornado.web.HTTPError(404, reason=str(e))
        except ValueError as e:
            raise tornado.web.HTTPError(400, reason=str(e))

    @delete(_path='/addresses/{aid}', _types=[str], _produces=mediatypes.APPLICATION_JSON)
    async def deleteAddressById(self, aid):
        try:
            await self.service.delete_address(aid)
            self.set_status(204)
            await self.finish()
        except KeyError as e:
            raise tornado.web.HTTPError(404, reason=str(e))


@register_swagger_model
class PostModel:
    """
    ---
    type: object
    description: Post model representation
    properties:
        id:
            type: integer
            format: int64
        title:
            type: string
        text:
            type: string
        is_visible:
            type: boolean
            default: true
    """
    pass
