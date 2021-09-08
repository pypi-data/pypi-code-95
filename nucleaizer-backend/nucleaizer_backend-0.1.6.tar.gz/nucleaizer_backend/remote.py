import json
import urllib.request
import pprint
from collections import defaultdict
from pathlib import Path

from tqdm import tqdm

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        print(b, bsize, tsize)
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def get_model_list(repository = 'etasnadi/Mask_RCNN'):
    github_api_URL = 'https://api.github.com/repos/%s/releases' % repository
    
    pp = pprint.PrettyPrinter(indent=4)
    
    all_assets = []

    with urllib.request.urlopen(github_api_URL) as response:
        html = response.read()
        releases = json.loads(html)
        for r in releases:
            for ass in r['assets']:
                ass_name = Path(ass['name'])
                ass_URL = ass['browser_download_url']
                all_assets.append((ass_name, ass_URL))
    
    
    models = [Path(m[0]).stem for m in all_assets if m[0].name.endswith('.h5')]

    model_assets = defaultdict(list)

    for asset_name, asset_URL in all_assets:
        for m in models: 
            if asset_name.name.startswith(m):
                model_assets[m].append((asset_URL, asset_name.name))

    return model_assets

def download_model(model_name, target_path, progress_bar):
    l = get_model_list()
    files = l[model_name]
    print('Files to download:', files)
    for file_URL, file_name in files:
        download_file(file_URL, target_path/file_name, progress_bar)


def download_file(url, output_path, progress_bar):
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        
        def update_progress(chunk_num, chunk_size, total_size):
            received = min(chunk_num*chunk_size, total_size)
            progress = int((received/total_size)*100)
            progress_bar.setValue(progress)

        urllib.request.urlretrieve(url, filename=output_path, reporthook=update_progress)