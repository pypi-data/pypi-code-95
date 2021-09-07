#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Repository can be used to connect to the titan repository service"""

from http import HTTPStatus
from typing import Any, Optional, Callable

from dataclasses import dataclass, field
from logging import LoggerAdapter
import requests

from dataclasses_json import dataclass_json

from titanfe.constants import BRICKRUNNER_DATABASE
from titanfe.config import configuration


@dataclass_json
@dataclass
class RequestData:
    """Request data object sent to the Repository service"""

    collection: str
    document: str
    value: Any
    find: Optional[dict] = field(default_factory=dict)
    database: str = BRICKRUNNER_DATABASE


@dataclass
class Request:
    """Request object

     Args:
       address : str       Target address
       method : Callable   requests method(get, put, delete..)
       logger              : the logger instance of the parent
       content: RequestData request content to be sent
    """

    address: str
    method: Callable
    content: RequestData
    log: LoggerAdapter
    response: Any = field(default_factory=dict)

    def send(self):
        """send request """

        if self.content:
            try:
                response = self.method(f"{self.address}/", data=self.content)
                if response.status_code == HTTPStatus.OK:
                    if response.content:
                        self.response = response.json()
                    return
            except requests.ConnectionError:
                self.log.error("Sending request to repo service failed", exc_info=True)
            else:
                self.log.error("Sending request to repo service failed: %r", response)
        return


class RepositoryService:
    """Repository service implements a connection to the titan repository service

    Args:
       brick_name (string) : the name of the brick instance
       logger              : the logger instance of the parent
       repo_service(string) : optional, address of the repository service
    """

    def __init__(self, logger, reposervice_address=None):
        self.address = reposervice_address or configuration.reposervice_address
        self.log = logger.getChild("RepositoryService")

        self.request = None  # for unit testing

    def __create_request(self, method, collection, document, value=None, find=None):
        "create and send request object understood by the repo service"
        request_data = RequestData(  # pylint: disable=no-member
            document=document, collection=collection, value=value, find=find,
        ).to_json()  # pylint: disable=no-member

        self.log.debug("Created request data %r :", request_data)
        return Request(address=self.address, method=method, content=request_data, log=self.log)

    def store(self, collection, document, value):
        "store data using the repository service"
        request = self.__create_request(
            method=requests.patch, collection=collection, document=document, value=value
        )
        request.send()
        return request

    def delete(self, collection, document):
        "delete data using the repository service"
        request = self.__create_request(
            method=requests.delete, collection=collection, document=document
        )
        request.send()
        return request

    def get(self, collection, document, find):
        "get data using the repository service"
        request = self.__create_request(
            method=requests.get, collection=collection, document=document, find=find
        )
        request.send()
        return request
