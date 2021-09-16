# 工具箱中的工具都是开箱即用的，不依赖特别的数据、配置和业务逻辑

from sometools.string_tools.string_cleaning import GeneralString
from sometools.log_tools.logger_main import GeneralLog
from sometools.datetime_tools.date_conversion import GeneralDatetime
from sometools.chinese_to_pinyin_acronym.chinese_to_pinyin import GeneralChineseToPinyin
from sometools.traditional_simplified_chinese_conversion.traditional_simplified_chinese import GeneralTraditionalSimplifiedChinese
from sometools.url_tools.url_encode_decode import GeneralUrlEncodeDecode


class Common_tools(GeneralChineseToPinyin, GeneralTraditionalSimplifiedChinese, GeneralUrlEncodeDecode, GeneralDatetime, GeneralString, GeneralLog):
    def __init__(self, *args, **kwargs):
        super(Common_tools, self).__init__(*args, **kwargs)
