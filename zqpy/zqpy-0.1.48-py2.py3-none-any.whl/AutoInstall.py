# 以下代码在 python 3.6.1 版本验证通过import sysimport osfrom importlib import import_module
import sys, os
from importlib import import_module
class AutoInstallClass():
    _loaded = set()
    @classmethod
    def find_spec(cls, name, path, target=None):
        if path is None and name not in cls._loaded:
            cls._loaded.add(name)
            print("Installing", name)
            try:
                result = os.system('pip install {}'.format(name))
                if result == 0:
                    return import_module(name)
            except Exception as e:
                print("Failed", e)
                return None
print('引入自动导入库成功')
sys.meta_path.append(AutoInstallClass)