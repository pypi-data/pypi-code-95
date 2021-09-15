# 依赖包
import http
import http.cookiejar
import os

import requests  # https://github.com/kennethreitz/requests
import pathlib
import json
# import base64
import logging
# from lxml import etree
import platform
...
# @author:zhubowen3432
# @作用：获取可以用于登陆的cookies
# @className：PyocsLogin
# @对外接口：get_login_cookies() 返回request需要的RequestsCookieJar类型的cookies
...


class PyocsUatLogin:
    # 全局信息
    __Login_Address = "https://ocs-uat.gz.cvte.cn/users/login"  # OCS登陆站点
    __OCS_Test_URL = "https://ocs-uat.gz.cvte.cn/tv"  # 测试用站点
    Access_URL = ['http://ocs-uat.gz.cvte.cn/tv', 'https://ocs.gz.cvte.cn/tv']  # 任何你想要访问的OCS站点
    _instance = None
    _cookies_file = ""
    _str_Location = 'Location'
    _logger = logging.getLogger(__name__)
    
    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别
        if platform.system() == "Linux":
            home_dir = os.environ['HOME']
            self._cookies_file = home_dir + '/.cookies'
            self._logger.info("linux环境")
        else:
            self._cookies_file = 'cookies'
            self._logger.info("windows环境")

    # 单例模式
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(PyocsUatLogin, cls).__new__(cls, *args, **kw)
        return cls._instance

    # 因为域账号统一，所以可以为其他系统提供账号，例如jenkins
    @staticmethod
    def get_account_from_json_file():
        if platform.system() == "Linux":
            home_dir = os.environ['HOME']
            _account_json_file = home_dir + '/.account.json'
        else:
            _account_json_file = 'account.json'
        try:
            logging.info(_account_json_file)
            with open(_account_json_file, 'r') as load_file:
                tmp = load_file.read()
                account_dict = json.loads(json.dumps(eval(tmp)))
                return account_dict
        except FileNotFoundError:
            logging.error("请创建JSON格式的文件，包含Username、Password值")
            return None

    def _get_cookies_form_4a(self, username, password):
        # # 直接从4a系统获取登陆cookies，主要分为如下4个部分
        #
        # # part 1 : 准备表单数据
        # form_data = dict()
        # form_data.update({
        #     '_method': 'POST',
        #     'data[User][username]': 'Username',
        #     'data[User][password]': 'Password',
        #     'ProductBussiness': "1"
        # })
        # form_data['data[User][username]'] = username
        # form_data['data[User][password]'] = password
        #
        # self._logger.info(form_data)
        # headers = dict()
        # headers.update({
        #     'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
        #     'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        # })
        #
        # # part 2 : 提交表单数据，获取ticket url
        # session = requests.Session() # 用requests.Session()创建session对象，相当于创建了一个空的会话框，准备保持cookies
        # # 在创建的session下用post发起登录请求，session这个时候就包括 cookies 了。allow_redirects=False表示禁止重定向
        # login_response = session.post(url=self.__Login_Address, data=form_data, allow_redirects=False, headers=headers)
        # # print(type(session.cookies)) # 打印cookies的类型,session.cookies就是登录的cookies
        # # print(session.cookies) # 打印cookies
        # self._logger.info("part 2 status code: " + str(login_response.status_code))
        # self._logger.info("part 2 header: " + str(login_response.headers))
        # ticket_url = login_response.headers[self._str_Location.title()]
        # self._logger.info("ticket_url: " + ticket_url)
        #
        # # part 3 : 从ticket url获取登陆cookies与跳转url
        # ticket_response = requests.get(ticket_url, allow_redirects=False)
        # self._logger.info("part 3 status code: " + str(ticket_response.status_code))
        # login_cookies = ticket_response.cookies
        # self._logger.info(login_cookies)
        # login_url = ticket_response.headers[self._str_Location.title()]
        # self._logger.info("login_url: " + login_url)
        #
        # # part 4 : 获取最终的登陆cookies
        # final_session = requests.Session()
        # final_response = final_session.get(login_url, cookies=login_cookies, allow_redirects=False)
        # self._logger.info("part 4 status code: " + str(final_response.status_code))
        # server_cookies = final_response.cookies
        # lwp_cookiesjar = http.cookiejar.LWPCookieJar(self._cookies_file)  # 实例化一个LWPcookiejar对象,用于写cookies到文件
        # requests.utils.cookiejar_from_dict({c.name: c.value for c in server_cookies}, lwp_cookiesjar)
        # lwp_cookiesjar.save(self._cookies_file, ignore_discard=True, ignore_expires=True)
        # self._logger.info(server_cookies)
        # return server_cookies
        return None

    def _get_cookies_from_file(self):
        # load_cookiejar = http.cookiejar.LWPCookieJar()
        # try:
        #     # 从文件中加载cookies(LWP格式)，装载前面保存在本地的cookie文件
        #     load_cookiejar.load(self._cookies_file, ignore_discard=True, ignore_expires=True)
        # except (FileNotFoundError, http.cookiejar.LoadError):
        #     self._logger.info("cookies文件未找到")
        #     return None
        # else:
        #     # 工具方法转换成字典
        #     load_cookies = requests.utils.dict_from_cookiejar(load_cookiejar)
        #     # 工具方法将字典转换成RequestsCookieJar，赋值给session的cookies.
        #     file_cookies = requests.utils.cookiejar_from_dict(load_cookies)
        #     self._logger.info(file_cookies)
        #     return file_cookies
        return None

    def _use_4a_to_login(self):
        # self._logger.info("从4A系统获取cookies登陆")
        # account = self.get_account_from_json_file()
        # if account is None:
        #     return None
        # username = account['Username']
        # password = account['Password']
        # tmp_cookies = self._get_cookies_form_4a(username, password)
        # request_from_4a = requests.get(self.Access_URL, cookies=tmp_cookies, allow_redirects=False)
        # if str(request_from_4a.url) == self.Access_URL:
        #     self._logger.info('远程cookies登陆成功')
        #     return tmp_cookies
        return None

    def get_login_cookies(self):
        """
        :rtype: RequestsCookieJar
        """

        # cookie_file = pathlib.Path(self._cookies_file)
        # if cookie_file.exists():
        #     file_cookies = self._get_cookies_from_file()
        #     self._logger.info("本地cookies:" + str(file_cookies))
        #     r = requests.get(self.Access_URL, cookies=file_cookies)
        #     self._logger.info("r.url:" + r.url)
        #     if str(r.url) == self.Access_URL:
        #         self._logger.info('本地cookies登陆成功')
        #         return file_cookies
        #     else:
        #         self._logger.info('本地cookies过期，从4A重新获取cookies')
        #         # cookie_file.unlink()
        #         return self._use_4a_to_login()
        # else:
        #     cookie_file.open(mode='w')  # 创建cookies文件
        #     return self._use_4a_to_login()

        # 获取本地存储的账号，并更新登录表单数据
        account = self.get_account_from_json_file()
        if account is None:
            return None

        form_data = dict()
        form_data.update({
            '_method': 'POST',
            'data[User][username]': account['Username'],
            'data[User][password]': account['Password'],
            'ProductBussiness': "1"
        })
        self._logger.info(form_data)

        headers = dict()
        headers.update({
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            'Accept': "text/html, application/xhtml+xml, application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        })

        # 提交表单数据，登录
        session = requests.Session()
        login_response = session.post(url=self.__Login_Address, data=form_data, allow_redirects=False, headers=headers)
        self._logger.info("part 2 status code: " + str(login_response.status_code))
        self._logger.info("part 2 header: " + str(login_response.headers))

        ticket_url = login_response.headers[self._str_Location.title()]
        self._logger.info("ticket_url: " + ticket_url)
        self._logger.info(login_response.cookies)

        # 判断登录结果
        if ticket_url in self.Access_URL:
            self._logger.warning('远程cookies登陆成功')
            return login_response.cookies
        else:
            self._logger.error('远程cookies登陆失败')
            return None