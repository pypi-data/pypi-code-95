from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ImageSendMessage, StickerSendMessage, AudioSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key

import speech_recognition as sr
import os
from botnoi import decode
#import decode

class linesetting():
    def __init__(self,lineaccesstoken):
        self.lineaccesstoken = lineaccesstoken
        self.line_bot_api = LineBotApi(lineaccesstoken)

class lineevent():
  def __init__(self,event,s3info,line_bot_api):
    self.event = event
    self.eventtype = event['type']
    self.timestamp = event['timestamp']
    self.userid = event['source']['userId']
    self.rtoken = event['replyToken']
    self.aws_access_key_id = s3info['AWS_ACCESS_KEY_ID']
    self.aws_secret_access_key = s3info['AWS_SECRET_ACCESS_KEY']
    self.imagebucket = s3info['imagebucket']
    self.audiobucket = s3info['audiobucket']
    if self.eventtype == 'message':
      messageevent = self.event['message']
      self.messagetype = messageevent['type']
      if self.messagetype == 'text':
        messageinput = messageevent['text']
        self.result = messageinput
      elif self.messagetype == 'image':
        message_content = line_bot_api.get_message_content(messageevent['id'])
        self.imfile = 'im_'+str(self.userid)+'_'+str(self.timestamp)+'.jpg'
        with open(self.imfile, 'wb') as fd:
          for chunk in message_content.iter_content():
            fd.write(chunk)
        #result = upload(imfile, public_id=imfile)
        result = self.upload_s3(self.imfile, '.jpg', self.imagebucket)
        print(result)
        self.result = result
      elif self.messagetype == 'audio':
        message_content = line_bot_api.get_message_content(messageevent['id'])
        self.aufile = 'au_'+str(self.userid)+'_'+str(self.timestamp)+'.wav'
        with open(self.aufile, 'wb') as fd:
          for chunk in message_content.iter_content():
            fd.write(chunk)
        result = self.upload_s3(self.aufile, '.wav', self.audiobucket)
        print(result)
        self.result = result

  def upload_s3(self, file, content_type, bucket_name):
    s3connection = S3Connection(self.aws_access_key_id, self.aws_secret_access_key)
    bucket = s3connection.get_bucket(bucket_name)
    obj = S3Key(bucket)
    obj.name = file
    obj.set_metadata('Content-Type', content_type)
    obj.set_contents_from_filename(file)
    obj.set_acl('public-read')
    return obj.generate_url(expires_in=0, query_auth=False)

  def transcribeaudio(self,lang='th-TH'):
    r = sr.Recognizer()
    decode.decodeaudio(self.aufile)
    with sr.AudioFile(self.aufile) as source:
        audio = r.record(source)  # read the entire audio file
    try:
        result = r.recognize_google(audio,language=lang)
    except sr.UnknownValueError:
        result = "unknown error"
    except sr.RequestError as e:
        result = "could not request service"
    return result

  def deletefile(self):
    try:
        os.remove(self.imfile)
    except:
        pass
    try:
        os.remove(self.aufile)
    except:
        pass







