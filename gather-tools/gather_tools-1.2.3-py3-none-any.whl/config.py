# -*- coding:utf-8 -*-
import configparser
class config():
    def __init__(self):
        self.config = configparser.ConfigParser()

    def read(self, file, encoding='GB18030'):
        return self.config.read(file, encoding)
     # -sections得到所有的section，并以列表的形式返回

    def sections(self):
        return self.config.sections()

    # -options(section)得到该section的所有option
    def options(self, section):
        return self.config.options(section)
    # 得到该section的所有键值对
    def options(self, section):
        return self.config.items(section)

    #返回为string类型
    def get(self, section, key):
        return self.config.get(section, key)

    def getint(self, section, key):
        return self.config.getint(section, key)

    def getfloat(self, section, key):
        return self.config.getfloat(section, key)

    def getboolean(self, section, key):
        return self.config.getboolean(section, key)
