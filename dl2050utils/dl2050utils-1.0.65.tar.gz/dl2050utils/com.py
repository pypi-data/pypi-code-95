import os, re
import socket
import json
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
from twilio.rest import Client
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from multiprocessing import Process
import boto3
import mimetypes
mimetypes.init()
from dl2050utils.core import *

default_address_book = {
    'jneto': {'email': 'joao.filipe.neto@gmail.com', 'phone': '+351966221506'},
    'pneto': {'email': 'pneto.98@gmail.com', 'phone': '+351910528813‬'},
    'jranito': {'email': 'joao.vasco.ranito@gmail.com', 'phone': '+351966221505'},
    'rassuncao': {'email': 'rui.assuncao@ndrive.com ', 'phone': '+351933339307'}
}

def read_address_book():
    try:
        with open('./.addressbook') as f: d = json.loads(f.read())
    except IOError:
        return None
    return d

# SendGrid
def send_mail(api_key, to, subject=None, msg=None, html=None, files=[]):
    to = listify(to)
    try:
        msg = msg or '   '
        html2 = html or msg
        subject = subject or '  '
        msg = Mail(from_email='ops@dl2050.com', to_emails=to, subject=subject, html_content=html2)
        if len(files):
            attachments = []
            for file in files:
                with open(str(file), 'rb') as f: data=f.read()
                data = base64.b64encode(data).decode()
                attachedFile = Attachment(
                    FileContent(data),
                    FileName(file.name),
                    FileType(mimetypes.types_map[file.suffix]),
                    Disposition('attachment')
                )
                attachments.append(attachedFile)
            msg.attachment = attachments
        sg = SendGridAPIClient(api_key)
        res = sg.send(msg)
    except Exception as e:
        return f'SendGrid ERROR: {str(e)}'
    if res.status_code!=202: return f'SendGrid ERROR: status code={res.status_code}'
    return None

def send_mail_async(api_key, to, subject=None, msg=None, html=None, files=[]):
    p = Process(target=send_mail, args=(api_key, to, subject, msg, html, files), daemon=True)
    p.start()

# def send_sms_aws(sms_id, sms_passwd, to, msg):
#     MessageAttributes={'AWS.SNS.SMS.SenderID': {'DataType': 'String','StringValue': 'DLOPS'}}
#     client = boto3.client('sns', aws_access_key_id=sms_id, aws_secret_access_key=sms_passwd, region_name="eu-west-1")
#     client.publish(PhoneNumber=to, Message=msg, MessageAttributes=MessageAttributes)
#     return None

def send_sms(account_sid, auth_token, service_name, to, msg):
    to = listify(to)
    try:
        client = Client(account_sid, auth_token)
        for e in to:
            message = client.messages.create(body=msg, from_=service_name, to=e)
        return None
    except Exception as e:
        return f'Twilio Exception: {str(e)}'

class Notify():
    def __init__(self, cfg=None, api_key=None, sms_id=None, sms_passwd=None, address_book=None):
        self.address_book = address_book if address_book is not None else default_address_book
        if cfg is not None:
            try:
                api_key = cfg['email']['sendgrid_api_key']
                sms_id = cfg['aws']['aws_access_key_id']
                sms_passwd = cfg['aws']['aws_secret_access_key']
            except Exception as e:
                print(f'Config ERROR: cant find variable: {e}')
        self.api_key = api_key
        self.sms_id = sms_id
        self.sms_passwd = sms_passwd
        
    def __call__(self, how, to, subject=None, msg=None, html=None, files=[]):
        if how not in ['email', 'email_async', 'sms']: return 'Invalid method, options are email, email_async or sms'
        # if isinstance(ini_list1, list)
        to = listify(to)
        if not len(to): return 'No destination addresses'
        for e in to:
            if e not in self.address_book: return f'Destination {e} not found in address book'
        if how=='email' or how=='email_async':
            if self.api_key is None: return 'email credentials not defined'
            to = [self.address_book[e]['email'] for e in to]
        if how == 'email_async':
            return self.send_mail_async(to, subject=subject, msg=msg, html=html, files=files)
        if how == 'email':
            return self.send_mail(to, subject=subject, msg=msg, html=html, files=files)
        if how=='sms':
            if self.sms_id is None or self.sms_passwd is None: return 'sms credentials not defined'
            to = [self.address_book[e]['phone'] for e in to]
            return send_sms(self.sms_id, self.sms_passwd, to, msg)
    
    def send_mail_async(self, to, subject=None, msg=None, html=None, files=[]):
        send_mail_async(self.api_key, to, subject=subject, msg=msg, html=html, files=files)
    
    def send_mail(self, to, subject=None, msg=None, html=None, files=[]):
        return send_mail(self.api_key, to, subject=subject, msg=msg, html=html, files=files)

    def send_sms(self, to, msg):
        return send_sms(self.sms_id, self.sms_passwd, to, msg)

EMAIL_TEMPLATE = \
"""
<html>
<head>
    <link href="https://fonts.googleapis.com/css?family=Muli::100,200,300,400,500,600,700,800" rel="stylesheet">
</head>
    <body style="position: relative; float: left; width: 100%; height: 100%;  text-align: center; font-family: 'Muli', sans-serif;">
        <h2 style="float: left; width: 100%; margin: 40px 0px 10px 0px; font-size: 16px; text-align: center; color: #555555;">{msg}</h2>
        <h2 style="float: left; width: 100%; margin: 0px 0px 40px 0px; font-size: 24px; text-align: center; color: #61C0DF; font-weight: bold;">{otp}</h2>
    </body>
</html>
"""

def send_otp_by_email(notify, product, email, otp):
    try:
        subject = f'{product} OTP'
        msg = f'{product} OTP: '
        html = EMAIL_TEMPLATE
        html = re.sub(r'{msg}', msg, html)
        html = re.sub(r'{otp}', f'{otp}', html)
        notify.send_mail_async(email, subject=subject, html=html)
    except Exception as e:
        return str(e)
    return None

def send_otp_by_phone(notify, product, phone, otp):
    msg = f'{product} OTP: {otp}'
    try:
        notify.send_sms(phone, msg)
    except Exception as e:
        return str(e)
    return None

def send_otp(notify, mode, product, email, phone, otp):
    if mode=='phone': return send_otp_by_phone(notify, product, phone, otp)
    return send_otp_by_email(notify, product, email, otp)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP