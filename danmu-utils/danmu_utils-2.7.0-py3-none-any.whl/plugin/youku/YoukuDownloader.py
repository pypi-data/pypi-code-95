import urllib.request
import urllib
from urllib.parse import urlencode
import json
import re

from danmu_utils.common.IDownloader import IDownloader


class YoukuDownloader(IDownloader):
    @property
    def DANMU_TYPE(self):
        return 'youku'

    @property
    def DANMU_EXTNAME(self):
        return 'ykjson'

    @property
    def DANMU_LIST_EXTNAME(self):
        return 'yklist'

    def _download(self, videoId):
        param_now = {
            "mcount": "1",
            "ct": "1001",
            "iid": "",
        }
        danmu_collect = {
            "count": 0,
            "filtered": 1,
            "result": [],
        }
        param_now["iid"] = videoId
        j = 0
        while(True):
            param_now["mat"] = j
            query = urlencode(param_now)
            url = "https://service.danmu.youku.com/list?%s" % query
            print('Start download: "%s".' % url)
            try:
                with urllib.request.urlopen(url) as f:
                    body = f.read()
            except Exception as e:
                print(e)
                break
            danmus = re.findall(r"\{.*\}", str(body, encoding='utf-8'))
            danmu = danmus[0]
            try:
                danmu_json = json.loads(danmu)
            except Exception as e:
                print(e)
                break
            if danmu_json["count"] == 0:
                print("Section download finished: %s" % videoId)
                break
            try:
                danmu_collect["count"] += danmu_json["count"]
                danmu_collect["result"].extend(danmu_json["result"])
            except Exception as e:
                print(e)
                break
            j += 1
        return json.dumps(danmu_collect, ensure_ascii=False).encode(encoding='utf-8')

    def download(self, line):
        line_res = []
        line_params = line.strip('\n').split('\t')
        videoId = line_params[0]
        res = self._download(videoId)
        item_res = {}
        item_res['filename'] = videoId + '.' + self.DANMU_EXTNAME
        item_res['data'] = res
        line_res.append(item_res)
        return line_res


from danmu_utils.common.plugin_collection import add_download_tool
add_download_tool(YoukuDownloader().DANMU_TYPE, YoukuDownloader)