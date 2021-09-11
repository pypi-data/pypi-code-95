import json
from xml.dom import minidom
from danmu_utils.common.IConverter import IConverter
from danmu_utils.plugin.bilibili.BilibiliGenerator import  BilibiliGenerator


class DiyidanToBilibiliConverter(IConverter):
    @property
    def DANMU_TYPE_SRC(self):
        return 'diyidan'

    @property
    def DANMU_TYPE_DST(self):
        return 'bilibili'

    @property
    def DANMU_EXTNAME_SRC(self):
        return 'dydjson'

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
        for entry_src in item_src['data']['danmakuList']:
            try:
                if 'text' in entry_src:
                    text = entry_src['text']
                    send_time = entry_src['time'] / 10
                    color = int(entry_src['color'].split('#')[1], 16)
                    sender_id = entry_src['danmakuId']
                elif 'danmakuContent' in entry_src:
                    text = entry_src['danmakuContent']
                    send_time = entry_src['danmakuTime'] / 1000
                    color = entry_src['danmakuTextColor']
                    sender_id = entry_src['danmakuId']
                else:
                    continue
            except Exception as e:
                print(e)
                continue
            bilibiliGenerator.append(text, send_time, color=color, sender_id=sender_id)
        return bilibiliGenerator.output()


from danmu_utils.common.plugin_collection import add_convert_tool

add_convert_tool(DiyidanToBilibiliConverter().DANMU_TYPE_SRC, DiyidanToBilibiliConverter().DANMU_TYPE_DST, DiyidanToBilibiliConverter)
