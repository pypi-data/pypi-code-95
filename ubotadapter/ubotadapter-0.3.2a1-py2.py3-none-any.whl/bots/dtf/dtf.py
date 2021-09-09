import itertools

from deteefapi import DeteefAPI
from deteefapi.webhook import CommentCreator

from ubotadapter import UBotAdapter, BotInfo, ChannelType, BotMessage, BotReplyStatus, BotContext
from ubotadapter.logger import logger
from .inbound import DTFInboundMessage


class DTF(UBotAdapter):
    channel = ChannelType.DTF
    _info = BotInfo(name=ChannelType.DTF.name)
    _InboundMessageClass = DTFInboundMessage

    def _init_api(self):
        self._api = DeteefAPI(self.config.token)

    @property
    def api(self) -> DeteefAPI:
        return self._api

    def check_webhook(self) -> (bool, str):
        webhook_data = self.api.get_webhook()
        is_set = webhook_data.is_webhook(self.config.webhook_url, event_type='new_comment')
        webhook_url = webhook_data.get_url()
        if is_set and webhook_url == self.config.webhook_url:
            return True, webhook_url
        return False, webhook_url

    def set_webhook(self) -> bool:
        response = self.api.set_webhook(self.config.webhook_url, event='new_comment')
        result = response.json()['result']
        return response.status_code == 200 and result['url'] == self.config.webhook_url

    def disable_webhook(self) -> bool:
        response = self.api.delete_webhook(webhook_url=self.config.webhook_url, event='new_comment')
        result = response.json()['result']
        return response.status_code == 200 and result['success']

    def reset_webhook(self) -> (bool, str):
        webhook_data = self.api.get_webhook()
        webhook_url = webhook_data.get_url()
        if webhook_url:
            self.api.delete_webhook(webhook_url=webhook_url, event='new_comment')
        is_ok, url = self.set_webhook(), self.config.webhook_url
        return is_ok, url

    def update_webhook(self) -> (bool, str):
        is_ok, url = self.check_webhook()
        if not is_ok:
            self.reset_webhook()
        return self.check_webhook()

    def reply(self, context: BotContext, message: BotMessage) -> (bool, BotReplyStatus):
        text = message.text
        post_id = context.inbound.chat_id
        reply_to = context.inbound.message_id
        if message.keyboard:
            buttons_chain = itertools.chain.from_iterable(message.keyboard.buttons)
            buttons_text_list = [f'{i + 1}. {btn}' for i, btn in enumerate(buttons_chain)]
            buttons_text = '\n'.join(buttons_text_list)
            if not text:
                text = buttons_text
            else:
                text += '\n' + buttons_text
        response = self.api.comment_send(post_id=post_id, text=text, reply_to=reply_to)
        if response.status_code == 200:
            return True, BotReplyStatus.ok
        logger.error(f'DTF error response: {response.json()}')
        return False, BotReplyStatus.unknown_error

    def get_user_data(self, inbound: DTFInboundMessage) -> CommentCreator:
        return inbound.user_data
