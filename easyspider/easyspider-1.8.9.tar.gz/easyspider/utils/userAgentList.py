# coding=utf-8

UA_headers = [  # 浏览器头信息 (PC端)
    # 我自己浏览器标志
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36'},
    # safari 5.1 – MAC
    {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
    # safari 5.1 – Windows
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
    # Firefox 4.0.1 – MAC
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
    # Firefox 4.0.1 – Windows
    # {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
    # Opera 11.11 – MAC
    # {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},
    # Opera 11.11 – Windows
    # {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36 OPR/47.0.2631.71'},
    # Chrome 17.0 – MAC
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},
    # 傲游（Maxthon）
    # # 在某些服务器上，已经不能使用，会报浏览日过老的错误。
    # {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)'},
    # 腾讯TT
    # # 在某些服务器上，已经不能使用，会报浏览日过老的错误。
    # {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)'},
    # 世界之窗（The World） 3.x
    # # 在某些服务器上，已经不能使用，会报浏览日过老的错误。
    # {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)'},
    # IE 9.0
    # # 在某些服务器上，已经不能使用，会报浏览日过老的错误。
    # {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'},
    # IE 8.0
    # 在某些服务器上，已经不能使用，会报浏览日过老的错误。
    # {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)'}
]

r"""

opera ua header is error... must start with Mozilla*
Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36 OPR/47.0.2631.71






http://www.zydmall.com/detail/good_2919.html


2017-09-07 10:44:58 [zydDetail] INFO: http://www.zydmall.com/ashx/detail_product
s.ashx is recorded, because Spider error processing <POST http://www.zydmall.com
/ashx/detail_products.ashx> (referer: http://www.zydmall.com/detail/good_3240.ht
ml): info (<class 'scrapy.spidermiddlewares.httperror.HttpError'>, HttpError('Ig
noring non-200 response',), <traceback object at 0x00000000058CBE08>) happended,
 following are detail info:
            response url -> http://www.zydmall.com/ashx/detail_products.ashx,
            status code -> 404,
            request url -> http://www.zydmall.com/ashx/detail_products.ashx,
            original request url -> http://www.zydmall.com/ashx/detail_products.
ashx

            request headers -> {'Accept-Language': ['en'], 'Accept-Encoding': ['
gzip,deflate'], 'Accept': ['text/html,application/xhtml+xml,application/xml;q=0.
9,*/*;q=0.8'], 'User-Agent': ['Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131
 Version/11.11'], 'Referer': ['http://www.zydmall.com/detail/good_3240.html'], '
Content-Type': ['application/x-www-form-urlencoded; charset=UTF-8']},
            request body -> {'pid': '255072', 'goods_id': '3240'},

            request callback -> self.parse,

            response body -> <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict
//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=gb2312"/>
<title>404 - 找不到文件或目录。</title>
<style type="text/css">
<!--
body{margin:0;font-size:.7em;font-family:Verdana, Arial, Helvetica, sans-serif;b
ackground:#EEEEEE;}
fieldset{padding:0 15px 10px 15px;}
h1{font-size:2.4em;margin:0;color:#FFF;}
h2{font-size:1.7em;margin:0;color:#CC0000;}
h3{font-size:1.2em;margin:10px 0 0 0;color:#000000;}
#header{width:96%;margin:0 0 0 0;padding:6px 2% 6px 2%;font-family:"trebuchet MS
", Verdana, sans-serif;color:#FFF;
background-color:#555555;}
#content{margin:0 0 0 2%;position:relative;}
.content-container{background:#FFF;width:96%;margin-top:8px;padding:10px;positio
n:relative;}
-->
</style>
</head>
<body>
<div id="header"><h1>服务器错误</h1></div>
<div id="content">
 <div class="content-container"><fieldset>
  <h2>404 - 找不到文件或目录。</h2>
  <h3>您要查找的资源可能已被删除，已更改名称或者暂时不可用。</h3>
 </fieldset></div>
</div>
</body>
</html>

2017-09-07 10:44:59 [zydDetail] INFO: reput crawl task into start url, detail in
fo are {u'body': {'pid': '255072', 'goods_id': '3240'}, 'cookies': None, u'heade
rs': {'Accept-Language': ['en'], 'Accept-Encoding': ['gzip,deflate'], 'Accept':
['text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'], 'User-Agent
': ['Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'], 'Referer
': ['http://www.zydmall.com/detail/good_3240.html'], 'Content-Type': ['applicati
on/x-www-form-urlencoded; charset=UTF-8']}, u'url': u'http://www.zydmall.com/ash
x/detail_products.ashx', u'dont_filter': True, u'callback': 'self.parse', 'meta'
: {u'last_page_result': {u'category_channel': u'\u9996\u9875>\u4f4e\u538b\u914d\
u7535>\u5851\u58f3\u65ad\u8def\u5668>\u5851\u58f3\u914d\u7535\u4fdd\u62a4>\u5929
\u6b63\u7535\u6c14 THM1-250A 50KA \u56fa\u5b9a\u5f0f 3P \u5851\u58f3\u914d\u7535
\u4fdd\u62a4', u'pid': u'255072', u'main_panel': {u'\u6298\u6263\u4ef7\uff1a': u
'\xa5;780.00', u'\u9762\u4ef7\uff1a': u'\xa5780.00', u'\u7cfb\u5217\uff1a': u'TH
M1', u'\u54c1\u724c\uff1a': u'\u5929\u6b63\u7535\u6c14'}, u'goods_id': u'3240',
u'th_header': [u'\u8ba2\u8d27\u53f7', u'\u4ea7\u54c1\u578b\u53f7', u'\u9762\u4ef
7', u'\u6298\u6263\u4ef7', u'\u5e93\u5b58', u'\u8d27\u671f', u'\u6570\u91cf', u'
\u91cd\u91cf(g)', u'\u5355\u4f4d', u'\u58f3\u67b6\u7535\u6d41', u'\u5206\u65ad\u
80fd\u529b', u'\u8131\u6263\u5f62\u5f0f', u'\u8131\u6263\u5355\u5143', u'\u8131\
u6263\u5668\u989d\u5b9a\u7535\u6d41', u'\u6781\u6570', u'\u5b89\u88c5\u65b9\u5f0
f', u'\u63a5\u7ebf\u65b9\u5f0f', u'\u64cd\u4f5c\u65b9\u5f0f', u'\u4fdd\u62a4\u52
9f\u80fd', u'\u989d\u5b9a\u7535\u538b', u'\u9644\u4ef6']}, u'download_timeout':
7.0, u'depth': 1, u'download_latency': 0.06199979782104492, u'download_slot': u'
www.zydmall.com', u'easyspider': {u'from_retry': 1, u'remark': None, u'source_st
art_url': u'http://www.zydmall.com/ashx/detail_products.ashx'}}, u'method': 'POS
T'}
2017-09-07 10:44:59 [scrapy.extensions.logstats] INFO: Crawled 201 pages (at 60
pages/min), scraped 0 items (at 0 items/min)
















curl -vXPOST http://www.zydmall.com/ashx/detail_products.ashx \
-H "Content-Type': application/x-www-form-urlencoded; charset=UTF-8" \
-H "Referer: http://www.zydmall.com/detail/good_2919.html" \
-H "X-Requested-With: XMLHttpRequest" \
-H "User-Agent: Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11" \
-d "goods_id=2919&pid=229752" | iconv -f gbk

curl -vXPOST http://www.zydmall.com/ashx/detail_products.ashx \
-H "Content-Type': application/x-www-form-urlencoded; charset=UTF-8" \
-H "Referer: http://www.zydmall.com/detail/good_2919.html" \
-H "X-Requested-With: XMLHttpRequest" \
-H "User-Agent: Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36" \
-d "goods_id=2919&pid=229752"


curl -vXPOST http://www.zydmall.com/ashx/detail_products.ashx \
-H "Content-Type': application/x-www-form-urlencoded; charset=UTF-8" \
-H "Referer: http://www.zydmall.com/detail/good_2919.html" \
-H "X-Requested-With: XMLHttpRequest" \
-H "User-Agent: Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11" \
-d "goods_id=2919&pid=229752" | iconv -f gbk

"""