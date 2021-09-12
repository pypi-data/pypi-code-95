import urllib.request

from danmu_utils.common.IDownloader import IDownloader


class DiyidanDownloader(IDownloader):
    @property
    def DANMU_TYPE(self):
        return 'diyidan'

    @property
    def DANMU_EXTNAME(self):
        return 'dydjson'

    @property
    def DANMU_LIST_EXTNAME(self):
        return 'dydlist'

    def _download(self, videoId=None, postId=None):
        res = {}
        if videoId != None:
            url = 'https://api.diyidan.net/v0.2/posts/danmaku?videoId=%s' % (videoId)
            try:
                with urllib.request.urlopen(url) as f:
                    danmu = f.read()
                    res['videoId'] = danmu
            except Exception as e:
                print(e)
        if postId != None:
            url = 'https://api.diyidan.net/v0.2/posts/danmaku?postId=%s' % (postId)
            try:
                with urllib.request.urlopen(url) as f:
                    danmu = f.read()
                    res['postId'] = danmu
            except Exception as e:
                print(e)
        return res

    def download(self, line):
        line_res = []
        line_params = line.strip('\n').split('\t')
        videoId = line_params[0]
        postId = line_params[1]
        res = self._download(videoId=videoId, postId=postId)
        if 'videoId' in res:
            out_filename = ''
            if postId != None:
                out_filename = out_filename + postId
            out_filename = out_filename + '-' + videoId
            out_filename = out_filename + '.' + 'dydjson'
            item_res = {}
            item_res['filename'] = out_filename
            item_res['data'] = res['videoId']
            line_res.append(item_res)
        if 'postId' in res:
            out_filename = postId + '-'
            out_filename = out_filename + '.' + 'dydjson'
            item_res = {}
            item_res['filename'] = out_filename
            item_res['data'] = res['postId']
            line_res.append(item_res)
        return line_res

if __name__ == '__main__':
    pass
else:
    from danmu_utils.common.plugin_collection import add_download_tool
    add_download_tool(DiyidanDownloader().DANMU_TYPE, DiyidanDownloader)