"""Telegram bot"""
import functools
import json
import smtplib
from email.mime.text import MIMEText

import codefast as cf
import requests
from codefast.utils import retry

import dofast.utils as du
from dofast._flask.config import AUTH_KEY
from dofast.pipe import author
from dofast.security._hmac import generate_token
from dofast.utils import get_proxy


@retry()
def message_to_working_bot(text: str, use_proxy: bool = False):
    '''Sent message through bot. Bot chat id is required'''
    api_token = author.get('working_bot')
    bot_chat_id = author.get('working_bot_chat_id')
    url = f"https://api.telegram.org/bot{api_token}/sendMessage?chat_id={bot_chat_id}&text={text}"
    proxies = get_proxy()
    res = requests.get(url, proxies=proxies if use_proxy else None)
    print(res, res.content)


@retry()
def bot_say(api_token: str,
            text: str,
            bot_name: str = 'PlutoShare',
            use_proxy: bool = False):
    url = f"https://api.telegram.org/bot{api_token}/sendMessage?chat_id=@{bot_name}&text={text}"
    proxies = get_proxy()
    res = requests.get(url, proxies=proxies if use_proxy else None)
    print(res, res.content)


def tg_bot(use_proxy: bool = True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _msg = func(*args, **kwargs)
            _token = author.get('mess_alert')
            url = f"https://api.telegram.org/bot{_token}/sendMessage?chat_id=@messalert&text={_msg}"
            res = requests.get(
                url, proxies=get_proxy()) if use_proxy else requests.get(url)
            return res, res.content

        return wrapper

    return decorator


def bot_messalert(msg: str) -> None:
    bot_say(author.get('mess_alert'), msg, bot_name='messalert')


@retry()
def messalert(msg: str) -> None:
    '''send Telegram message via remote consumer'''
    SERVER_HOST = author.get('SERVER_HOST')
    res = cf.net.post(f'http://{SERVER_HOST}:6363/messalert',
                      json={'text': msg},
                      params={'token': generate_token(AUTH_KEY)})
    assert res.text == 'SUCCESS', 'Telegram message failed to send.'


def read_hema_bot():
    bot_updates = author.get('pluto_share')
    print(bot_updates)
    # resp = du.client.get(bot_updates, proxies=get_proxy())
    # print(json.loads(resp.text))


@retry(total_tries=100, initial_wait=0.01, backoff_factor=1)
def download_file_by_id(file_id: str) -> None:
    _token = author.get('hemahema')
    _prefix = f'https://api.telegram.org/bot{_token}'
    _url = _prefix + f'/getFile?file_id={file_id}'
    _path = cf.net.get(_url, proxies=get_proxy()).json()['result']['file_path']
    _full_url = (_prefix + '/' + _path).replace('/bot', '/file/bot')
    target = f'/tmp/{cf.io.basename(_path)}'
    cf.info('Downloading file to ', target)
    cf.net.download(_full_url, name=target, proxies=get_proxy())
    return True


@retry(100, 0.1, 1)
def download_latest_file() -> bool:
    _token = author.get('hemahema')
    _prefix = f'https://api.telegram.org/bot{_token}/getUpdates'
    latest_dict = cf.net.get(_prefix,
                             proxies=get_proxy()).json()['result'].pop()
    fid = None
    if 'photo' in latest_dict['message']:
        fid = latest_dict['message']['photo'].pop()['file_id']
    elif 'video' in latest_dict['message']:
        fid = latest_dict['message']['video']['file_id']
    else:
        cf.warning('unexpected media type', str(latest_dict))

    cf.info('Lastest media file id is', str(fid))
    if fid:
        download_file_by_id(fid)
        return True
    return False


def mail2foxmail(subject: str, message: str):
    r = author.get('FOXMAIL')
    YahooMail().send(r, subject, message)


def mail2gmail(subject: str, message: str):
    r = author.get('GMAIL2')
    YahooMail().send(r, subject, message)


class YahooMail:
    def __init__(self):
        self.smtp_server = "smtp.mail.yahoo.com"
        self.smtp_port = 587
        self.username = author.get('YAHOO_USER_NAME')
        self.password = author.get('YAHOO_USER_PASSWORD')
        self.email_from = self.username + "@yahoo.com"
        mail = smtplib.SMTP(self.smtp_server, self.smtp_port)
        mail.set_debuglevel(debuglevel=True)
        mail.starttls()
        mail.login(self.username, self.password)
        self.mail = mail

    def send(self, receiver: str, subject: str, message: str) -> bool:
        msg = MIMEText(message.strip())
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = receiver

        try:
            du.info("Yahoo mail login success")
            self.mail.sendmail(self.email_from, receiver, msg.as_string())
            du.info(f'SUCCESS[YahooMail.send()]'
                    f'{Message(receiver, subject, message)}')
            # self.mail.quit()
            return True
        except Exception as e:
            du.error("Yahoo mail sent failed" + repr(e))
            return False


class Message:
    def __init__(self, receiver: str, subject: str, message: str):
        self.r = receiver
        self.s = subject
        self.m = message

    def __repr__(self) -> str:
        return '\nReceiver: {}\nSubject : {}\nMessage : {}'.format(
            self.r, self.s, self.m)
