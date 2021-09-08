import uuid
import requests
import hashlib
import base64
import time
import json
import os

CURRENT_WORD = None
LAST_WORD = None


class Word:
    ''' errorCode	text	错误返回码	一定存在
        query	text	源语言	查询正确时，一定存在
        translation	Array	翻译结果	查询正确时，一定存在
        basic	text	词义	基本词典，查词时才有
        web	Array	词义	网络释义，该结果不一定存在
        l	text	源语言和目标语言	一定存在
        dict	text	词典deeplink	查询语种为支持语言时，存在
        webdict	text	webdeeplink	查询语种为支持语言时，存在
        tSpeakUrl	text	翻译结果发音地址	翻译成功一定存在，需要应用绑定语音合成实例才能正常播放否则返回110错误码
        speakUrl	text	源语言发音地址	翻译成功一定存在，需要应用绑定语音合成实例才能正常播放否则返回110错误码
        returnPhrase	Array	单词校验后的结果	主要校验字母大小写、单词前含符号、中文简繁体
    '''
    def __init__(self, **kwargs) -> None:
        # 翻译结果
        # 列表 [英俊的]
        self.is_word = kwargs.get("isWord")
        self.translation = kwargs.get("translation")[0]
        # 基本释义（查询内容是单词是才有）
        # 字典
        # 会用到的键值对{phonetic:"ˈhænsəm",explains:[adj. （男子）英俊的；可观的；大方的，慷慨的；健美而端庄的]}
        self.query = kwargs['query']
        self.basic = []
        self.phonetic = ''
        if kwargs.get("basic"):
            basic = kwargs.get("basic")
            if basic.get('explains'):
                self.basic = basic['explains']
            if basic.get('phonetic'):
                self.phonetic = basic['phonetic']
        # 网络释义
        # 列表
        # [{"handsome":["英俊的","美观的","大方的","漂亮的"]},
        #  {"handsome siblings":["绝代双骄","新绝代双骄","旷世双骄"]},
        #  {"handsom man reiver":["江玉郎","英俊的男人河"]}
        # ]
        self.web = {}
        if kwargs.get("web"):
            web = kwargs.get("web")
            for item in web:
                self.web[item['key']] = item['value']
        # 发音地址（audio/mp3）
        # 网址 content-type:audio/mp3
        self.speakUrl = kwargs.get("speakUrl")
        # 词典地址
        # 字典
        self.webdict = kwargs.get("webdict")["url"]
        global CURRENT_WORD
        CURRENT_WORD = self

    def __repr__(self) -> str:
        return self.translation + f"[{self.phonetic}]({self.webdict})"


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    u = base64.b64decode("aHR0cHM6Ly9vcGVuYXBpLnlvdWRhby5jb20vYXBp").decode(
        "utf8")
    return requests.post(u, data=data, headers=headers)


def get_word():
    if CURRENT_WORD:
        return CURRENT_WORD
    else:
        raise SystemExit('当前没有查询的单词')


def phrase(word_json):
    ''' errorCode	text	错误返回码	一定存在
        query	text	源语言	查询正确时，一定存在
        translation	Array	翻译结果	查询正确时，一定存在
        basic	text	词义	基本词典，查词时才有
        web	Array	词义	网络释义，该结果不一定存在
        l	text	源语言和目标语言	一定存在
        dict	text	词典deeplink	查询语种为支持语言时，存在
        webdict	text	webdeeplink	查询语种为支持语言时，存在
        tSpeakUrl	text	翻译结果发音地址	翻译成功一定存在，需要应用绑定语音合成实例才能正常播放否则返回110错误码
        speakUrl	text	源语言发音地址	翻译成功一定存在，需要应用绑定语音合成实例才能正常播放否则返回110错误码
        returnPhrase	Array	单词校验后的结果	主要校验字母大小写、单词前含符号、中文简繁体
    '''

    word_dict = json.loads(word_json)
    return Word(**word_dict)


def get_word_audio(url=None, filename=None):
    if url is None and CURRENT_WORD is None:
        raise SystemExit('无法获取单词读音文件')
    if url is None:
        url = CURRENT_WORD.speakUrl
    resp = requests.get(url)
    resp.raise_for_status()
    contentType = resp.headers['Content-Type']
    if filename is None:
        filename = os.path.join(os.getcwd(), 'word.mp3')
    if contentType == "audio/mp3":
        with open(filename, 'wb') as fo:
            fo.write(resp.content)
        return os.path.abspath(filename)
    else:
        raise SystemExit('服务器返回内容错误')


def connect(word):
    q = word

    data = {}
    data['from'] = 'auto'
    data['to'] = 'auto'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    AK = base64.b64decode("N2RlMzBiMDRjY2M3MTA3Mg==").decode("utf8")
    AS = base64.b64decode(
        "ZmtUZHhUU1Ywb1p1THJzTHVQVVlMSkpOZ3BtN0JXSlA=").decode("utf8")
    signStr = AK + truncate(q) + salt + curtime + AS
    sign = encrypt(signStr)
    data['appKey'] = AK
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign

    response = do_request(data)
    contentType = response.headers['Content-Type']
    if contentType == "audio/mp3":
        # millis = int(round(time.time() * 1000))
        # filePath = "合成的音频存储路径" + str(millis) + ".mp3"
        # fo = open(filePath, 'wb')
        # fo.write(response.content)
        # fo.close()
        return response.content
    else:
        # print(response.content)
        return response.text


if __name__ == '__main__':
    txt = connect("hello")
    print(txt)
    word = Word(**json.loads(txt))
    print(word)
