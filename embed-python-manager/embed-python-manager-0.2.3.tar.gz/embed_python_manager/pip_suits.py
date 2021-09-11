"""
If you want only pip package installed, run `get_pip` and it is fast to
generate.
If you need '~/scripts/pip.exe' etc., run `get_pip_scripts`. Note that `get_pip_
scripts` can only generate pip scripts, no package being installed; you may
need also to run `get_pip` after that.

References:
    ~/docs/depsland-venv-setup.md
    
FIXME:
    All static links in this script should be replaced with source-selectable
    links.
"""
import os
import shutil
from os.path import dirname
from os.path import exists

from lk_logger import lk
from lk_utils import find_dirs
from lk_utils import find_files
from lk_utils import run_cmd_shell

from .downloader import download
from .downloader import extract
from .path_model import assets_model
from .pyversion import PyVersion

""" Notice of Extracting whl/tar Files

Example:
    ~/assets/pip_suits/python3
    |
    |
    |- pip-21.2.4-py3-none-any.whl  # 1.1. download whl file
    |= pip  # 1.2. extract whl file (notice there're two dirs)
        |= pip
        |= pip-21.2.4.dist-info
    |
    |
    |- pip-21.2.4.tar.gz  # 2.1. download tar file
    |= pip_src  # 2.2. extract tar file
        |= pip-21.2.4  # 2.3. we will rename it to 'pip'. see `download_pip_src`
            |- setup.py
            |- ...
        |- @PaxHeader
    |
    |
    |- setuptools-58.0.4-py3-none-any.whl  # 3.1
    |= setuptools  # 3.2 (notice there're four dirs and one file)
        |= _distutils_hack
        |= pkg_resources
        |= setuptools
        |= setuptools-58.0.4.dist-info
        |- distutils-precedence.pth
    |
    |
    |- urllib3-1.25.9-py2.py3-none-any.whl  # 4.1
    |= urllib3  # 4.2
        |= urllib3
        |= urllib3-1.25.9.dist-info
"""


def download_setuptools(pyversion: PyVersion):
    """ Download and extract setuptools.
    """
    if pyversion.major == 2:
        name = 'setuptools-45.0.0-py2.py3-none-any.whl'
        link = 'https://pypi.tuna.tsinghua.edu.cn/packages/af/e7/02db816dc88c' \
               '598281bacebbb7ccf2c9f1a6164942e88f1a0fded8643659/setuptools-4' \
               '5.0.0-py2.py3-none-any.whl'
    elif pyversion.major == 3:
        name = 'setuptools-58.0.4-py3-none-any.whl'  # 2021-09-09
        link = 'https://pypi.tuna.tsinghua.edu.cn/packages/c4/c1/aed7dfedb18e' \
               'a73d7713bf6ca034ab001a6425be49ffa7e79bbd5999f677/setuptools-5' \
               '8.0.4-py3-none-any.whl'
    else:
        raise Exception(pyversion)
    
    file = download(
        link, dirname(assets_model.setuptools_in_pip_suits) + '/' + name)
    dir_ = extract(file, assets_model.setuptools_in_pip_suits)
    return f'{dir_}/setuptools'


def download_pip_src(pyversion: PyVersion):
    if pyversion.major == 2:
        name = 'pip-20.3.4.tar.gz'
        link = 'https://pypi.tuna.tsinghua.edu.cn/packages/53/7f/55721ad0501a' \
               '9076dbc354cc8c63ffc2d6f1ef360f49ad0fbcce19d68538/pip-20.3.4.t' \
               'ar.gz'
    elif pyversion.major == 3:
        name = 'pip-21.2.4.tar.gz'  # 2021-09-09
        link = 'https://pypi.tuna.tsinghua.edu.cn/packages/52/e1/06c018197d81' \
               '51383f66ebf6979d951995cf495629fc54149491f5d157d0/pip-21.2.4.t' \
               'ar.gz'
    else:
        raise Exception(pyversion)
    
    file = download(
        link, dirname(assets_model.pip_src_in_pip_suits) + '/' + name)
    dir_ = extract(file, assets_model.pip_src_in_pip_suits, type_='tar')
    os.rename(f'{dir_}/{name.replace(".tar.gz", "")}', f'{dir_}/pip')
    return f'{dir_}/pip'


def download_pip(pyversion: PyVersion):
    if pyversion.major == 2:
        name = 'pip-20.3.4-py2.py3-none-any.whl'
        link = 'https://pypi.tuna.tsinghua.edu.cn/packages/27/79/8a850fe34964' \
               '46ff0d584327ae44e7500daf6764ca1a382d2d02789accf7/pip-20.3.4-p' \
               'y2.py3-none-any.whl'
    elif pyversion.major == 3:
        name = 'pip-21.2.4-py3-none-any.whl'  # 2021-09-09
        link = 'https://pypi.tuna.tsinghua.edu.cn/packages/ca/31/b88ef447d595' \
               '963c01060998cb329251648acf4a067721b0452c45527eb8/pip-21.2.4-p' \
               'y3-none-any.whl'
    else:
        raise Exception(pyversion)
    
    file = download(
        link, dirname(assets_model.pip_in_pip_suits) + '/' + name)
    dir_ = extract(file, assets_model.pip_in_pip_suits)
    return f'{dir_}/pip'


def download_urllib3_compatible(pyversion: PyVersion):
    """
    References:
        https://blog.csdn.net/shizheng_Li/article/details/115838420
    """
    if pyversion.major == 2:
        lk.logt('[I3412]', 'no need to download urllib3 compatible version')
        return
    
    name = 'urllib3-1.25.9-py2.py3-none-any.whl'
    link = 'https://pypi.tuna.tsinghua.edu.cn/packages/e1/e5/df302e8017440f11' \
           '1c11cc41a6b432838672f5a70aa29227bf58149dc72f/urllib3-1.25.9-py2.p' \
           'y3-none-any.whl'
    file = download(
        link, dirname(assets_model.urllib3_in_pip_suits) + '/' + name)
    dir_ = extract(file, assets_model.urllib3_in_pip_suits)
    return f'{dir_}/urllib3'


# ------------------------------------------------------------------------------

def get_setuptools():
    return _copy_resources(
        assets_model.setuptools_in_pip_suits,
        assets_model.site_packages,
    )


def get_pip_scripts():
    run_cmd_shell('cd "{pip_src_dir}" & "{python}" setup.py install'.format(
        pip_src_dir=assets_model.pip_src_in_pip_suits + '/' + 'pip',
        python=assets_model.python,
    ).replace('/', '\\'))
    
    assert exists(assets_model.pip_script)
    
    # find and remove pip egg dir in site-packages
    for dp, dn in find_dirs(assets_model.site_packages, fmt='zip'):
        if dn.startswith('pip-') and dn.endswith('.egg'):
            shutil.rmtree(dp)
            break
    
    return assets_model.pip_script


def get_pip():
    return _copy_resources(
        assets_model.pip_in_pip_suits,
        assets_model.site_packages,
    )


def replace_urllib3():
    os.rename(
        assets_model.urllib3,
        assets_model.urllib3 + '_bak'
    )
    return _copy_resources(
        assets_model.urllib3_in_pip_suits,
        assets_model.pip_vendor,
        exclusions=('urllib3-1.25.11.dist-info',)
    )


def _copy_resources(parent_dir_i, parent_dir_o, exclusions=()):
    out = []
    
    for dp, dn in find_dirs(parent_dir_i, fmt='zip'):
        if dn in exclusions:
            continue
        dp_i, dp_o = dp, f'{parent_dir_o}/{dn}'
        shutil.copytree(dp_i, dp_o)
        out.append(dp_o)
    
    for fp, fn in find_files(parent_dir_i, fmt='zip'):
        if fn in exclusions:
            continue
        fp_i, fp_o = fp, f'{parent_dir_o}/{fn}'
        shutil.copyfile(fp_i, fp_o)
        out.append(fp_o)
    
    return out
