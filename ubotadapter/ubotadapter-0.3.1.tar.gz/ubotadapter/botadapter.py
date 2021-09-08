import json
import traceback
from abc import ABC, abstractmethod
from functools import partial
from typing import Union, Type

import backoff as backoff

from .botconfig import BotConfig
from .botcontext import BotContext
from .botdebug import *
from .botinfo import BotInfo
from .botmsg import BotMessage
from .enums import ChannelType
from .inbound import InboundProcessor, InboundMessage, DefaultInboundProcessor, InboundMessageFactory
from .logger import logger
from .msgfilter import MessageFilterManager, NotBotMessage
from .uhttp import *


class UBotAdapter(ABC):
    channel: ChannelType = None
    _info = None
    _BotContextClass = BotContext
    _BotMessageClass = BotMessage
    _inbound_message_factory = InboundMessageFactory
    _InboundMessageClass = InboundMessage
    _InboundProcessorClass = DefaultInboundProcessor
    _success_webhook_response = DEFAULT_SUCCESS_HTTP_RESPONSE

    __slots__ = ('_api', '_config', '_context', '_inbound_processor', '_message_filters_manager')

    def __init__(self, config: Union[str, dict, BotConfig]):
        """config. str == path, dict -> config"""
        if isinstance(config, str):
            config = BotConfig(self._load_config(config))
        elif isinstance(config, dict):
            config = BotConfig(config)
        self._config = config
        # info
        self.info.name = self.config.name or f'{self.channel.name}_{self.config.bot_id}'
        # API
        self._api = None
        self._inbound_processor = self._InboundProcessorClass
        self._init_api()
        self._message_filters_manager = MessageFilterManager([NotBotMessage])
        self._context = self._BotContextClass(self)
        logger.debug(f'Bot "{self.channel.name}" with name "{self.info.name}" initialized')

    @property
    @abstractmethod
    def api(self):
        return self._api

    @property
    def context(self) -> _BotContextClass:
        return self._context

    @property
    def inbound_message_factory(self):
        return self._inbound_message_factory(self._InboundMessageClass)

    def _init_api(self):
        return None

    @property
    def info(self) -> BotInfo:
        return self._info

    @property
    def message_filters_manager(self) -> MessageFilterManager:
        return self._message_filters_manager

    @staticmethod
    def _load_config(path) -> dict:
        """
        token: str
        webhook_url: str
        confirmation_code (optional): str
        :param str path:
        :return: dict config
        """
        with open(path, 'r') as f:
            return json.load(f)

    # region Webhooks
    @abstractmethod
    def check_webhook(self) -> (bool, str):
        """Check if webhook is set"""
        pass

    @property
    def is_webhook_set(self) -> bool:
        """Check if webhook is online"""
        is_ok, url = self.check_webhook()
        return is_ok

    @abstractmethod
    def set_webhook(self) -> bool:
        pass

    @abstractmethod
    def disable_webhook(self) -> bool:
        pass

    @abstractmethod
    def reset_webhook(self) -> (bool, str):
        pass

    @abstractmethod
    def update_webhook(self) -> (bool, str):
        """Check if webhook is relevant, is set and active, if not - set"""
        pass

    # endregion

    @abstractmethod
    def reply(self, context: BotContext, message: BotMessage) -> (bool, BotReplyStatus):
        """Returns (True, BotReplyStatus.ok) if success, (False, BotReplyStatus.<error>) if not"""
        pass

    @property
    def config(self) -> BotConfig:
        return self._config

    @property
    def inbound_processor(self) -> Type[InboundProcessor]:
        return self._inbound_processor

    def handle(self, data) -> BotHandleResult:
        self.context.clear()  # TODO: is it necessary?

        logger.debug('serialize inbound')
        inbound = self._init_inbound(data)

        # process inbound message
        logger.debug('processing')
        if inbound:
            if inbound.secret_code and self.config.webhook_secret != inbound.secret_code:
                data = {'webhook': self.config.webhook_secret, 'inbound': inbound.secret_code}
                self.context.handle_result.process_result = BotProcessResult(BotProcessStatus.wrong_secret, data=data)
            else:
                self.context.handle_result.process_result = self._process(inbound)

        # reply
        logger.debug('replying')
        if not self.context.replies.count:
            logger.info('No messages in replies')
        for message in self.context.replies:
            if self.is_message_valid(message):
                self.context.handle_result.reply_result = self._reply(message)
            else:
                logger.info('Warning: no message')
                self.context.handle_result.reply_result = BotReplyResult(BotReplyStatus.ok)

        return self.context.handle_result

    @property
    def success_webhook_response(self) -> UBotHTTPResponse:
        return self._success_webhook_response

    def get_prehandle_webhook_response(self, data) -> Union[UBotHTTPResponse, None]:
        """returned response should be sent before main processing"""
        pass

    def set_inbound_processor(self, processor: Type[InboundProcessor]):
        self._inbound_processor = processor

    def _init_inbound(self, data) -> InboundMessage:
        inbound = None
        try:
            inbound = self.inbound_message_factory.create(data)
            inbound.user.set_user_data_getter(partial(self.get_user_data, inbound))
            self.context.inbound = inbound  # TODO: why set inbound?
        except Exception as e:
            self.context.handle_result.process_result = BotProcessResult(BotProcessStatus.inbound_error,
                                                                         exception=traceback.format_exc())
            raise e
        return inbound

    def _process(self, inbound: InboundMessage) -> BotProcessResult:
        # filtering
        not_passed_filter = self.message_filters_manager.check(self.context, inbound)
        if not_passed_filter is not None:
            return BotProcessResult(BotProcessStatus.filter_not_passed, data=not_passed_filter.__name__)
        # main process
        try:
            result = self.inbound_processor.process(self.context, inbound)
            return BotProcessResult(BotProcessStatus.ok, data=result)
        except Exception as e:
            logger.error(f'Failed on _process with exception: {repr(e)}')
            if self.config.is_send_process_error_message:
                self.context.replies.add(BotMessage(self.inbound_processor.error_message_default))
            return BotProcessResult(BotProcessStatus.unknown_error, exception=traceback.format_exc())

    @backoff.on_exception(backoff.expo,
                          BotReplyException,
                          max_tries=10,
                          max_time=60)
    def _reply(self, message) -> (bool, BotReplyStatus):
        try:
            is_ok, reply_status = self.reply(self.context, message)
            if not is_ok:
                logger.error(f'No reply: {reply_status}')
            return BotReplyResult(reply_status, exception=reply_status)
        except Exception as e:
            error_msg = f'Failed on _process with exception: {repr(e)}'
            logger.error(error_msg, exc_info=1)
            return BotReplyResult(BotReplyStatus.unknown_exception, exception=traceback.format_exc())

    def is_message_valid(self, message: BotMessage) -> bool:
        return isinstance(message, BotMessage) and message.has_content

    @abstractmethod
    def get_user_data(self, inbound: InboundMessage):
        pass
