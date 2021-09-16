import os, requests

from typing import List, Tuple, AnyStr


def _get_vars(params: List[Tuple], kw: dict) -> List[AnyStr]:
    result = []

    for kw_name, env_name in params:
        env_name = f'MY_{env_name}'
        if kw_name in kw:
            result.append(kw[kw_name])
        elif env_name in os.environ:
            result.append(os.environ[env_name])
        else:
            raise RuntimeError("missing parameter '%s' or variable '%s'" % (kw_name, env_name))

    return result


def telegram_notify(text: str,
                    parse_mode: str = None,
                    disable_web_page_preview: bool = False,
                    **kwargs):
    chat_id, token = _get_vars([
        ('chat_id', 'TELEGRAM_CHAT_ID'),
        ('token', 'TELEGRAM_TOKEN')
    ], kwargs)

    data = {
        'chat_id': chat_id,
        'text': text
    }
    if parse_mode is not None:
        data['parse_mode'] = parse_mode
    if disable_web_page_preview:
        data['disable_web_page_preview'] = 1

    r = requests.post('https://api.telegram.org/bot%s/sendMessage' % token, data=data)

    if r.status_code != 200:
        raise RuntimeError("telegram returned %d" % r.status_code)
