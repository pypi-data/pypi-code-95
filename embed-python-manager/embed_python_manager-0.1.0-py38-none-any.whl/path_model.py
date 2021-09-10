from os import mkdir
from os.path import dirname
from os.path import exists

from .pyversion import PyVersion
from .env import ASSETS_ENTRY
from .env import SYSTEM


class ProjectPathModel:
    cur_dir = dirname(__file__)
    prj_dir = dirname(cur_dir)
    source_list = f'{cur_dir}/source_list'


class AssetsPathModel:
    
    def __init__(self, pyversion):
        self.assets = f'{ASSETS_ENTRY}/assets'
        
        self.embed_python = f'{self.assets}/embed_python'
        self.pip_suits = f'{self.assets}/pip_suits'
        self.tk_suits = f'{self.assets}/tk_suits'
        
        self.pip_suits_py2 = f'{self.pip_suits}/python2'
        self.pip_suits_py3 = f'{self.pip_suits}/python3'
        self.tk_suits_py2 = f'{self.tk_suits}/python2'
        self.tk_suits_py3 = f'{self.tk_suits}/python3'
        
        self.system = f'{self.embed_python}/{SYSTEM}'
        
        self.indexing_dirs(pyversion)
    
    # noinspection PyAttributeOutsideInit
    def indexing_dirs(self, pyversion):
        self.pyversion = f'{self.system}/{pyversion}'
        self.python = f'{self.pyversion}/python.exe'
        self.python_pth = f'{self.pyversion}/{pyversion.v0}._pth'
        
        self.scripts = f'{self.pyversion}/scripts'
        self.lib = f'{self.pyversion}/lib'
        self.site_packages = f'{self.lib}/site-packages'
        
        self.setuptools = f'{self.site_packages}/setuptools'
        self.pip = f'{self.site_packages}/pip'
        self.urllib3 = f'{self.pip}/_vendor/urllib3'
        self.pip_egg = f'{self.site_packages}/'
        self.pip_script = f'{self.scripts}/pip.exe'
        
        current_pip_suits = f'{self.pip_suits}/{pyversion.v0[:-1]}'
        self.setuptools_in_pip_suits = f'{current_pip_suits}/setuptools'
        self.pip_src_in_pip_suits = f'{current_pip_suits}/pip_src'
        self.pip_in_pip_suits = f'{current_pip_suits}/pip'
        self.urllib3_in_pip_suits = f'{current_pip_suits}/urllib3'
        
    def build_dirs(self):
        for d in (
                self.assets,
                self.embed_python,
                self.pip_suits,
                self.tk_suits,
                self.pip_suits_py2,
                self.pip_suits_py3,
                self.tk_suits_py2,
                self.tk_suits_py3,
                self.system,
                self.pyversion,
        ):
            if exists(d):
                mkdir(d)


prj_model = ProjectPathModel()
assets_model = AssetsPathModel(PyVersion('python39'))
