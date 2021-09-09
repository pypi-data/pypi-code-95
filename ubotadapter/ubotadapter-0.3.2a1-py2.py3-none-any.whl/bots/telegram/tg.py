import telegram
from telegram import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from ubotadapter import UBotAdapter, BotInfo, ChannelType
from ubotadapter.botdebug import *
from ubotadapter.logger import logger
from .inbound import TGInboundMessage, TGInboundMessageFactory


class Telegram(UBotAdapter):
    channel = ChannelType.Telegram
    _info = BotInfo(channel=ChannelType.Telegram)
    _inbound_message_factory = TGInboundMessageFactory
    _InboundMessageClass = TGInboundMessage

    def _init_api(self):
        self._api = telegram.Bot(self.config.token)

    @property
    def api(self) -> telegram.Bot:
        return self._api

    def reply(self, context, message):
        def serialize_inline_button(text: str, callback_data: str = None, **kwargs):
            return InlineKeyboardButton(text=text, callback_data=callback_data or text, **kwargs)

        params = dict(chat_id=self.context.inbound.chat_id, text=message.text)
        # buttons
        if message.keyboard:
            if message.keyboard.in_line:
                keyboard = message.keyboard.serialize_buttons(serialize_inline_button)
                reply_markup = InlineKeyboardMarkup(keyboard)
            else:
                keyboard = message.keyboard.serialize_buttons(KeyboardButton)
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=message.keyboard.one_time)

            params.update(reply_markup=reply_markup)
        # reply to
        if message.is_reply_to_message or message.reply_to_message:
            message_id = message.reply_to_message if message.reply_to_message else self.context.inbound.message_id
            params.update(reply_to_message_id=message_id)
        response = self.api.send_message(**params)
        if response and response.message_id:
            return True, BotReplyStatus.ok
        logger.error(f'Reply {self.channel} error: ' + response)
        return False, BotReplyStatus.unknown_error

    def check_webhook(self):
        info = self.api.get_webhook_info()
        is_ok = bool(info.url) and info.url == self.config.webhook_url
        return is_ok, info.url

    def delete_webhook(self) -> bool:
        return self.api.delete_webhook()

    def set_webhook(self) -> bool:
        return self.api.set_webhook(url=self.config.webhook_url)

    def disable_webhook(self) -> bool:
        return self.api.delete_webhook()

    def update_webhook(self) -> (bool, str):
        info = self.api.get_webhook_info()
        if info.url != self.config.webhook_url:
            if info.url:
                self.disable_webhook()
            self.set_webhook()
        return self.check_webhook()

    def reset_webhook(self) -> (bool, str):
        self.disable_webhook()
        self.set_webhook()
        return self.check_webhook()

    def get_user_visual_name(self, inbound: TGInboundMessage) -> str:
        return inbound.user_visual_name

    def get_user_data(self, inbound: TGInboundMessage):
        return inbound.user_data


if __name__ == '__main__':
    tgbot = Telegram('config/telegram.json')
    print(tgbot.check_webhook())
