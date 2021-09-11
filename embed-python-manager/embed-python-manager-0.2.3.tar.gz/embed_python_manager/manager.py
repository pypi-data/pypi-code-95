import shutil
from os.path import exists
from typing import Union

from . import pip_suits
from . import tk_suits
from .downloader import EmbedPythonDownloader
from .path_model import assets_model
from .pyversion import PyVersion


class EmbedPythonManager:
    
    def __init__(self, pyversion: Union[str, PyVersion]):
        if isinstance(pyversion, str):
            self.pyversion = PyVersion(pyversion)
        else:
            self.pyversion = pyversion
            
        assets_model.indexing_dirs(self.pyversion)
        assets_model.build_dirs()
        self.model = assets_model

        self._downloader = EmbedPythonDownloader(dl_dir=self.model.python_dir)

        self.python = f'{self.model.python_dir}/python.exe'
        self.pythonw = f'{self.model.python_dir}/pythonw.exe'
    
    def deploy(self, add_pip_suits=True, add_pip_scripts=True,
               add_tk_suits=False):
        self._downloader.main(self.pyversion, disable_pth_file=True)
        
        if add_pip_suits:
            if not self.has_setuptools:
                pip_suits.download_setuptools(self.pyversion)
                pip_suits.get_setuptools()
            
            if add_pip_scripts and not self.has_pip_scripts:
                pip_suits.download_pip_src(self.pyversion)
                pip_suits.get_pip_scripts()
                
            if not self.has_pip:
                pip_suits.download_pip(self.pyversion)
                pip_suits.get_pip()
            
                pip_suits.download_urllib3_compatible(self.pyversion)
                pip_suits.replace_urllib3()
        
        if add_tk_suits and (
                d := input('Input System {} directory (abspath only): '.format(
                    str(self.pyversion).title()
                ))
        ):
            tk_suits.copy_tkinter(d)
    
    def download(self):
        self.deploy(False, False)

    def copy_to(self, dst_dir):
        shutil.copytree(self.model.python_dir, dst_dir)

    def move_to(self, dst_dir):
        shutil.move(self.model.python_dir, dst_dir)

    def change_source(self, source):
        self._downloader.change_source(source)
    
    # --------------------------------------------------------------------------
    # status
    
    @property
    def is_pth_disabled(self):
        return not exists(self.model.python_pth)
    
    @property
    def has_pip(self):
        return exists(self.model.pip)
    
    @property
    def has_setuptools(self):
        return exists(self.model.setuptools)
    
    @property
    def has_pip_scripts(self):
        return exists(self.model.pip_script)
