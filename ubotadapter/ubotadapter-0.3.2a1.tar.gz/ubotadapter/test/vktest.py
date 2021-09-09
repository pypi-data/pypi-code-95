from ubotadapter.bots import VK
from ubotadapter.inbound import EchoInboundProcessor, EchoReplyToInboundProcessor


def get_bot():
    bot = VK('data/vk.json')
    bot.set_inbound_processor(EchoInboundProcessor)
    return bot


def test_msg():
    bot = get_bot()
    bot.handle({
        'type': 'message_new',
        'object': {
            'message': {
                'date': 1624210273,
                'from_id': 4909962,
                'id': 1,
                'out': 0,
                'peer_id': 4909962,
                'text': 'test_ubot',
                'conversation_message_id': 1,
                'fwd_messages': [],
                'important': False,
                'random_id': 0,
                'attachments': [],
                'is_hidden': False
            },
            'client_info': {
                'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback', 'intent_subscribe',
                                   'intent_unsubscribe'],
                'keyboard': True,
                'inline_keyboard': True,
                'carousel': True,
                'lang_id': 0
            }
        },
        'group_id': 204429470,
        'event_id': 'b6ca7d45d8055839911ed53a23f46b8098fe526f'
    }
    )


def test_msg_groupchat():
    bot = get_bot()
    bot.handle({
        'type': 'message_new',
        'object': {
            'message': {
                'date': 1624208087,
                'from_id': 4909962,
                'id': 1,
                'out': 0,
                'peer_id': 2000000001,
                'text': 'qwert',
                'conversation_message_id': 7,
                'fwd_messages': [],
                'important': False,
                'random_id': 0,
                'attachments': [],
                'is_hidden': False
            },
            'client_info': {
                'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback', 'intent_subscribe',
                                   'intent_unsubscribe'],
                'keyboard': True,
                'inline_keyboard': True,
                'carousel': True,
                'lang_id': 0
            }
        },
        'group_id': 204429470,
        'event_id': '78a6cd66ea3b22fb218b9fb7f969868fa85220ae'
    }
    )


if __name__ == '__main__':
    import logging
    from ubotadapter.logger import logger

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

    # fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
    # fileHandler.setFormatter(logFormatter)
    handler = logging.StreamHandler()
    handler.setFormatter(logFormatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    test_msg()
    # test_msg_groupchat()
