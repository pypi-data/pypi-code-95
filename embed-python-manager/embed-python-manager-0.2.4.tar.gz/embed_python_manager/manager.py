import shutil
from os import listdir
from os import remove
from os.path import dirname
from os.path import exists
from typing import Union

from lk_logger import lk

from . import pip_suits
from . import tk_suits
from .downloader import EmbedPythonDownloader
from .path_model import assets_model
from .pyversion import PyVersion


class EmbedPythonManager:
    
    def __init__(self, pyversion: Union[str, PyVersion], system_python=''):
        if isinstance(pyversion, str):
            self.pyversion = PyVersion(pyversion)
        else:
            self.pyversion = pyversion
            
        assets_model.indexing_dirs(self.pyversion)
        assets_model.build_dirs()
        self.model = assets_model

        self._downloader = EmbedPythonDownloader(dl_dir=self.model.python_dir)

        self.system_python = system_python
        self.python = f'{self.model.python_dir}/python.exe'
        self.pythonw = f'{self.model.python_dir}/pythonw.exe'
    
    def deploy(self, add_pip_suits=True, add_pip_scripts=True,
               add_tk_suits=False):
        lk.logt('[I0921]', 'depoly local embed python',
                '(internet connection maybe required)')

        lk.loga('download and extract embed_python')
        d = self._downloader.main(self.pyversion, disable_pth_file=True)
        
        if add_pip_suits:
            if not self.has_setuptools:
                lk.loga('download and extract setuptools')
                pip_suits.download_setuptools(self.pyversion)
                pip_suits.get_setuptools()
            
            if add_pip_scripts and not self.has_pip_scripts:
                lk.loga('download and extract pip (tarfile)')
                pip_suits.download_pip_src(self.pyversion)
                pip_suits.get_pip_scripts()
                
            if not self.has_pip:
                lk.loga('download and extract pip (whlfile)')
                pip_suits.download_pip(self.pyversion)
                pip_suits.get_pip()

                lk.loga('replace ~/pip/_venvdor/urllib3 with a lower version')
                pip_suits.download_urllib3_compatible(self.pyversion)
                pip_suits.replace_urllib3()
        
        if add_tk_suits:
            if not self.has_tkinter:
                if self.system_python:
                    dir_i = dirname(self.system_python)
                else:
                    from textwrap import dedent
                    lk.logt('[I1500]', dedent('''
                        tkinter suits are not found. you need to install a
                        regular python ({}) in your computer and pass its
                        dirpath below.
                    '''.format(self.pyversion)).strip())
                    dir_i = input('Input System {} directory (abspath): '.format(
                        str(self.pyversion).title()
                    ))
                dir_o = self.model.tk_suits_py3
                lk.loga('copying files from "{}" to "{}"'.format(dir_i, dir_o))
                tk_suits.copy_tkinter(dir_i, dir_o)
            if not self.has_tkinter_installed_in_python_dir:
                from .pip_suits import copy_resources
                dir_i = self.model.tk_suits_py3
                dir_o = self.model.python_dir
                lk.loga('copying files from "{}" to "{}"'.format(dir_i, dir_o))
                copy_resources(dir_i, dir_o)
    
    def download(self):
        self.deploy(False, False)

    def copy_to(self, dst_dir):
        shutil.copytree(self.model.python_dir, dst_dir)

    def move_to(self, dst_dir):
        # warning: if dst_dir exists, `shutil.move(src_dir, dst_dir)` will
        # create a subdir in dst_dir; if not exists, will create dir_dir and
        # move. we prevent this behavior and make sure there's only case#2
        # happend.
        if exists(dst_dir):
            if listdir(dst_dir):
                raise FileExistsError(dst_dir)
            else:
                remove(dst_dir)
        shutil.move(self.model.python_dir, dst_dir)

    def change_source(self, source):
        self._downloader.change_source(source)
    
    # --------------------------------------------------------------------------
    # status
    
    @property
    def is_pth_disabled(self):
        return not exists(self.model.python_pth)
    
    @property
    def has_setuptools(self):
        return exists(self.model.setuptools)
    
    @property
    def has_pip(self):
        return exists(self.model.pip)
    
    @property
    def has_pip_scripts(self):
        return exists(self.model.pip_script)

    @property
    def has_tkinter(self):
        return listdir(self.model.tk_suits_py3)  # FIXME
    
    @property
    def has_tkinter_installed_in_python_dir(self):
        return exists(f'{self.model.python_dir}/tkinter')
