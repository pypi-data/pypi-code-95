from typing import List

from ubotadapter import BotContext, InboundMessage, BotMessage
from ubotadapter.botmsg import Keyboard
from ubotadapter.inbound import InboundProcessor

MARKER = 'utest_cmnd_in'


def wrap_buttons(buttons: List[List[str]]):
    for i in range(len(buttons)):
        for j in range(len(buttons[i])):
            buttons[i][j] = f'{MARKER} {buttons[i][j]}'
    return buttons


class TestingInboundProcessor(InboundProcessor):
    @staticmethod
    def process(context: BotContext, inbound: InboundMessage):
        text = inbound.text.lower()
        tokens = text.split(' ')
        set_tokens = set(tokens)
        if MARKER not in set_tokens:
            return

        reply_text = ''
        keyboard = None
        data = {}

        if 'echo' in set_tokens:
            reply_text = inbound.text
        elif 'say my name' in text:
            reply_text = f'OK – {inbound.user.visual_name}'
        elif 'reply to me' in text:
            reply_text = f'Replying.'
            data['is_reply_to_message'] = True
        elif 'buttons' in set_tokens:
            in_line = 'in_line' in set_tokens or 'inline' in set_tokens
            reply_text = 'Выбери'
            buttons = [['echo', 'say my name'], ['buttons', 'reply to me']]
            buttons = wrap_buttons(buttons)
            keyboard = Keyboard(buttons=buttons, one_time=False, in_line=in_line)

        if reply_text:
            data['text'] = reply_text
            if keyboard:
                data['keyboard'] = keyboard
            message = BotMessage(**data)
            context.replies.add(message)


