import json
from xml.dom import minidom
from danmu_utils.common.IConverter import IConverter
from danmu_utils.plugin.bilibili.BilibiliGenerator import BilibiliGenerator


class YoukuToBilibiliConverter(IConverter):
    @property
    def DANMU_TYPE_SRC(self):
        return 'youku'

    @property
    def DANMU_TYPE_DST(self):
        return 'bilibili'

    @property
    def DANMU_EXTNAME_SRC(self):
        return 'ykjson'

    @property
    def DANMU_EXTNAME_DST(self):
        return 'xml'

    def convert(self, data):
        bilibiliGenerator = BilibiliGenerator()
        item_src = json.loads(data)
        for entry_src in item_src['result']:
            try:
                text = entry_src['content']
                send_time = entry_src['playat'] / 1000
                color = 16777215
                if (entry_src["propertis"] != ""):
                    propertis = json.loads(entry_src["propertis"])
                    if "color" in propertis.keys():
                        color = int(propertis["color"])
                sender_id = entry_src['uid']
            except Exception as e:
                print(e)
                continue
            bilibiliGenerator.append(text, send_time, color=color, sender_id=sender_id)
        return bilibiliGenerator.output()


from danmu_utils.common.plugin_collection import add_convert_tool

add_convert_tool(YoukuToBilibiliConverter().DANMU_TYPE_SRC, YoukuToBilibiliConverter().DANMU_TYPE_DST, YoukuToBilibiliConverter)
