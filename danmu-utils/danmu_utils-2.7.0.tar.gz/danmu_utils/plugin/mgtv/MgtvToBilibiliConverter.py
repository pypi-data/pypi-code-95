import json
from danmu_utils.common.IConverter import IConverter
from danmu_utils.plugin.bilibili.BilibiliGenerator import  BilibiliGenerator


class DiyidanToBilibiliConverter(IConverter):
    @property
    def DANMU_TYPE_SRC(self):
        return 'mgtv'

    @property
    def DANMU_TYPE_DST(self):
        return 'bilibili'

    @property
    def DANMU_EXTNAME_SRC(self):
        return 'mgtvjson'

    @property
    def DANMU_EXTNAME_DST(self):
        return 'xml'

    def convert(self, data):
        bilibiliGenerator = BilibiliGenerator()
        try:
            item_src = json.loads(data)
        except Exception as e:
            print(e)
            return None
        for entry_src in item_src['data']['items']:
            try:
                text = entry_src['content']
                send_time = entry_src['time'] / 1000
                color = 0xffffff
                sender_id = entry_src['uid']
            except Exception as e:
                print(e)
                continue
            bilibiliGenerator.append(text, send_time, color=color, sender_id=sender_id)
        return bilibiliGenerator.output()


from danmu_utils.common.plugin_collection import add_convert_tool

add_convert_tool(DiyidanToBilibiliConverter().DANMU_TYPE_SRC, DiyidanToBilibiliConverter().DANMU_TYPE_DST, DiyidanToBilibiliConverter)
