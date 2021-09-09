import json

from vkale import VKaleAPI

from ubotadapter import UBotAdapter, BotInfo, ChannelType
from ubotadapter.botdebug import *
from ubotadapter.uhttp import *
from ubotadapter.logger import logger
from .inbound import VKInboundMessage


class VK(UBotAdapter):
    channel = ChannelType.VK
    _default_server_name = 'main'
    _InboundMessageClass = VKInboundMessage
    _info = BotInfo(channel=ChannelType.VK)

    def _init_api(self):
        self._api = VKaleAPI(self.config.token)

        if self.config.get('server_name'):
            self._default_server_name = self.config['server_name']

    @property
    def api(self) -> VKaleAPI:
        return self._api

    def set_webhook(self):
        server = self.api.groups.get_callback_server_by_name(group_id=self.config.bot_id,
                                                             server_name=self._default_server_name)
        if not server:
            server_id = self.api.groups.add_callback_server(group_id=self.config.bot_id,
                                                            url=self.config.webhook_url,
                                                            title=self._default_server_name,
                                                            secret_key=self.config.webhook_secret)
            server = self.api.groups.get_callback_servers(group_id=self.config.bot_id, servers_id=server_id)[0]
        response = self.api.groups('editCallbackServer',
                                   group_id=self.config.bot_id,
                                   server_id=server.id,
                                   url=self.config.webhook_url,
                                   title=self._default_server_name,
                                   secret_key=self.config.webhook_secret)
        response = self.api.groups.set_callback_settings(group_id=self.config.bot_id,
                                                         server_id=server.id,
                                                         message_new=1)

        if not response:
            raise Exception(f'Cant add server {response}')

        return response

    def disable_webhook(self) -> bool:
        server = self.api.groups.get_callback_server_by_name(group_id=self.config.bot_id,
                                                             server_name=self._default_server_name)
        if server:
            response = self.api.groups.set_callback_settings(group_id=self.config.bot_id,
                                                             server_id=server.id,
                                                             message_new=0)
            return response == 1
        return True

    def check_webhook(self) -> (bool, str):
        server = self.api.groups.get_callback_server_by_name(group_id=self.config.bot_id,
                                                             server_name=self._default_server_name)
        if not server:
            return False, ''
        settings = self.api.groups.get_callback_settings(group_id=self.config.bot_id,
                                                         server_id=server.id)
        status = server.url == self.config.webhook_url and settings.message_new == 1  # server.status == 'ok'
        return status, server.url

    def reset_webhook(self) -> (bool, str):
        self.disable_webhook()
        return self.update_webhook()

    def update_webhook(self) -> (bool, str):
        is_ok, url = self.check_webhook()
        if not is_ok or url != self.config.webhook_url:
            self.set_webhook()
            return self.check_webhook()
        return is_ok, url

    def reply(self, context, message):
        def serializer_button(text):
            return {
                "action": {
                    "type": "text",
                    # "payload": "{\"button\": \"1\"}",
                    "label": text
                },
                "color": "secondary"
            }

        params = dict(peer_id=context.inbound.chat_id,
                      message=message.text,
                      random_id=0)

        if message.is_reply_to_message:
            message_id = message.reply_to_message if message.reply_to_message else self.context.inbound.message_id
            if self.context.inbound.is_private:
                params['reply_to'] = message_id

        if message.keyboard:
            buttons = list(message.keyboard.serialize_buttons(serializer_button))
            keyboard = {
                'buttons': buttons,
                'inline': message.keyboard.in_line,
                'one_time': message.keyboard.one_time and not message.keyboard.in_line
            }
            params['keyboard'] = json.dumps(keyboard)

        response = self.api.method(method_name='messages.send', **params)
        # Success
        if response and 'response' in response:
            if isinstance(response['response'], int):
                return True, BotReplyStatus.ok
        # Errors
        logger.error(f'VK error response: {response}')
        if 'error' in response:
            code = response['error']['error_code']
            if code == 901:
                return False, BotReplyStatus.no_permission
            raise ValueError(response)
        return False, BotReplyStatus.unknown_error

    def get_confirmation_code(self) -> str:
        code = self.api.groups.get_callback_confirmation_code(group_id=self.config.bot_id)
        return code

    def get_user_data(self, inbound: VKInboundMessage):
        return self.api.users.get(user_ids=inbound.user_id)[0]

    def get_prehandle_webhook_response(self, data: dict) -> Union[UBotHTTPResponse, None]:
        if data.get('type', None) == 'confirmation':
            logger.info('vk confirmation')
            return UBotHTTPResponse(self.get_confirmation_code(), status=200, is_forced_response=True)
        return None


if __name__ == '__main__':
    vkubot = VK('config/vk.json')
    print(vkubot.check_webhook())
