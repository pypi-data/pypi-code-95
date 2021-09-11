import urllib.request
import zlib
from xml.dom import minidom


from danmu_utils.common.IDownloader import IDownloader


class IqiyiDownloader(IDownloader):
    @property
    def DANMU_TYPE(self):
        return 'iqiyi'

    @property
    def DANMU_EXTNAME(self):
        return 'iqyxml'

    @property
    def DANMU_LIST_EXTNAME(self):
        return 'iqylist'

    def _download(self, videoId):
        url_template = 'https://cmts.iqiyi.com/bullet/%s/%s/%s_300_%s.z' % (videoId[-4: -2], videoId[-2: ], videoId, '%s')
        page = 0
        root = None
        while(True):
            page += 1
            url = url_template % page
            print('Start download: "%s".' % url)
            try:
                with urllib.request.urlopen(url) as f:
                    body = f.read()
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    break
                else:
                    print(e)
                    break
            except Exception as e:
                if isinstance(e, urllib.error.HTTPError) and e.code == 404:
                    print('Download finished.')
                else:
                    print(e)
                break
            text = zlib.decompress(body)
            cur_root = minidom.parseString(text.decode('utf-8'))
            if root == None:
                root = cur_root
                continue
            try:
                data_tag = root.getElementsByTagName('danmu')[0].getElementsByTagName('data')[0]
                cur_data_tag = cur_root.getElementsByTagName('danmu')[0].getElementsByTagName('data')[0]
                data_tag.childNodes.extend(cur_data_tag.childNodes)
            except Exception as e:
                print(e)
                break

        return root.toxml().encode('utf-8')

    def download(self, line):
        line_res = []
        line_params = line.strip('\n').split('\t')
        tvId = line_params[0]
        res = self._download(tvId)
        item_res = {}
        item_res['filename'] = tvId + '.' + self.DANMU_EXTNAME
        item_res['data'] = res
        line_res.append(item_res)
        return line_res


if __name__ == '__main__':
    pass
else:
    from danmu_utils.common.plugin_collection import add_download_tool
    add_download_tool(IqiyiDownloader().DANMU_TYPE, IqiyiDownloader)