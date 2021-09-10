# -*- coding: utf-8 -*-

'''
Qianniu 客户端控制
'''

from pyAppControl import Win64ControlQianniu

class Qianniu:
    def __init__(self):
        print('账号首次登录时, 请对客户端做如下配置:')
        print('1. 通过短信验证')
        print('2. 去掉每次关闭前的提醒的勾选')
        print('3. 将发送的快捷键修改为 Ctrl + Enter')
        self.__qianniu = Win64ControlQianniu.Qianniu()
    
    def Login(self, appPath: str, userName: str, password: str, platformIndex: int = 0):
        '''
        登录 Qianniu 客户端
        更换设备时, 首次登录需要短信验证, 人工输入短信登录即可
        当前版本暂不支持短信验证登录
        未来可能会提供此功能, 敬请期待
        :param appPath       : str.  必填。Qianniu 客户端的启动路径
        :param userName      : str.  必填。登录用户名
        :param password      : str.  必填。登录密码
        :param platformIndex : int.  选填。默认为 0。指的是 Qianniu 客户端的登录平台, 顺序以实际情况为准

        :return dict. 返回登录状态. 返回结果示例: { 'state': 200, 'message': '' }
        '''
        response = self.__qianniu.Login(appPath, userName, password, platformIndex)
        return { 'state': response[0], 'message': response[1] }
    
    def Quit(self, userName: str):
        '''
        退出 Qianniu 客户端
        :param userName      : str.  必填。登录用户名

        :return dict. 返回退出状态. 返回结果示例: { 'state': 200, 'message': '' }
        '''
        response = self.__qianniu.Quit(userName)
        return { 'state': response[0], 'message': response[1] }
    
    def SendMessage(self, userName: str, customerId: str, message: str, sendState: bool = False):
        '''
        给指定账号的指定用户发送消息。两条消息消息之间的执行间隔建议尽量拉长一点
        :param userName   : str.  必填。登录用户名
        :param customerId : str.  必填。客户 id
        :param message    : str.  必填。需要发送的内容。如有换行, 可用 /n 来表示
        :param sendState  : bool. 选填。默认为 False。为 True 时执行发送

        :return dict. 返回发送状态. 返回结果示例: { 'state': 200, 'message': '' }
        '''
        response = self.__qianniu.SendMessage(userName, customerId, message, sendState)
        return { 'state': response[0], 'message': response[1] }
