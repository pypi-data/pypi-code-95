#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""The BrickAdapter get's passed into the brick's module on execution"""
from collections import namedtuple
from dataclasses import dataclass
from Crypto.Cipher import AES

from titanfe.repository import RepositoryService
from titanfe.utils import generate_key
from ...config import configuration

MetaData = namedtuple("MetaData", "uid name")

NONCE_LEN = 12
TAG_LEN = 16


@dataclass
class AdapterMeta:
    """ flow/brick meta data to be made available for access inside a brick """

    brick: MetaData
    flow: MetaData

    def __post_init__(self):
        self.brick = MetaData(*self.brick)
        self.flow = MetaData(*self.flow)


class BrickAdapter:  # pylint: disable=too-few-public-methods
    """The BrickAdapter get's passed into the brick's module on execution

    Arguments:
            result_put_callback (Callable): callback to output a result to the runner
            log (logging.Logger): the logger instance of the parent runner

    Attributes
        log: a logging.logger instance to be used from within the brick's module
            if one wants to have something in the general application log.
    """

    def __init__(self, meta_data: AdapterMeta, result_put_callback, log, default_port):
        self.meta = meta_data

        self.log = log.getChild(f"BrickAdapter.{self.meta.brick.name}")
        self.state = State(self.meta.flow.uid, self.meta.brick.uid, self.log)

        self.__put_packet = result_put_callback
        self.__default_port = default_port

        # TODO: deprecate:
        self.terminated = False
        self.stop_processing = lambda: None

    def emit_new_packet(self, value, port=None):
        """A new packet will be created from the given value and infused into the flow of data.

        Note:
            This will create and output a new packet into the flow.
            To modify the payload of an already travelling packet,
            simply return a value from the brick processing method.

        Args:
            value (Any): Any value
        """

        self.log.debug(
            "brick emitted new value: %r , port: %s" % (value, port or self.__default_port)
        )
        self.__put_packet((value, port or self.__default_port))

    def decrypt_parameter(self, parameter):  # pylint: disable=no-self-use
        """Decrypt a secret parameter using AES GCM

        Args:
            parameter(String): hex encoded encryped parameter
        """

        key = generate_key(bytes(configuration.secret_key, 'utf-8'),
                           bytes(self.meta.flow.uid, 'utf-8'))
        parameter_bytes = bytes.fromhex(parameter)
        nonce = parameter_bytes[:NONCE_LEN]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

        encrypted_parameter = parameter_bytes[NONCE_LEN:len(parameter_bytes)-TAG_LEN]
        decrypted_parameter = cipher.decrypt(encrypted_parameter)
        return decrypted_parameter.decode()


class State:
    """State allows bricks to persist/get state and the brick runner to reset it
    during teardown"""

    def __init__(self, flow_id, brick_uid, log):
        self.log = log.getChild(f"BrickState.{brick_uid}")
        self.__repository_service = RepositoryService(self.log)
        self.collection = flow_id
        self.document = brick_uid

    def set(self, value):
        """Store brick state
        Args:
            value (Any):  state to be stored
        """
        self.log.debug(
            "inserting %r to document %r of collection %r" % (value, self.document, self.collection)
        )
        self.__repository_service.store(self.collection, self.document, value)

    def reset(self):
        """Delete brick state
        """
        self.log.debug("deleting document %r of collection %r" % (self.document, self.collection))
        self.__repository_service.delete(self.collection, self.document)

    def get(self):
        """Getting brick state"""

        self.log.debug("getting document %s of collection %r" % (self.document, self.collection))
        return self.__repository_service.get(self.collection, self.document, None).response
