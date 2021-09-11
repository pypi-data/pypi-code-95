import urllib.request
import json


from danmu_utils.common.IDownloader import IDownloader


class MgtvDownloader(IDownloader):
    @property
    def DANMU_TYPE(self):
        return 'mgtv'

    @property
    def DANMU_EXTNAME(self):
        return 'mgtvjson'

    @property
    def DANMU_LIST_EXTNAME(self):
        return 'mgtvlist'

    def _download(self, cid, vid):
        url_template = 'https://galaxy.bz.mgtv.com/rdbarrage?vid=%s&cid=%s&time=%s' % (vid, cid, '%s')
        time = 0
        root = None
        while(True):
            url = url_template % time
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
            text = body
            cur_root = json.loads(text)
            if root == None:
                root = cur_root
                continue
            try:
                data_items = root['data']['items']
                cur_data_items = cur_root['data']['items']
                if cur_data_items is None:
                    break
                data_items.extend(cur_data_items)
                root['data']['next'] = cur_root['data']['next']
                time = cur_root['data']['next']
            except Exception as e:
                print(e)
                break

        return json.dumps(root, ensure_ascii=False).encode(encoding='utf-8')

    def download(self, line):
        line_res = []
        line_params = line.strip('\n').split('\t')
        cid = line_params[0]
        vid = line_params[1]
        res = self._download(cid=cid, vid=vid)
        item_res = {}
        item_res['filename'] = cid + '-' + vid + '.' + self.DANMU_EXTNAME
        item_res['data'] = res
        line_res.append(item_res)
        return line_res


if __name__ == '__main__':
    pass
else:
    from danmu_utils.common.plugin_collection import add_download_tool
    add_download_tool(MgtvDownloader().DANMU_TYPE, MgtvDownloader)