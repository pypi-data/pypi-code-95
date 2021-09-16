# coding=utf-8

# 测试: scrapy crawl spider_name -s SCHEDULER_FLUSH_ON_START=True
# 部署: scrapy crawl spider_name -s LOG_FILE=spider_name.log -s
# LOG_LEVEL=INFO -s LOG_STDOUT=True

REDIS_URL = "redis://127.0.0.1:6379"
MONGO_URL = "mongodb://127.0.0.1:27017/"

MONGO_DB_NAME = "easyspider"

ITEM_PIPELINES = {
    'easyspider.pipelines.pipelines.ExamplePipeline': 500,
    "easyspider.pipelines.easy_mongo_pipeline.easyMongoPipeline": 504,
}

DOWNLOAD_TIMEOUT = 10

# 0的速度太恐怖了
DOWNLOAD_DELAY = 2

# 禁用cookies  因为默认的居然还是开...
COOKIES_ENABLED = False

# 开启后可以看到每次的cookies状态
COOKIES_DEBUG = True

REDIRECT_MAX_TIMES = 3  # 最大重定向次数

# HTTPERROR_ALLOWED_CODES = [200, 301, 302, 303, 304, 305, 306]
# 忽略该列表中所有非200状态码的response
HTTPERROR_ALLOWED_CODES = [301, 302, 303, 304, 305, 306]

DOWNLOADER_MIDDLEWARES = {
    # 修改UA头
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "easyspider.middlewares.useragent.userAgentMiddleware": 400,
    # 超过次数的跳转直接返回，不丢弃.跳转全部都是dont_filter
    "scrapy.downloadermiddlewares.redirect.RedirectMiddleware": None,
    "easyspider.middlewares.redirect.directReturnRedirectMiddleware": 600,
    # 连接超时(代理无效)或者50X的错误(其实还有400和408)，就需要重试，超过重试次数，不丢弃give up,而是重新放回入口链接
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
    "easyspider.middlewares.retry.retryToStartMiddleware": 500,
}

SPIDER_MIDDLEWARES = {
    # 类似于404的错误记录到redis中去
    "scrapy.spidermiddlewares.httperror.HttpErrorMiddleware": None,
    "easyspider.middlewares.httperror.recordHttpErrorMiddleware": 50,
    # 是否被block的判断
    "easyspider.middlewares.antiSpider.antiSpiderMiddleware": 950,
}

# 没有不行, 这是scrapy寻找spider的路径
SPIDER_MODULES = ['easyspider.spiders']

# NEWSPIDER_MODULE = 'easyspider.spiders'

# redis 作为去重器
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 使用自定义的调度器
SCHEDULER = "easyspider.core.scheduler.easyScheduler"

# 显示所有被过滤器过滤掉的请求
DUPEFILTER_DEBUG = True

# 状态收集器scrapy.extensions.logstats打印日志的频率
LOGSTATS_INTERVAL = 1

# 允许自定义引擎
ENGINE = "easyspider.core.easyEngine.easyEngine"

# 允许自定义scraper
SCRAPER = "easyspider.core.easyScraper.easyScraper"
