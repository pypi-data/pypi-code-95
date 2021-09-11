from os import mkdir
from os.path import dirname
from os.path import exists

from .env import ASSETS_ENTRY
from .env import SYSTEM
from .pyversion import PyVersion


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
        self.pyversion = pyversion
        
        self.python_dir = f'{self.system}/{pyversion}'
        self.python = f'{self.python_dir}/python.exe'
        self.python_pth = f'{self.python_dir}/{pyversion.v_prefix}._pth'
        
        self.dlls = f'{self.python_dir}/dlls'
        self.scripts = f'{self.python_dir}/scripts'
        self.lib = f'{self.python_dir}/lib'
        self.site_packages = f'{self.lib}/site-packages'
        
        self.setuptools = f'{self.site_packages}/setuptools'
        self.pip = f'{self.site_packages}/pip'
        self.pip_vendor = f'{self.pip}/_vendor'
        self.urllib3 = f'{self.pip}/_vendor/urllib3'
        self.pip_egg = f'{self.site_packages}/'
        self.pip_script = f'{self.scripts}/pip.exe'
        
        current_pip_suits = f'{self.pip_suits}/python{pyversion.major}'
        self.setuptools_in_pip_suits = f'{current_pip_suits}/setuptools'
        self.pip_src_in_pip_suits = f'{current_pip_suits}/pip_src'
        self.pip_in_pip_suits = f'{current_pip_suits}/pip'
        self.urllib3_in_pip_suits = f'{current_pip_suits}/urllib3'
    
    def build_dirs(self):
        if not exists(self.assets):
            mkdir(self.assets)
            
            mkdir(self.embed_python)
            mkdir(self.system)
            
            mkdir(self.pip_suits)
            mkdir(self.pip_suits_py2)
            mkdir(self.pip_suits_py3)
            
            mkdir(self.tk_suits)
            mkdir(self.tk_suits_py2)
            mkdir(self.tk_suits_py3)
        
        # if not exists(self.python_dir):
        #     mkdir(self.python_dir)
        #
        #     mkdir(self.dlls)
        #     mkdir(self.scripts)
        #     mkdir(self.lib)
        #
        #     mkdir(self.site_packages)


prj_model = ProjectPathModel()
assets_model = AssetsPathModel(PyVersion('python39'))
