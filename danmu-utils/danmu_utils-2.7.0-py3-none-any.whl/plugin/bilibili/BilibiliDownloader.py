import urllib.request
import zlib

from danmu_utils.common.IDownloader import IDownloader


class BilibiliDownloader(IDownloader):
    @property
    def DANMU_TYPE(self):
        return 'bilibili'

    @property
    def DANMU_EXTNAME(self):
        return 'xml'

    @property
    def DANMU_LIST_EXTNAME(self):
        return 'xmllist'

    def __deflate(self, data):
        try:
            return zlib.decompress(data, -zlib.MAX_WBITS)
        except zlib.error:
            return zlib.decompress(data)

    def _download(self, aid):
        url = 'https://comment.bilibili.com/%s.xml' % (aid)
        with urllib.request.urlopen(url) as f:
            danmu = f.read()
        return self.__deflate(danmu)

    def download(self, line):
        line_res = []
        line_params = line.strip('\n').split('\t')
        aid = line_params[0]
        res = self._download(aid)
        item_res = {}
        item_res['filename'] = aid + '.' + self.DANMU_EXTNAME
        item_res['data'] = res
        line_res.append(item_res)
        return line_res


from danmu_utils.common.plugin_collection import add_download_tool
add_download_tool(BilibiliDownloader().DANMU_TYPE, BilibiliDownloader)