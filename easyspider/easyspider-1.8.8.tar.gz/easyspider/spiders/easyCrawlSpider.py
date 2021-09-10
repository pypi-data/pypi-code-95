# coding=utf-8
import sys
if sys.version_info < (3, ):
    reload(sys)
    sys.setdefaultencoding("utf-8")
    import urlparse
else:
    from urllib import parse as urlparse
from scrapy_redis.spiders import RedisCrawlSpider
from easyspider.utils.tools import get_time
from easyspider.utils.tools import flat
from scrapy.http import Response
from bs4 import UnicodeDammit
from scrapy import Request
import traceback
from django.core.serializers.json import DjangoJSONEncoder

import urllib
import socket
import time
import json
import copy
import pdb
import redis
import base64

from functools import partial
json.dumps = partial(json.dumps, cls=DjangoJSONEncoder)


class easyCrawlSpider(RedisCrawlSpider):
    """所有爬虫最全的基类
    提供了一系列优秀简便的方法，来使编码过程更加友好快捷
    base spider of easyspider
    have provied multi useful method to make crawler more easier
    """

    name = "easyCrawlSpider"
    # redis 数据库key的定义，都是按照 spider_name:key_name 的格式
    start_key = "start_urls"
    priority_start_key = "priority_start_urls"
    successed_key = "successed_urls"
    failed_key = "failed_urls"
    # 最大重试次数
    retry_max_time = 1

    # 一次从redis中取多少条任务/链接
    fetch_unit = 16

    # 操作redis 的方法，可替换
    # 操作普通队列的方法， rpop, lpush
    fetch_from_redis_method = (lambda self, server: server.rpop)
    save_into_redis_method = (lambda self, server: server.lpush)

    # 操作优先级队列的方法
    fetch_from_priority_queue = (lambda self, server, key_name, fetch_unit: server.zrevrangebyscore(key_name, float('inf'), float('-inf'), 0, fetch_unit))
    delete_from_priority_queue = (lambda self, server, key_name, val: server.zrem(key_name, val))
    if redis.VERSION[0] < 3:
        save_into_priority_queue = (lambda self, server, key_name, val, data: server.zadd(key_name, val, data))
    else:
        save_into_priority_queue = (lambda self, server, key_name, val, data: server.zadd(key_name, {data: val}))

    is_base64 = False

    def next_requests(self):
        """
        整个的心跳函数
        heartbeat of engine, called every 5s, to generate new request in crawler process

        next_requests will [r]pop the spider_name:start_key list queue from redis (attention, operation is lpop,
        so when you need to push into redis, you should use lpush instead)
        """
        count = 0
        while count < self.fetch_unit:
            """从redis中获取任务，进行编码，然后提交到引擎，注意：

            1. 先检查 优先队列中是否有任务，优先队列中有，先处理优先队列的任务
            2. 其次再是正常的list普通任务

            (try except 是因为：在整个过程中，由于adsl 机器恶劣的网络环境，每一步网络操作，都需要预防在操作的过程中出现 【断网】的极端情况)
            """
            try:
                # 先尝试从优先队列中获取任务
                start_map = self.fetch_from_priority_queue(self.server, "%s:%s" % (self.name, self.priority_start_key), 1)
                if start_map:
                    """注意返回的是list，所以需要[0]的操作
                    另外优先队列是没有 pop的操作的，get了之后，需要立即做pop/delete处理
                    """
                    start_map = start_map[0]
                    self.delete_from_priority_queue(self.server, "%s:%s" % (self.name, self.priority_start_key), start_map)
                else:
                    """如果优先队列中没有内容，则从普通任务中提取
                    if not, fetch from common queue
                    """
                    start_map = self.fetch_from_redis_method(self.server)(u"%s:%s" % (self.name, self.start_key))
            except Exception:
                """如果因为某种问题，如断网，影响了redis的连接，此时应该等待一段时间
                再次尝试连接。

                因为没有获得具体的任务，所以下面的操作都执行不下去，在这里就要continue，继续尝试从redis中获取任务
                """
                self.logger.exception("in easyCrawlSpider: next_requests,  start_map = self.fetch_from_redis_method(self.server)(u\"%s:%s\" % (self.name, self.start_key)) failed, continue")
                # time.sleep(3)
                count += 1
                continue
            # 提取任务成功，开始对任务进行解码，提交到引擎处理
            req = self.convert_startmap_2_request(start_map)
            if isinstance(req, Request):
                yield req
                # 收到的任务数+1
                count += 1
            else:
                # 如果没有获取到任务，那么就直接退出，等待下次检查是否有新任务出现
                break

        self.logger.debug("Read %s requests from '%s:%s'" % (count, self.name, self.start_key))

    def convert_startmap_2_request(self, start_map):
        """爬虫任务的解析函数。redis 中存储的任务，及任务附带的信息，在这里被解码，从而
        真正提交到引擎去执行抓取。
        注意这个解析是非常复杂的，涉及了非常多的方面。
        """

        # 如果redis中任务为空，那么直接返回，等待下次检查是否有新任务出现
        if not start_map:
            return
        # 如果任务不能被解码，那么就是极度异常的情况，后面都不能继续下去
        try:
            start_map = json.loads(start_map)
        except Exception:
            self.logger.exception(u"convert start url -> dict failed, start_map source is %s" % (start_map))

        try:
            """解析原则：

            1. 如果这个任务，是由 retry_middleware (即是属于，在出错情况下，被添加进来的任务)那么就要无视他的dont_filter(因为本来就是出错才重试，如果被filter了，那么就没有意义)

            """

            # ------------------------------------------
            # 处理dont_filter:
            # 判断是否是，之前任务执行失败，而添加的新任务，就是看任务中，有没有 from_retry字段
            if not start_map.get("dont_filter"):
                # 含有from_retry 字段，且from_retry 不为0
                # from_retry = int(start_map.get("easyspider", {}).get("from_retry", 0))
                # if from_retry > 0:
                #     close_filter = True
                # else:
                #     close_filter = False
                close_filter = False
            else:
                # 其他情况，那么就根据他自己的情况来, 指定关闭过滤器，则关闭过滤器
                if start_map.get("dont_filter") in ["True", "true", True]:
                    close_filter = True
                else:
                    close_filter = False

            # ------------------------------------------
            # 处理callback:
            # callback 函数默认为self.parse, 但是一样可以自定义
            # 不过要注意的是，需要把callback由字符串，转变为函数

            callback_fun = start_map.get("callback") or "self.parse"
            req_callback_method = eval(callback_fun)

            # ------------------------------------------
            # 处理url:
            # 请求的网址，从url 中获取

            req_url = start_map.get("url")

            # ------------------------------------------
            # 处理请求方法:
            # 默认的请求是 GET

            req_method = start_map.get("method") or "GET"

            # ------------------------------------------
            # 处理请求头:
            # 注意，请求头应该是dict字典格式，而不是编码后的字符串 ！！！
            # 需要额外注意的是，如果是json格式的请求，需要额外编码

            req_headers = start_map.get("headers") or {}

            # ------------------------------------------
            # 处理cookie：
            # 注意，cookie 应该是字符串格式，这里将不会再进行编码

            req_cookies = start_map.get("cookies") or None

            # ------------------------------------------
            # 处理请求体body:
            # 请求体可以有多种格式，无论是dict字典的给出，还是字符串的给出，都能被接受
            # 注意，针对json格式的请求，需要额外增加支持

            if req_method.upper() != "GET":
                post_data = start_map.get("body", "")
                req_body = post_data
                if start_map.get("meta", {}).get("is_base64"):
                    req_body = base64.b64decode(req_body)
                else:
                    req_body = post_data.encode("utf-8")
                # if isinstance(post_data, dict):
                #     req_body = urllib.urlencode(post_data)
                #     # req_body = post_data
                # elif isinstance(post_data, unicode) or isinstance(post_data, str):
                #     req_body = post_data

                # 针对json 格式的请求，增加支持
                # if "application/json" in req_headers.get("Content-Type", ""):
                #     req_body = json.loads(req_body)
            else:
                req_body = None
            # print req_body
            # pdb.set_trace()
            # ------------------------------------------
            # 处理其他的特色附加信息，这个也是非常重要的
            # 特色附加信息，都是挂载在 easyspider 下的
            # 注意这里忽略了 exo_info 错误信息
            # 2018年03月04日18:07:51   以下都是错的，作为一个解析任务的函数，为什么还需要做处理呢
            # 直接带上就好了啊
            req_meta = start_map.get("meta", {}) or {}
            # last_easyspider = req_meta.get("easyspider") or {}
            # easyspider_info = {
            #     # 是否来源于错误提交
            #     "from_retry": last_easyspider.get("from_retry", 0),
            #     # 真实的起始链接，如果没有，就是当前的链接
            #     "source_start_url": last_easyspider.get("source_start_url") or req_url,
            #     # 备注信息，一般没有
            #     "remark": last_easyspider.get("remark"),
            #     # 爬虫经过的全部路径，调试的非常重要，这样就知道为什么被卡住了
            #     "crawled_urls_path": last_easyspider.get("crawled_urls_path") or []
            # }
            # req_meta.update({"easyspider": easyspider_info})

            # ------------------------------------------
            # 最终才能够组合完成
            return Request(url=req_url,
                           callback=req_callback_method,
                           method=req_method,
                           meta=req_meta,
                           body=req_body,
                           headers=req_headers,
                           cookies=req_cookies,
                           dont_filter=close_filter
                           )
        except Exception:
            self.logger.exception(u"parse start url error, source start url is %s" % start_map)

    def is_blocked_spider(self, response):
        """检测爬虫是否被屏蔽的方法。每个成功的请求，都会进入这个函数
        默认为 False, 即爬虫没有被屏蔽，没有被屏蔽，那么就会进入正常流程，接下来调用对应callback

        可以重写这个函数，来检测爬虫是否被屏蔽，比如检测
        u"次数过多" in resposne.body
        出现这个情况的时候，就是True，爬虫就被屏蔽，就不会进入接下来的callback正常流程
        接下里就会调用blocked_call_back， 来进行屏蔽处理

        method is called every time to check if blocked the spider, default to be False or None
        """
        pass

    def blocked_call_back(self, response, reason="spider was blocked", exc_info=None, extra=None):
        """兼容历史老代码的api
        """
        self.blocked_callback(response, reason, exc_info, extra)

    def blocked_callback(self, response, reason=u"spider was blocked", exc_info=None, extra=None):
        """如果检测到爬虫被屏蔽，那么就会调用这个函数来对进行处理
        默认的操作是重新放回 任务队列的队尾，可以通过重写这个方法，来完成自定义的 屏蔽处理逻辑

        注意一点：这个函数，并不只是在被屏蔽的时候可以调用，它是 【通用的】
        即，当你需要重新抓取某个链接的时候，可以通过 【假装这个链接被屏蔽了】，来达到重新抓取的效果

        一个典型应用就是： 我在列表页list发现了新的任务，通过调用blocked_call_back 的put_back_2_start_url, 达到添加任务的效果

        method called when spider is blocked, also can be used to record other error situation"""

        # 记录这个状态，即爬虫出现问题
        self.report_this_crawl_2_log(response, reason, exc_info)
        # 重新添加任务
        if not exc_info:
            # 如果没有exc_info 那么说明就是从 is_spider_blocked 过来的，附带上被屏蔽返回的代码
            exc_info = "%s; response.body %s" % (reason, self.get_unicode_response_body(response))
        self.put_back_2_start_url(response, exc_info)

    def report_this_crawl_2_log(self, response, reason, exc_info=None):
        """记录此次请求
        log this response
        """
        if not exc_info:
            # 在 redirectmiddleware 中，是直接的reason，没有返回exc_info的
            # 适应之前代码
            exc_info = reason
        report_template = u"""
            response body -> %(response_body)s
            %(response)s is recorded, because %(reason)s happended, following are detail info:
            response url -> %(response_url)s,
            status code -> %(status_code)s,
            request url -> %(request_url)s,
            original request url -> %(original_request_url)s

            request headers -> %(request_headers)s,
            request body -> %(request_body)s,

            request callback -> %(request_callback)s,

            exc_info -> %(exc_info)s
            """

        report_info = {
            "response": response.url,
            "reason": reason,
            "response_url": response.url,
            "status_code": response.status,
            "request_url": response.request.url,
            "original_request_url": self.get_source_url(response),
            "request_headers": response.request.headers.to_unicode_dict(),
            # dict type
            "request_body": self.get_request_body(response),
            # u"request_callback": response.request.callback.__name__,
            "request_callback": self.get_last_request_callback(response),
            # unciode body
            "response_body": self.get_unicode_response_body(response),
            "exc_info": exc_info,
        }

        self.logger.warning(report_template % report_info)

    def get_common_request(self, r):
        """兼容Reques和Response 的状态，统一变为request状态
        避免修改，返回的都是副本

        注意：Request object can't use copy
        """
        if isinstance(r, Response):
            # Request object can't use copy
            # r_copy = copy.deepcopy(r.request)
            r_copy = r.request.copy()
        else:
            # r_copy = copy.deepcopy(r)
            r_copy = r.copy()
        return r_copy

    def get_source_url(self, r):
        """获得最原始的的请求链接
        因为在302跳转的情况下，当前的链接，并不是最开始的任务链接
        to get the original url, because 302 will modified the request url
        """
        r_copy = self.get_common_request(r)

        source_url = r_copy.meta.get("easyspider", {}).get("source_start_url")
        redirect_urls = r_copy.meta.get("redirect_urls") or []

        if source_url:
            # 如果source_start_url里面有内容(即在任务里面，就注明了初始url 这个优先级是最高的)
            return source_url
        elif len(redirect_urls) > 0:
            # 第二优先级，是取redirect_urls里面的第一个url
            return redirect_urls[0]
        else:
            # 实在是什么都没有，那么初始链接，就是当前的链接
            return r_copy.url

    def get_request_body(self, r):
        """把字符串的请求体，变成字典类型，方便人类查看
        return str/unicode request body -> dict
        """
        r_copy = self.get_common_request(r)
        try:
            return r_copy.body.decode("utf-8")
        except:
            # 判断是否二进制数据，如果是二进制数据，需要编码base64
            if isinstance(r_copy.body, bytes):
                self.logger.info("Requests body 格式为二进制流，将编码为base64 并解码为utf-8字符串")
                self.is_base64 = True
                return base64.b64encode(r_copy.body).decode("utf-8")
            return r_copy.body
        dict_body = self.parse_query_2_dict(r_copy.body)

        # pdb.set_trace()
        if not dict_body:
            try:
                # dict_body = json.dumps(r_copy.body, ensure_ascii=False)
                dict_body = r_copy.body
            except Exception:
                self.logger.exception("convert request body failed... source body is %s" % r_copy.body)
        return dict_body

    def parse_query_2_dict(self, query):
        """parse url query to dict format"""
        try:
            return dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])
        except Exception:
            self.logger.exception("can't parse url -> dict, source url data is %s" % query)

    def detect_encoding(self, body):
        dammit = UnicodeDammit(body)
        return dammit.original_encoding

    def get_unicode_response_body(self, response):
        """避免乱码，在保存的时候，所有的body 都会被解码成unicode形式
        """
        return response.body_as_unicode()
        encoding = self.detect_encoding(response.body)
        if encoding:
            # 有编码则解码，无编码则直接返回，因为无编码的话，按照None解码将会出错
            # TypeError: decode() argument 1 must be string, not None
            # print u"检测编码结果是：%s" % encoding
            try:
                # 如果请求的是图片，那么检测出来的虽然是utf-8 但是是无法解码的
                # 保存直接保存整个body 就可以了
                return response.body.decode(encoding)
            except Exception:
                msg = traceback.format_exc()
                return u"decode response error, msg is %s" % msg
        return response.body

    def put_back_2_start_url(self, r, exc_info=None, last_response=None):
        """非常有效的核心通用函数
        这个函数不只是在 检测是否被屏蔽的时候可以调用

        还可以被充当，添加新任务的功能。
        如果需要添加一个新的任务，那么直接调用这个函数就可以了

        reput request to redis
        """

        r_copy = self.get_common_request(r)

        # 基于这样一种情况，如果某个response 不是正确的response
        # 那么就根据这个错误response，对应的request，生成新的request
        if not last_response:
            last_response_copy = r_copy
        else:
            last_response_copy = self.get_common_request(last_response)

        # 检查这个任务，是否需要提高优先级，默认优先级为0
        if hasattr(r_copy, "priority"):
            priority = r_copy.priority or 0
        else:
            priority = 0

        # 最原始的reput_request
        reput_request = {
            "url": self.get_source_url(r_copy),
            "callback": self.get_last_request_callback(r_copy),
            "method": r_copy.method,
            "headers": r_copy.headers.to_unicode_dict(),
            "dont_filter": False if (not hasattr(r, "dont_filter") or r.dont_filter is None) else r.dont_filter,
            "priority": priority,
        }

        # ------------------------------------------
        # 检测请求体：
        # 如果这个请求不是GET类型，那么需要添加请求体body
        reput_request["body"] = self.get_request_body(r_copy)

        if reput_request.get("method") == "GET":
            reput_request.pop("body")

        # ------------------------------------------
        # 更新附加信息

        meta = copy.deepcopy(r_copy.meta)
        # 判断是否是base64二进制编码
        if self.is_base64:
            if "is_base64" not in meta:
                meta["is_base64"] = True
        # pdb.set_trace()
        last_easyspider = meta.get("easyspider") or {}
        last_easyspider.update({
            "from_retry": (int(last_easyspider.get(u"from_retry", -1)) + 1),
            "source_start_url": self.get_source_url(r_copy),
            "remark": last_easyspider.get(u"remark"),
            "crawled_urls_path": last_easyspider.get("crawled_urls_path", []) + [last_response_copy.url],
            "exc_info": exc_info
        })
        # ------------------------------------------
        # 记录当前的时间，和出现问题时候的IP(机器)
        # ------------------------------------------
        try:
            last_easyspider["crawled_server"] = ";".join(flat(socket.gethostbyname_ex(socket.gethostname())))
        except Exception:
            # 没想到这里也引用了
            last_easyspider["crawled_server"] = socket.gethostname()
        last_easyspider["crawled_time"] = get_time()

        meta["easyspider"] = last_easyspider
        reput_request["meta"] = meta

        # ------------------------------------------
        # 检测cookie:
        # 如果开启了cookie，那么cookie随之保存启用
        if self.settings.get(u"COOKIES_ENABLED"):
            reput_request["cookies"] = r_copy.cookies

        # ------------------------------------------
        # 开始存入 redis 任务队列，存入不成功，一直存入
        current_retry_time = reput_request.get("meta").get("easyspider").get("from_retry")
        while True:
            try:
                max_retry_time = self.retry_max_time + 1
                try:
                    dumps_str = json.dumps(reput_request, ensure_ascii=False)
                except Exception:
                    try:
                        traceback.print_exc()
                        import pdb
                        # pdb.set_trace()
                        exc_info = json.dumps(reput_request["meta"]["easyspider"]["exc_info"], ensure_ascii=False)
                    #     json.dumps(exc_info, ensure_ascii=False)
                    #     json.dumps(reput_request["meta"]["easyspider"], ensure_ascii=False)
                        reput_request["meta"]["easyspider"]["exc_info"] = exc_info.decode("gbk")
                        # reput_request["meta"]["easyspider"]["exc_info"] = exc_info.decode("gbk")

                        dumps_str = json.dumps(reput_request, ensure_ascii=False)
                    except Exception:
                        #     traceback.print_exc()
                        #     traceback.print_exc()
                        traceback.print_exc()
                        # pdb.set_trace()
                if current_retry_time >= max_retry_time:
                    # 如果超过了重试次数的限制，那么就放回failed
                    try:
                        self.save_into_redis_method(self.server)("%s:%s" % (self.name, self.failed_key), dumps_str)
                    except Exception:
                        exc_info = json.dumps(reput_request["meta"]["easyspider"]["exc_info"], ensure_ascii=False)
                        reput_request["meta"]["easyspider"]["exc_info"] = exc_info
                        # json.dumps(reput_request["meta"]["easyspider"], ensure_ascii=False)
                        try:
                            self.save_into_redis_method(self.server)("%s:%s" % (self.name, self.failed_key), json.dumps(reput_request, ensure_ascii=False))
                        except:
                            traceback.print_exc()
                            # pdb.set_trace()
                    self.logger.info("超过重试的最大次数限制，放入到 failed key 中")
                # elif reput_request.get("priority") != 0:
                elif reput_request.get("priority") > 0:
                    # 有时候priority还会出现负数的情况
                    # 如果是优先任务，那么放入优先任务队列
                    self.save_into_priority_queue(self.server, "%s:%s" % (self.name, self.priority_start_key), float(reput_request.get("priority")), dumps_str)
                else:
                    # 其他的放入普通任务
                    self.save_into_redis_method(self.server)("%s:%s" % (self.name, self.start_key), dumps_str)
                break
            except Exception:
                msg = traceback.format_exc()
                self.logger.exception("in easyCrawlSpider: put_back_2_start_url,  self.save_into_redis_method failed, loop until it successed.. reput_request is %s, %s" % (reput_request, msg))
                # break
                # current_retry_time += 1
                # time.sleep(2)
                # 需要重新加入，而不是简单的在这里退出，因为涉及到最后对 exc_info 字段的处理，当前进来第一次exc_info是空的，要等到后面自动来添加
                # self.put_back_2_start_url(r)
                # raise Exception(msg)

        # logginig
        put_back_logging_template = """reput crawl task into start url, detail info are %s"""
        self.logger.info(put_back_logging_template % reput_request)

    def get_last_request_callback(self, r):
        r_copy = self.get_common_request(r)
        if not r_copy.callback:
            return "self.parse"
        return "self.%s" % r_copy.callback.__name__

    def parse_request_to_dict(self, r):
        """这家伙不能删除。。。在 core/easyScraper.py 中会调用。。坑爹
        return error request to start step
        """
        if isinstance(r, Response):
            # r_copy = copy.deepcopy(r.request)
            r_copy = r.request.copy()
        else:
            # r_copy = copy.deepcopy(r)
            r_copy = r.copy()

        reput_request = {
            u"url": self.get_source_url(r_copy),
            # u"callback": r_copy.callback.__name__,
            u"callback": self.get_last_request_callback(r_copy),
            u"method": r_copy.method,
            u"body": self.get_request_body(r_copy),
            u"headers": r_copy.headers.to_unicode_dict(),
            u"dont_filter": r_copy.dont_filter
        }

        meta = copy.deepcopy(r.meta)
        # direct launch Requst from start_requests won't have start_url template
        meta.get(u"easyspider", {}).update({
            u"from_retry": int(meta.get(u"easyspider", {}).get(u"from_retry", 0) or 0) + 1,
            u"source_start_url": self.get_source_url(r_copy),
            u"remark": meta.get(u"easyspider", {}).get(u"remark"),
        })
        reput_request["meta"] = meta
        # TODO: check if need to save cookies
        if self.settings.get(u"COOKIES_ENABLED"):
            reput_request["cookies"] = r_copy.cookies
        else:
            reput_request["cookies"] = None
        return reput_request

    def extract_text_and_strip(self, xpath_exp):
        """用来方便的获取某个下面所有的text"""
        return "".join(xpath_exp.xpath(".//text()").extract()).strip()

    def text_strip(self, t):
        """增强型strip 用来方便的过滤掉其他的乱字符"""
        return t.strip().replace("\r", "").replace("\n", "").replace("\t", "")
