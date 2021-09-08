from frasco.mail.provider import MailProvider
import requests
import logging
import base64
from email.utils import parseaddr
from flask_mail import sanitize_address


MAILJET_API_URL = 'https://api.mailjet.com/v3.1'


class MailjetProvider(MailProvider):
    def send(self, msg):
        r = requests.post("%s/send" % self.options.get('mailjet_api_url', MAILJET_API_URL),
            auth=(self.options['mailjet_api_key_public'], self.options['mailjet_api_key_private']),
            json={"Messages": [self.convert_to_mailjet_message(msg)]})
        r.raise_for_status()

    def convert_to_mailjet_message(self, msg):
        data = {
            "From": self.convert_address(msg.sender),
            "To": list([self.convert_address(addr) for addr in msg.recipients]),
            "Subject": msg.subject
        }

        if msg.cc:
            data['Cc'] = list([self.convert_address(addr) for addr in msg.cc])
        if msg.bcc:
            data['Bcc'] = list([self.convert_address(addr) for addr in msg.bcc])
        if msg.body:
            data['TextPart'] = msg.body
        if msg.html:
            data['HTMLPart'] = msg.html
        if msg.attachments:
            data['Attachments'] = []
            for attachment in msg.attachments:
                data['Attachments'].append({
                    "ContentType": attachment.content_type,
                    "Filename": attachment.filename,
                    "Base64Content": base64.b64encode(attachment.data)
                })
        if msg.extra_headers:
            data['Headers'] = msg.extra_headers
        if msg.reply_to:
            data.setdefault('Headers', {})
            data['Headers']['Reply-To'] = sanitize_address(msg.reply_to)

        return data

    def convert_address(self, addr):
        if isinstance(addr, (str, unicode)):
            addr = parseaddr(addr)
        name, addr = addr
        if name:
            return {"Email": addr, "Name": name}
        return {"Email": addr}
