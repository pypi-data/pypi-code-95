import logging
from logging import handlers

"""
https://www.cnblogs.com/nancyzhu/p/8551506.html
https://www.cnblogs.com/xianyulouie/p/11041777.html
"""

level_mp = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

class Logger(object):
    instance = {}

    def __init__(self, filename, level='info', when='D', backCount=10, fmt='%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        self.format_str = logging.Formatter(fmt)
        self.logger.setLevel(level_mp[level])

        # redirct to console
        console = logging.StreamHandler()
        console.setFormatter(self.format_str)
        self.logger.addHandler(console)

        # wirte to file
        handler = handlers.TimedRotatingFileHandler(filename=filename,      # 保存路径
                                                    when=when,              # 间隔的时间单位，单位有: S秒，M 分，H 小时，D 天，W 每星期（interval==0时代表星期一），midnight 每天凌晨
                                                    backupCount=backCount,  # 文件的个数，如果超过这个个数，就会自动删除
                                                    encoding='utf-8')
        handler.setFormatter(self.format_str)
        self.logger.addHandler(handler)


    @classmethod
    def get_instance(cls, filename, **kwargs):
        file_name = filename.split("/")[-1]
        if file_name not in cls.instance:
            cls.instance[file_name] = Logger(filename, **kwargs)
        return cls.instance[file_name]

if __name__ == '__main__':
    # server
    app = Logger.get_instance('app.log', level='debug')
    app.logger.debug('debug')
    app.logger.info('info')
    app.logger.warning('警告')
    app.logger.error('报错')
    app.logger.critical('严重')

    # db
    db = Logger('error.log', level='error')
    db.logger.error('error')