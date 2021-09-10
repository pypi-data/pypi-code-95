import shutil
from os.path import exists

from . import pip_suits
from . import tk_suits
from .downloader import EmbedPythonDownloader
from .path_model import assets_model
from .pyversion import PyVersion


class EmbedPythonManager:
    
    def __init__(self, pyversion: PyVersion):
        self.pyversion = pyversion
        
        assets_model.indexing_dirs(pyversion)
        assets_model.build_dirs()
        self.model = assets_model
        
        self.python = f'{self.model.pyversion}/python.exe'
        self.pythonw = f'{self.model.pyversion}/pythonw.exe'
    
    def copy_to(self, dst_dir):
        shutil.copytree(self.model.pyversion, dst_dir)
    
    def move_to(self, dst_dir):
        shutil.move(self.model.pyversion, dst_dir)
    
    def deploy(self, add_pip_suits=True, add_tk_suits=False):
        dl = EmbedPythonDownloader()
        dl.main(self.pyversion, disable_pth_file=True)
        
        if add_pip_suits:
            pip_suits.download_setuptools(self.pyversion)
            pip_suits.download_pip_src(self.pyversion)
            pip_suits.download_pip(self.pyversion)
            pip_suits.download_urllib3_compatible(self.pyversion)
            
            pip_suits.get_setuptools()
            pip_suits.get_pip_scripts()
            pip_suits.get_pip()
            pip_suits.replace_urllib3()
        
        if add_tk_suits and (
                d := input('Input System {} directory (abspath only): '.format(
                    str(self.pyversion).title()
                ))
        ):
            tk_suits.copy_tkinter(d)
    
    def download(self):
        self.deploy(False, False)
    
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
    def has_pip_script(self):
        return exists(self.model.pip_script)
