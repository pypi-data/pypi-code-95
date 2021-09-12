from xml.dom import minidom
from danmu_utils.common.IConverter import IConverter
from danmu_utils.plugin.bilibili.BilibiliGenerator import BilibiliGenerator


class IqiyiToBilibiliConverter(IConverter):
    @property
    def DANMU_TYPE_SRC(self):
        return 'iqiyi'

    @property
    def DANMU_TYPE_DST(self):
        return 'bilibili'

    @property
    def DANMU_EXTNAME_SRC(self):
        return 'iqyxml'

    @property
    def DANMU_EXTNAME_DST(self):
        return 'xml'

    def convert(self, data):
        bilibiliGenerator = BilibiliGenerator()
        item_src = minidom.parseString(data)
        for entry_src in item_src.getElementsByTagName('danmu')[0].getElementsByTagName('data')[0].getElementsByTagName('entry'):
            for bullet_info in entry_src.getElementsByTagName('list')[0].getElementsByTagName('bulletInfo'):
                try:
                    text = bullet_info.getElementsByTagName('content')[0].childNodes[0].nodeValue
                    send_time = float(bullet_info.getElementsByTagName('showTime')[0].childNodes[0].nodeValue)
                    color = int(bullet_info.getElementsByTagName('color')[0].childNodes[0].nodeValue, 16)
                    sender_id = int(bullet_info.getElementsByTagName('userInfo')[0].getElementsByTagName('uid')[0].childNodes[0].nodeValue)
                except Exception as e:
                    print(e)
                    continue
                bilibiliGenerator.append(text, send_time, color=color, sender_id=sender_id)
        return bilibiliGenerator.output()


from danmu_utils.common.plugin_collection import add_convert_tool

add_convert_tool(IqiyiToBilibiliConverter().DANMU_TYPE_SRC, IqiyiToBilibiliConverter().DANMU_TYPE_DST, IqiyiToBilibiliConverter)
