import urllib.request
import json


from danmu_utils.common.IDownloader import IDownloader


class WetvDownloader(IDownloader):
    @property
    def DANMU_TYPE(self):
        return 'wetv'

    @property
    def DANMU_EXTNAME(self):
        return 'wetvjson'

    @property
    def DANMU_LIST_EXTNAME(self):
        return 'wetvlist'

    def _download(self, vid, targetid):
        url_template = 'https://access.wetv.vip/overseas/DMCommentListRequest?vplatform=2&vappid=92089330&vsecret=cd21b1cef4d2ac7d600e5d3e4f1b1fb612a31b4c6ccf5c8d&raw=1&lang_code=1491963&country_code=153505'
        post_body_template = '''{
  "strDanmuKey": "type=2&id=%s&targetid=%s&vid=%s",
  "dwStartTime": %s
}''' % (vid, targetid, vid, '%s')
        headers = {'Referer': 'https://wetv.vip', 'Content-Type': 'text/plain'}
        time = 0
        time_max = 60 * 60
        root = None
        while(True):
            if time > time_max:
                break
            url = url_template
            post_body = post_body_template % (time)
            print('Start download: "%s".' % url)
            req = urllib.request.Request(url=url, data=post_body.encode('utf-8'), headers=headers, method='POST')
            try:
                with urllib.request.urlopen(req) as f:
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
                data_items = root['data']['commentList']
                cur_data_items = cur_root['data']['commentList']
                if cur_data_items is None:
                    break
                data_items.extend(cur_data_items)
                root['data']['dwNextTimeDur'] = cur_root['data']['dwNextTimeDur']
                time = time + cur_root['data']['dwNextTimeDur']
            except Exception as e:
                print(e)
                break

        return json.dumps(root, ensure_ascii=False).encode(encoding='utf-8')

    def download(self, line):
        line_res = []
        line_params = line.strip('\n').split('\t')
        vid = line_params[0]
        targetid = line_params[1]
        res = self._download(vid=vid, targetid=targetid)
        item_res = {}
        item_res['filename'] = vid + '-' + targetid + '.' + self.DANMU_EXTNAME
        item_res['data'] = res
        line_res.append(item_res)
        return line_res


if __name__ == '__main__':
    pass
else:
    from danmu_utils.common.plugin_collection import add_download_tool
    add_download_tool(WetvDownloader().DANMU_TYPE, WetvDownloader)