import os
import tarfile
from os.path import dirname
from os.path import exists
from time import strftime
from urllib import request
from zipfile import ZipFile

from lk_logger import lk
from lk_utils import loads

from .env import SYSTEM
from .path_model import assets_model
from .path_model import prj_model
from .pyversion import PyVersion


class EmbedPythonDownloader:
    
    def __init__(self, source_filename='www_python_org.yml',
                 dl_dir=assets_model.python_dir):
        self.source = loads(f'{prj_model.source_list}/{source_filename}')
        self.dl_dir = dl_dir
    
    def test_internet_connection(self):
        pass
    
    def change_source(self, source):
        """
        
        Args:
            source: Union[str, dict]
                str: './source_list/*.yml', just give the filename (with
                    suffix), not the full or relative path.
                    examples:
                        'npm_taobao_org.yml'
                        'www_python_org.yml'
                dict: {<system>: {<pyversion>: <link>, ...}, ...}
        """
        if isinstance(source, str):
            source = loads(f'{prj_model.source_list}/{source}')
        self.source = source
    
    def get_download_link(self, pyversion: PyVersion):
        return self.source[SYSTEM][pyversion.v]
    
    def main(self, pyversion: PyVersion, disable_pth_file=True):
        """
        Tree:
            ASSETS_ENTRY
            |= embed_python
                |= windows
                    |- python-3.9.5-embed-amd64.zip  # 1. download zip
                    |= python39  # 2. extracted here (this is `self.dl_dir`)
                        |- ...
                        |- python39._pth  # 3. rename it to 'python39._pth.bak'
        """
        link = self.get_download_link(pyversion)
        
        # filename = link.rsplit("/")[-1]
        file_i = f'{dirname(self.dl_dir)}/{link.rsplit("/")[-1]}'
        dir_o = self.dl_dir
        
        if not exists(file_i):
            download(link, file_i)
        
        if not exists(dir_o):  # note: do not create empty dirs in
            #   `~.path_model.build_dirs` stage.
            extract(file_i, dir_o)
            os.mkdir(f'{dir_o}/dlls')
            os.mkdir(f'{dir_o}/lib')
            os.mkdir(f'{dir_o}/lib/site-packages')
            os.mkdir(f'{dir_o}/scripts')
        
        if disable_pth_file:
            self.disable_pth_file(dir_o, pyversion)
    
    @staticmethod
    def disable_pth_file(dir_, pyversion=None):
        if not pyversion:
            try:
                pth_file = [
                    x for x in os.listdir(dir_)
                    if x.startswith('python') and x.endswith('._pth')
                ][0]
            except IndexError:
                return
        else:
            pth_file = f'{dir_}/{pyversion}._pth'
        if exists(pth_file):
            os.rename(pth_file, pth_file + '.bak')


def download(link, file, exist_ok=True):
    if exists(file):
        if exist_ok:
            return file
        else:
            raise FileExistsError(file)
    
    def _update_progress(block_num, block_size, total_size):
        """

        Args:
            block_num: downloaded data blocks number
            block_size: size of each block
            total_size: total size of remote file in url
        """
        percent = block_size * block_num / total_size * 100
        if percent > 100: percent = 100
        print('\r    {}\t{:.2f}%'.format(
            strftime('%H:%M:%S'), percent), end='')
        #   why put `\r` in the first param?
        #       because it doesn't work in pycharm if we pass it to
        #       `params:end`
        #       ref: https://stackoverflow.com/questions/34950201/pycharm
        #            -print-end-r-statement-not-working
    
    lk.logp(link, file, title='downloading')
    # https://blog.csdn.net/weixin_39790282/article/details/90170218
    request.urlretrieve(link, file, _update_progress)
    print(' --> done')  # this message will be added to the end of progress.
    
    return file


def extract(file_i, dir_o, type_='zip', exist_ok=True):
    if not dir_o:
        dir_o = file_i.removesuffix('.zip')
    if exists(dir_o):
        if os.listdir(dir_o):
            if exist_ok:
                return dir_o
            else:
                raise FileExistsError(dir_o)
        else:
            os.remove(dir_o)
    
    if type_ == 'zip':
        file_handle = ZipFile(file_i)
    else:
        file_handle = tarfile.open(file_i)
    file_handle.extractall(dir_o)
    return dir_o
