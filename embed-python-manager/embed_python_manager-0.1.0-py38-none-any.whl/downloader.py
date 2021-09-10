import os
import tarfile
from os.path import exists
from time import strftime
from urllib import request
from zipfile import ZipFile

from lk_logger import lk
from lk_utils import loads

from .path_model import assets_model
from .path_model import prj_model


class EmbedPythonDownloader:
    
    def __init__(self, source_filename='www_python_org.yml',
                 dl_dir=assets_model.pyversion):
        self.source = loads(f'{prj_model.source_list}/{source_filename}')
        self.dl_dir = dl_dir
    
    def get_download_link(self, pyversion):
        return self.source[pyversion]
    
    def main(self, pyversion, disable_pth_file=True):
        link = self.get_download_link(pyversion)
        
        filename = link.rsplit("/")[-1]
        file_zip = f'{self.dl_dir}/{filename}'
        
        if not exists(file_zip):
            download(link, file_zip)
        
        if not exists(dir_o := f'{self.dl_dir}/{filename}'):
            extract(file_zip, dir_o)
        
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


def download(link, file):
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
    
    lk.loga('downloading', link)
    # https://blog.csdn.net/weixin_39790282/article/details/90170218
    request.urlretrieve(link, file, _update_progress)
    lk.loga('done')
    
    return file


def extract(file_i, dir_o, type_='zip'):
    if not dir_o:
        dir_o = file_i.removesuffix('.zip')
    if type_ == 'zip':
        file_handle = ZipFile(file_i)
    else:
        file_handle = tarfile.open(file_i)
    file_handle.extractall(dir_o)
    return dir_o
