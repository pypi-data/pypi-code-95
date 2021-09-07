from os import remove, path
from HttpService import HttpServiceClass
from FileService import FileServiceClass
from werkzeug._reloader import run_with_reloader
import json
import time

class ToolsServiceClass(object):
    def __init__(self):
        self.httpService = HttpServiceClass()
        self.fileService = FileServiceClass()
        #region 企业微信
        self.corpid = "wwb6ec4438ccc388c3"      # Corpid是企业号的标识
        self.secret = "_surPYo0SLVcxPKzAnHdWBwpGl2woxWKWpSTMvbZvnw"     # Secret是管理组凭证密钥
        self.agentid = "1000002"        # 应用ID
        self.tokenConfig = "" #self.fileService.ConvertTempPath(r'./zabbix_wechat_config.json')     # token_config文件放置路径
        self.fileService.CreateDir(self.tokenConfig)
        self.bot = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c2ae20ef-9a26-4791-abb5-962e07f97144"
        #endregion
    def ToNumberCompany(self, number):
        if number > 100000000:
            return number/100000000 + '亿'
        elif number > 10000000:
            return number/10000000 + '千万'
        elif number > 1000000:
            return number/1000000 + '百万'
        elif number > 100000:
            return number/100000 + '十万'
        elif number > 10000:
            return number/10000 + '万'
        else:
            return number
    
    #https://www.runoob.com/markdown/md-block.html
    def SendNotify(self, desc='', userId=None):
        data={"msgtype":"text", "text":{"content":desc}}
        if userId:
            data["touser"] = userId
        self.SendWorkWX(data)
    
    def _GetTokenFromServer(self, corpid, secret, tokenConfig):
        """ 获取 token """
        token = False
        try:
            if path.exists(tokenConfig):
                file = open(tokenConfig, 'r')
                jsonFileData = json.load(file)
                token = jsonFileData['access_token']
                expires_in = jsonFileData['expires_in']
                file.close()
                
                modifyTime = path.getmtime(tokenConfig)
                offtime = time.time() - modifyTime - expires_in
                if offtime > 0:
                    token = False
                    raise Exception('%s 校验文件已过期,需要重新获取校验信息'%tokenConfig)
            else:
                raise Exception('%s 校验文件不存在需要创建'%tokenConfig)
        except Exception as e:
            print("Error: %s"%e)
            url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
            data = {
                "corpid": corpid,
                "corpsecret": secret
            }
            r = self.httpService.PostUrlResetByRequests(url=url, params=data, verify=False)
            print("企业微信Token: %s"%r.json())
            if r.json()['errcode'] != 0:
                token = False
            else:
                token = r.json()['access_token']
                file = open(tokenConfig, 'w')
                file.write(r.text)
                file.close()
                print('%s 校验文件已更新'%tokenConfig)
        return token

    def SendWorkWX(self, data, corpid=None, secret=None, errorNum=3):
        """ 
        发送消息到企业微信
        API文档： https://work.weixin.qq.com/api/doc/90000/90135/90236
        """
        if not corpid or not secret:
            corpid = self.corpid
            secret = self.secret
        tokenConfig = self.fileService.ConvertTempPath(r'./%s_wechat_config.json'%(corpid))
        # 获取token信息
        token = self._GetTokenFromServer(corpid, secret, tokenConfig)
        # 发送消息
        if not "agentid" in data:
            data["agentid"] = self.agentid
        if not "touser" in data:
            data["touser"] = "@all"
        if not "toparty" in data:
            data["toparty"] = "1"
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % token
        result = self.httpService.PostUrlResetByRequests(url=url, data=json.dumps(data), verify=False)
        print("企业微信应用消息： %s"%result.json())
        # 如果发送失败，将重试多次if
        if result.json()['errcode'] != 0 and errorNum and errorNum > 0:
            if result.json()['errcode'] == 42001:
                remove(tokenConfig)
                token = self._GetTokenFromServer(corpid, secret, tokenConfig)
            return self.SendWorkWX(data, corpid, secret, errorNum-1)
        else:
            return result.json()
    
    def SendWorkWXBot(self, data, url=None):
        """
        发送企业微信消息，机器人群
        API文档： https://work.weixin.qq.com/api/doc/90000/90136/91770
        """
        url = url or self.bot
        if not "mentioned_list" in data["text"]:
            data["text"]["mentioned_list"] = ["@all"]
        if not "mentioned_mobile_list" in data["text"]:
            data["text"]["mentioned_mobile_list"] = ["@all"]
        print(json.dumps(data))
        result = self.httpService.PostUrlResetByRequests(url=url, data=json.dumps(data), verify=False)
        print("企业微信应用消息： %s"%result.json())

    def RunWithReloader(func):
        """ 利用的flask的重启模块 """
        run_with_reloader(func)