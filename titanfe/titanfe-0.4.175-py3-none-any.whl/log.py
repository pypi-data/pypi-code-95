#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""setup the logging with a custom metric-level"""
import sys
import platform
import traceback
from dataclasses import dataclass, asdict
from typing import Optional

import pathlib
import logging
import logging.config
from datetime import datetime

import ruamel.yaml
from kafka import KafkaProducer

from titanfe.config import configuration
from titanfe.ujo_helper import py_to_ujo_bytes


class TitanLogRecord(logging.LogRecord):  # pylint: disable=too-few-public-methods
    """A log record - Titan style"""

    hostname = platform.node()
    servicename = ""
    flowuid = ""
    flowname = ""
    brickuid = ""
    brickname = ""


@dataclass
class FlowContext:
    """ The Flow Context"""

    flowuid: str = ""
    flowname: str = ""
    brickuid: str = ""
    brickname: str = ""

    @classmethod
    def from_flow(cls, flow: "titanfe.apps.control_peer.flow.Flow"):  # noqa
        return cls(flow.uid, flow.name)

    @classmethod
    def from_brick(cls, brick: "titanfe.apps.control_peer.brick.Brick"):  # noqa
        return cls(brick.flow.uid, brick.flow.name, brick.uid, brick.name)

    def asdict(self):
        return asdict(self)


class TitanLogAdapter(logging.LoggerAdapter):
    """The Log Adapter wraps a logger and adds some context to each log record"""

    def getChild(self, suffix):  # pylint: disable=invalid-name
        logger = self.logger.getChild(suffix)
        return TitanLogAdapter(logger, self.extra)

    @property
    def context(self):
        return self.extra

    @context.setter
    def context(self, new):
        self.extra.clear()
        if isinstance(new, FlowContext):
            new = new.asdict()
        self.extra.update(new)


class TitanPlatformLogger(logging.Logger):
    """to write contextual logging information use e.g. `log.with_context.info`"""

    def __new__(cls, name, context: Optional[FlowContext] = None):
        # pylint: disable=unused-argument
        logger = logging.getLogger(name)
        logger.__class__ = cls
        return logger

    def __init__(self, name, context: Optional[FlowContext] = None):
        # pylint: disable=super-init-not-called, unused-argument
        if isinstance(context, FlowContext):
            context = context.asdict()
        self.context = context
        self.context_logger = TitanLogAdapter(self, context or global_context)

    def getChild(self, suffix) -> "TitanPlatformLogger":  # pylint: disable=invalid-name
        if self.root is not self:
            suffix = ".".join((self.name, suffix))
        logger = TitanPlatformLogger(suffix, self.context)
        return logger

    @property
    def with_context(self):
        return self.context_logger


global_context = {}  # pylint: disable=invalid-name


def getLogger(  # pylint: disable=invalid-name ; noqa: N802
    name: str, context: Optional[FlowContext] = None
) -> logging.Logger:
    """ Get a Logger
    Args:
        name: the logger name
        context: a flow context (if available)

    Returns:
        logging.Logger: a Logger
    """
    if not name.startswith("titanfe."):
        name = f"titanfe.bricks.{name}"

    logger = logging.getLogger(name)

    if context is not None:
        if isinstance(context, FlowContext):
            context = context.asdict()
        logger = TitanLogAdapter(logger, context)

    elif global_context:
        logger = TitanLogAdapter(logger, global_context)

    return logger


def initialize(service=""):
    """ initialize the titan logging module, e.g. set up a KafkaLogHandler

    Args:
        service: name of the current service
    """
    TitanLogRecord.servicename = service

    log_config_file = pathlib.Path(__file__).parent / "log_config.yml"
    with open(log_config_file) as cfile:
        log_config = ruamel.yaml.safe_load(cfile)
        logging.config.dictConfig(log_config)

    if configuration.kafka_bootstrap_servers and not configuration.no_kafka_today:
        kafka_handler = KafkaLogHandler(
            bootstrap_server=configuration.kafka_bootstrap_servers,
            topic=configuration.kafka_log_topic,
        )
        root = logging.getLogger("titanfe")
        root.addHandler(kafka_handler)


def add_logging_level(level, level_name, method_name=None):
    """ add a level to the logging module

    Args:
        level (int): level number
        level_name: name of the level
        method_name: name of the method that gets attached to logging
    """
    if not method_name:
        method_name = level_name.lower()

    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level):
            self._log(level, message, args, **kwargs)  # pylint: disable=protected-access

    def log_to_root(message, *args, **kwargs):
        logging.log(level, message, *args, **kwargs)

    logging.addLevelName(level, level_name)
    setattr(logging, level_name, level)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(TitanLogAdapter, method_name, log_for_level)
    setattr(logging, method_name, log_to_root)


def flush_kafka_log_handler():
    """"Flush messages sent to KafkaLogHandler and
    suppress warnings from kafka
    --> called during shutdown of brick runner"""
    for handler in logging.getLogger("titanfe").handlers:
        if isinstance(handler, KafkaLogHandler):
            handler.flush()
    logging.getLogger('kafka').propagate = False


class UjoBinFormatter(logging.Formatter):
    """ Format log records as an UjoBinary"""

    def format(self, record):
        """ Format a log record as an UjoBinary

        Args:
            record (logging.Record): the log record

        Returns:
            bytes: binary UjoMap
        """
        message = record.getMessage()

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if message[-1:] != "\n":
                message = message + "\n"
            message = message + record.exc_text
        if record.stack_info:
            if message[-1:] != "\n":
                message = message + "\n"
            message = message + self.formatStack(record.stack_info)

        log_entry = {
            "Timestamp": datetime.fromtimestamp(record.created),
            "Severity": record.levelname,
            "Message": message,
            "Hostname": record.hostname,
            "Servicename": record.servicename,
            "Source": record.name,
            "FlowUID": record.flowuid,
            "FlowName": record.flowname,
            "BrickUID": record.brickuid,
            "BrickName": record.brickname,
        }
        ujo_bin_map = py_to_ujo_bytes(log_entry)
        return ujo_bin_map


class KafkaLogHandler(logging.Handler):
    """Stream LogRecords to Kafka

    Arguments:
        bootstrap_server (str): 'Host:Port' of a kafka bootstrap server
        topic (str): the kafka topic to produce into
    """

    def __init__(self, bootstrap_server, topic):
        logging.Handler.__init__(self)
        self.formatter = UjoBinFormatter()
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server)

    def emit(self, record):
        """emits the record"""
        if record.name.startswith("kafka"):
            # drop kafka logging to avoid infinite recursion
            return

        try:
            log_message = self.format(record)
            self.producer.send(self.topic, log_message)
        except Exception:  # pylint: disable=broad-except
            exc_info = sys.exc_info()
            traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], None, sys.stderr)
            del exc_info

    def flush(self):
        self.producer.flush()

    def close(self):
        self.producer.flush()
        self.producer.close()
        logging.Handler.close(self)


logging.setLogRecordFactory(TitanLogRecord)

METRIC_LVL = 5  # between DEBUG & INFO
add_logging_level(METRIC_LVL, "METRIC")
