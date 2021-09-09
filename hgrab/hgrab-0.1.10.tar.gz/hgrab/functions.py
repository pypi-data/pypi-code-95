#!/usr/bin/env python 
# coding=utf-8
# @Time : 2021/9/1 13:42 
# @Author : HL 
# @Site :  
# @File : functions.py 
# @Software: PyCharm
import configparser
import difflib
import hashlib
import json
import os
import re
import time
import traceback
from time import sleep

import cchardet
import pymysql
import requests
import farmhash
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

conf_path = os.path.join('E:\project\python3-object\spiderman_config_file_package\hgrab\hgrab', 'config.ini')


def load_config(file):
    conf = configparser.ConfigParser()
    conf.read(file)
    return conf


class MysqlDB:
    def __init__(self, section='database', config_path=None, debug=False):
        if config_path:
            self.config_path = config_path
        else:
            self.config_path = conf_path
        self.conf = load_config(self.config_path)
        self.connet = pymysql.connect(host=self.conf.get(section, 'host'), user=self.conf.get(section, 'user'),
                                      password=self.conf.get(section, 'password'),
                                      database=self.conf.get(section, 'database'),
                                      port=int(self.conf.get(section, 'port')),
                                      charset=self.conf.get(section, 'charset'))
        self.section = section
        self.cursor = self.connet.cursor()
        self.debug = debug

    def reload_database(self):
        self.conf = load_config(self.config_path)
        self.connet = pymysql.connect(host=self.conf.get(self.section, 'host'),
                                      user=self.conf.get(self.section, 'user'),
                                      password=self.conf.get(self.section, 'password'),
                                      database=self.conf.get(self.section, 'database'),
                                      port=self.conf.get(self.section, 'port'),
                                      charset=self.conf.get(self.section, 'charset'))
        self.cursor = self.connet.cursor()

    # 插入
    def insert(self, sql, times=0, print_text='insert'):
        try:
            self.cursor.execute(sql)
            self.connet.commit()
        except:
            times += 1
            if self.debug:
                traceback.print_exc()
            print('failed {}!!! :{}'.format(print_text, sql))
            if times > 4:
                traceback.print_exc()
                return False
            sleep(1.5)
            self.reload_database()
            self.insert(sql, times)
        return True

    # 插入
    async def insert_async(self, sql, times=0, print_text='insert'):
        try:
            await self.cursor.execute(sql)
            await self.connet.commit()
        except:
            times += 1
            if self.debug:
                traceback.print_exc()
            print('failed {}!!! :{}'.format(print_text, sql))
            if times > 4:
                traceback.print_exc()
                return False
            sleep(1.5)
            self.reload_database()
            await self.insert_async(sql, times)
        return True

    # 查询
    def select(self, sql, times=0):
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except:
            times += 1
            if self.debug:
                traceback.print_exc()
            print('failed select!!! :', sql)
            if times > 4:
                traceback.print_exc()
                return ''
            sleep(1.5)
            self.reload_database()
            self.select(sql, times)
        return result

    # 存在
    def has(self, sql, times=0):
        try:
            self.cursor.execute(sql)
            if self.cursor.fetchone() is None:
                return False
        except:
            times += 1
            if self.debug:
                traceback.print_exc()
            print('failed has!!! :', sql)
            if times > 4:
                traceback.print_exc()
                return ''
            sleep(1.5)
            self.reload_database()
            self.has(sql, times)
        return True

    # 存在
    async def has_async(self, sql, times=0):
        try:
            await self.cursor.execute(sql)
            if self.cursor.fetchone() is None:
                return False
        except:
            times += 1
            if self.debug:
                traceback.print_exc()
            print('failed has!!! :', sql)
            if times > 4:
                traceback.print_exc()
                return ''
            sleep(1.5)
            self.reload_database()
            await self.has_async(sql, times)
        return True

    # 更新
    def update(self, sql, times=0):
        self.insert(sql, times=times, print_text='update')

    # 根据字典、表名生成 insert sql
    def create_sql(self, table, dics, **kwargs):
        conditon = ''
        values = ''
        for k, v in dict.items(dics):
            conditon = conditon + ',' + pymysql.escape_string(str(k))
            values = values + ',"' + pymysql.escape_string(str(v)) + '"'
        for k, v in dict.items(kwargs):
            conditon = conditon + ',' + pymysql.escape_string(str(k))
            values = values + ',"{}"'.format(pymysql.escape_string(str(v)))

        sql = "INSERT INTO `{}`({}) VALUES ({})".format(table, conditon[1:], values[1:])
        return sql


class Downloader:
    def __init__(self, config_path=None, section='proxy', debug=False):
        if config_path:
            self.config_path = config_path
        else:
            self.config_path = conf_path
        self.conf = load_config(self.config_path)
        self.headers = json.loads(self.conf.get('headers', 'headers_'))
        self.proxyMeta = "http://%(host)s:%(port)s" % {
            "host": self.conf.get(section, 'proxy_host'),
            "port": self.conf.get(section, 'proxy_port'),
        }
        self.proxies = {
            "http": self.proxyMeta,
            "https": self.proxyMeta,
        }
        self.debug = debug

    # 获取链接Response
    def get_response(self, href, timeout=10, headers=None, debug=False, proxy_use=False):
        if not headers:
            headers = self.headers
        redirected_url = href
        response = None
        try:
            if proxy_use:
                response = requests.get(href, headers=headers, timeout=timeout)
            else:
                response = requests.get(href, headers=headers, proxies=self.proxies, timeout=timeout)
            redirected_url = response.url
            status = response.status_code
        except:
            if debug:
                traceback.print_exc()
            msg = 'failed download: {}'.format(href)
            print(msg)
            status = 0
        return status, response, redirected_url

    # 获取网页源码
    def get_html(self, href, timeout=10, headers=None, debug=False, binary=False, proxy_use=False):
        status, response, redirected_url = self.get_response(href, timeout=timeout, headers=headers, debug=debug,
                                                             proxy_use=proxy_use)
        if status == 0:
            if binary:
                html = b''
            else:
                html = ''
            return status, html, redirected_url
        if binary:
            html = response.content
        else:
            encoding = cchardet.detect(response.content)['encoding']
            html = response.content.decode(encoding)
        return status, html, redirected_url

    # 获取源码返回BeautifulSoup
    def get_soup(self, href, timeout=10, headers=None, debug=False, proxy_use=False):
        status, html, redirected_url = self.get_html(href, timeout=timeout, headers=headers, debug=debug,
                                                     proxy_use=proxy_use)
        soup = None
        try:
            soup = BeautifulSoup(html, 'lxml')
        except:
            if debug:
                traceback.print_exc()
            msg = 'failed soup analysis!!! href: {}  \nhtml:{}'.format(href, html)
            print(msg)
        return status, soup, redirected_url

    # POST获取链接Response
    def post_response(self, href, data, timeout=10, headers=None, debug=False, proxy_use=False):
        if not headers:
            headers = self.headers
        redirected_url = href
        response = None
        try:
            if proxy_use:
                response = requests.post(href, headers=headers, data=data, timeout=timeout)
            else:
                response = requests.post(href, headers=headers, data=data, proxies=self.proxies, timeout=timeout)
            redirected_url = response.url
            status = response.status_code
        except:
            if debug:
                traceback.print_exc()
            msg = 'failed download: {}'.format(href)
            print(msg)
            status = 0
        return status, response, redirected_url

    # POST获取网页源码
    def post_html(self, href, data, timeout=10, headers=None, debug=False, binary=False, proxy_use=False):
        status, response, redirected_url = self.post_response(href, data, timeout=timeout, headers=headers, debug=debug,
                                                              proxy_use=proxy_use)
        if status == 0:
            if binary:
                html = b''
            else:
                html = ''
            return status, html, redirected_url
        if binary:
            html = response.content
        else:
            encoding = cchardet.detect(response.content)['encoding']
            html = response.content.decode(encoding)
        return status, html, redirected_url

    # aiohttp异步
    async def fetch(self, session, url, headers=None, timeout=9, binary=False, debug=None, proxy=None):
        if not headers:
            _headers = self.headers
        if headers:
            _headers = headers
        try:
            if proxy:
                async with session.get(url, headers=_headers, timeout=timeout, proxy=self.proxyMeta) as response:
                    status = response.status
                    html = await response.read()
                    if not binary:
                        encoding = cchardet.detect(html)['encoding']
                        html = html.decode(encoding, errors='ignore')
                    redirected_url = str(response.url)
            else:
                async with session.get(url, headers=_headers, timeout=timeout) as response:
                    status = response.status
                    html = await response.read()
                    if not binary:
                        encoding = cchardet.detect(html)['encoding']
                        html = html.decode(encoding, errors='ignore')
                    redirected_url = str(response.url)
        except Exception as e:
            if debug:
                traceback.print_exc()
            msg = 'Failed download: {} | exception: {}, {}'.format(url, str(type(e)), str(e))
            print(msg)
            html = ''
            status = 0
            redirected_url = url
        return status, html, redirected_url

    async def post_fetch(self, session, url, data, headers=None, timeout=10, binary=False, debug=None, proxy=None):
        if not headers:
            _headers = self.headers
        if headers:
            _headers = headers
        try:
            if proxy:
                async with session.post(url, headers=_headers, data=data, timeout=timeout,
                                        proxy=self.proxyMeta) as response:
                    status = response.status
                    html = await response.read()
                    if not binary:
                        encoding = cchardet.detect(html)['encoding']
                        html = html.decode(encoding, errors='ignore')
                    redirected_url = str(response.url)
            else:
                async with session.post(url, headers=_headers, data=data, timeout=timeout) as response:
                    status = response.status
                    html = await response.read()
                    if not binary:
                        encoding = cchardet.detect(html)['encoding']
                        html = html.decode(encoding, errors='ignore')
                    redirected_url = str(response.url)

        except Exception as e:
            if debug:
                traceback.print_exc()
            msg = 'Failed download: {} | exception: {}, {}'.format(url, str(type(e)), str(e))
            print(msg)
            html = ''
            status = 0
            redirected_url = url
        return status, html, redirected_url

    # webdriver+selenium 模拟浏览器
    def get_selenium_driver(self, executable_path=None, wap_use=False):
        option = webdriver.ChromeOptions()
        # option.add_argument("--start-maximized")
        # prefs = {'profile.managed_default_content_settings.images': 2}
        # option.add_experimental_option('prefs', prefs)
        # option.add_extension(proxy_auth_plugin_path)
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        if wap_use:
            # wap端
            mobileEmulation = {'deviceName': 'iPhone X'}
            option.add_experimental_option('mobileEmulation', mobileEmulation)
        if not executable_path:
            executable_path = "D:\\chromedriver.exe"
        return webdriver.Chrome(chrome_options=option, executable_path=executable_path)

    # phantomjs+selenium 驱动
    def get_phantomjs_driver(self, headers=None):
        if not headers:
            headers = self.headers
        # 初始化浏览器对象
        # 使用copy() 防止修改原代码定义dict
        cap = DesiredCapabilities.PHANTOMJS.copy()
        for key, value in headers.items():
            cap['phantomjs.page.customHeaders.{}'.format(
                key)] = value

        # 在初始化浏览器对象的时候可以接收一个service_args的参数，使用这个参数设置代理
        driver = webdriver.PhantomJS(desired_capabilities=cap)
        # 设置页面加载和js加载超时时间，超时立即报错，如下设置超时时间为10秒
        driver.set_page_load_timeout(25)
        driver.set_script_timeout(25)
        return driver

    # phantomjs+selenium+proxy 驱动
    # 暂不使用
    def get_phantomjs_driver_proxy(self, headers=None):
        if not headers:
            headers = self.headers
        # 初始化浏览器对象
        # 使用copy() 防止修改原代码定义dict
        cap = DesiredCapabilities.PHANTOMJS.copy()
        for key, value in headers.items():
            cap['phantomjs.page.customHeaders.{}'.format(
                key)] = value
        proxy = [
            '--proxy=%s:%s' % (self.proxyHost, self.proxyPort),  # 代理服务器的域名
            '--proxy-type=http',  # 代理类型
            '--proxy-auth=%s:%s' % (self.proxyUser, self.proxyPass),  # 代理验证所需的用户名和密码
            '--ignore-ssl-errors=true',  # 忽略https错误
        ]

        # 在初始化浏览器对象的时候可以接收一个service_args的参数，使用这个参数设置代理
        driver = webdriver.PhantomJS(service_args=proxy, desired_capabilities=cap)

        # 设置页面加载和js加载超时时间，超时立即报错，如下设置超时时间为10秒
        driver.set_page_load_timeout(25)
        driver.set_script_timeout(25)

        return driver


class tools:
    # 将字符串生成MD5
    def get_md5(self, str):
        m = hashlib.md5()
        m.update(str.encode("utf8"))
        return m.hexdigest()

    # urlhash链接farmhash化（待完成） pip install pyfarmhash
    def get_farmhash(self, str):
        return farmhash.hash64(str)

    # 获取当前时间
    def now_time(self, nf=1, format='%Y-%m-%d %H:%M:%S', millisecond=False):
        if nf:
            return time.strftime(format)
        else:
            timestamp = time.time()
            return timestamp if millisecond else int(timestamp)

    # 时间字符串转成时间戳
    def str_to_timestamp(self, str, formart='%Y-%m-%d %H:%M:%S', millisecond=False):
        if millisecond:
            return time.mktime(time.strptime(str, formart))
        return time.mktime(time.strptime(str, formart))

    # 时间戳转字符串
    def timestamp_to_str(self, timestamp, formart='%Y-%m-%d %H:%M:%S'):
        if isinstance(timestamp, int):
            return time.strftime(formart, time.localtime(timestamp))
        elif isinstance(timestamp, float):
            return time.strftime(formart, time.localtime(timestamp))
        else:
            msg = 'Please convert the data into int or float format!!!'
            return msg

    # 比较两字符串的相似度
    def string_similar(self, s1, s2):
        try:
            f = difflib.SequenceMatcher(None, s1, s2).quick_ratio()
        except:
            traceback.print_exc()
            print('failed similar string!!!')
            return None
        return f

    # 上传图片到Zimg（传入图片链接，和下载图片暂存的本机路径）
    def uploadZimg(self, url, zimgUrl, path):
        header = {'Connection': 'Keep-Alive', 'Cache-Control': 'no-cache', }
        if not os.path.exists(path):
            try:
                r = requests.get(url, verify=False)
                r.raise_for_status()
                # 使用with语句可以不用自己手动关闭已经打开的文件流
                with open(path, "wb") as f:  # 开始写文件，wb代表写二进制文件
                    f.write(r.content)
            except Exception as e:
                print("爬取失败:" + str(e))
                return ''
        files = {'files': open(path, 'rb')}
        n = 1
        while True:
            try:
                r = requests.post(zimgUrl, files=files, headers=header)
                if 'Image upload successfully' in r.text:
                    md5 = re.search('<h1>MD5:(.*?)</h1>', r.text).group(1)
                    return md5
                else:
                    print('上传失败！！！')
                    return ''
            except Exception as e:
                print('上传失败：' + str(e))
                if n > 4:
                    return ''
                n += 1
                sleep(1.5)
