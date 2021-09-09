from ubotadapter.bots import Telegram
from ubotadapter.inbound import EchoInboundProcessor

def test_msg():
    tgbot = Telegram('data/telegram.json')
    tgbot.set_inbound_processor(EchoInboundProcessor)
    response = tgbot.handle({
        'update_id': 350516797,
        'message': {
            'message_id': 9,
            'from': {
                'id': 37610330,
                'is_bot': False,
                'first_name': 'Igor',
                'last_name': 'Shephard',
                'username': 'smyek',
                'language_code': 'en'
            },
            'chat': {
                'id': 37610330,
                'first_name': 'Igor',
                'last_name': 'Shephard',
                'username': 'smyek',
                'type': 'private'
            },
            'date': 1622413728,
            # 'text': 'reply_to_message'
            'text': 'test_text'
        }
    })
    return response


if __name__ == '__main__':
    import logging
    logging.getLogger('ubotadapter').addHandler(logging.StreamHandler())
    test_msg()
