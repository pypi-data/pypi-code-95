import julia
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

import appdirs


APPNAME = 'InterpretableAI'
NEEDS_RESTART = False


def iswindows():
    return (appdirs.system.startswith('win32') or
            appdirs.system.startswith('cygwin'))


def isapple():
    return appdirs.system.startswith('darwin')


def islinux():
    return appdirs.system.startswith('linux')


def julia_exename():
    return 'julia.exe' if iswindows() else 'julia'


def julia_default_depot():
    if iswindows():
        key = 'USERPROFILE'
    else:
        key = 'HOME'

    return os.path.join(os.environ[key], '.julia')


def get_prefs_dir():
    depot = os.environ.get('JULIA_DEPOT_PATH', julia_default_depot())
    prefs = os.path.join(depot, 'prefs')
    pathlib.Path(prefs).mkdir(parents=True, exist_ok=True)
    return prefs


# Configure julia with options specified in environment variables
def iai_run_julia_setup(**kwargs):
    if NEEDS_RESTART:
        raise Exception(
            'Need to restart Python after installing the IAI system image')

    # Check if system image replacement was queued on Windows
    replace_sysimg_file = sysimage_replace_prefs_file()
    if os.path.isfile(replace_sysimg_file):
        with open(replace_sysimg_file) as f:
            lines = f.read().splitlines()
        sysimage_do_replace(*lines)
        os.remove(replace_sysimg_file)

    if 'IAI_DISABLE_COMPILED_MODULES' in os.environ:  # pragma: no cover
        kwargs['compiled_modules'] = False

    if 'IAI_JULIA' in os.environ:  # pragma: no cover
        kwargs['runtime'] = os.environ['IAI_JULIA']
    else:
        julia_path = julia_load_install_path()
        if julia_path:
            kwargs['runtime'] = os.path.join(julia_path, 'bin',
                                             julia_exename())

    if 'IAI_SYSTEM_IMAGE' in os.environ:  # pragma: no cover
        kwargs['sysimage'] = os.environ['IAI_SYSTEM_IMAGE']
    else:
        sysimage_path = sysimage_load_install_path()
        if sysimage_path:
            kwargs['sysimage'] = sysimage_path

    # Add Julia bindir to path on Windows so that DLLs can be found
    if 'runtime' in kwargs and os.name == 'nt':
        bindir = os.path.dirname(kwargs['runtime'])
        os.environ['PATH'] += os.pathsep + bindir

    # Load Julia with IAI_DISABLE_INIT to avoid interfering with stdout
    os.environ['IAI_DISABLE_INIT'] = 'True'

    # Start julia once in case artifacts need to be downloaded
    # Skip if julia is already inited, as we may not know `runtime`
    if not julia.libjulia.get_libjulia():
        args = [kwargs.get('runtime', julia_exename())]
        if 'sysimage' in kwargs:
            args.extend(['-J', kwargs['sysimage']])
        args.extend(['-e', 'nothing'])
        subprocess.run(args, stdout=subprocess.DEVNULL)

    # Do custom Julia init if required
    if len(kwargs) > 0:
        julia.Julia(**kwargs)

    from julia import Main as _Main

    del os.environ['IAI_DISABLE_INIT']

    return _Main


def install(runtime=os.environ.get("IAI_JULIA", "julia"), **kwargs):
    """Install Julia packages required for `interpretableai.iai`.

    This function must be called once after the package is installed to
    configure the connection between Python and Julia.

    Parameters
    ----------
    Refer to the
    `installation instructions <https://docs.interpretable.ai/v2.2.0/IAI-Python/data/#Python-Installation-1>`
    for information on any additional parameters that may be required.

    Examples
    --------
    >>> install(**kwargs)
    """
    import julia
    os.environ['IAI_DISABLE_INIT'] = 'True'
    julia.install(julia=runtime, **kwargs)
    del os.environ['IAI_DISABLE_INIT']


# JULIA


def julia_default_install_dir():
    return os.path.join(appdirs.user_data_dir(APPNAME), 'julia')


def julia_latest_version():
    url = 'https://raw.githubusercontent.com/JuliaBinaryWrappers/Julia_jll.jl/master/Project.toml'
    toml = urllib.request.urlopen(url).read().decode('utf-8')
    match = re.search('version = "(.*)\\+(.*?)"', toml)
    captures = list(match.groups())
    captures[0] = 'v{0}'.format(captures[0])
    return captures


def julia_tgz_url(version, build):
    arch = 'x86_64'
    if islinux():
        os_code = 'linux-gnu'
    elif isapple():
        os_code = 'apple-darwin14'
    elif iswindows():
        os_code = 'w64-mingw32'
    else:  # pragma: no cover
        raise Exception(
            'Unsupported operating system: {0}'.format(appdirs.system))

    url = "https://github.com/JuliaBinaryWrappers/Julia_jll.jl/releases/download/Julia-{0}+{1}/Julia.{0}.{2}-{3}-libgfortran4-cxx11.tar.gz".format(version, build, arch, os_code)

    return url


def julia_path_prefs_file():
    return os.path.join(get_prefs_dir(), 'IAI-pyjulia')


def julia_save_install_path(path):
    with open(julia_path_prefs_file(), 'w') as f:
        f.write(path)


def julia_load_install_path():
    path = julia_path_prefs_file()
    if os.path.isfile(path):
        with open(path) as f:
            julia_path = f.read()
        if isinstance(julia_path, bytes):  # pragma: no cover
            julia_path = julia_path.decode('utf-8')
        return julia_path
    else:
        return None


def install_julia(prefix=julia_default_install_dir()):
    """Download and install Julia automatically.

    Parameters
    ----------
    prefix : string, optional
        The directory where Julia will be installed. Defaults to a location
        determined by
        `appdirs.user_data_dir <https://pypi.org/project/appdirs/>`.

    Examples
    --------
    >>> install_julia(**kwargs)
    """
    version, build = julia_latest_version()
    url = julia_tgz_url(version, build)

    print('Downloading {0}'.format(url), file=sys.stderr)
    filename, _ = urllib.request.urlretrieve(url)

    dest = os.path.join(prefix, version)
    if os.path.exists(dest):  # pragma: no cover
        shutil.rmtree(dest)

    with tarfile.open(filename) as f:
        f.extractall(dest)

    julia_save_install_path(dest)

    install(runtime=os.path.join(dest, 'bin', julia_exename()))

    print('Installed Julia to {0}'.format(dest), file=sys.stderr)
    return True


# IAI SYSTEM IMAGE


def sysimage_default_install_dir():
    return os.path.join(appdirs.user_data_dir(APPNAME), 'sysimage')


def get_latest_iai_version():
    url = 'https://docs.interpretable.ai/stable_version.txt'
    return urllib.request.urlopen(url).read().decode('utf-8')


def iai_download_url(julia_version, iai_version):
    if isapple():
        os_code = 'macos'
    elif iswindows():
        os_code = 'win64'
    elif islinux():
        os_code = 'linux'
    else:  # pragma: no cover
        raise Exception(
            'Unsupported operating system: {0}'.format(appdirs.system))

    if iai_version.startswith('v'):
        iai_version = iai_version[1:]

    if iai_version == 'dev':
        url = 'https://iai-system-images.s3.amazonaws.com/{0}/julia{1}/master/latest.zip'.format(os_code, julia_version)
    else:
        url = 'https://iai-system-images.s3.amazonaws.com/{0}/julia{1}/v{2}/sys-{0}-julia{1}-iai{2}.zip'.format(os_code, julia_version, iai_version)

    return url


# Saving location of system image

def sysimage_path_prefs_file():
    return os.path.join(get_prefs_dir(), 'IAI')


def sysimage_save_install_path(path):
    with open(sysimage_path_prefs_file(), 'w') as f:
        f.write(path)


def sysimage_load_install_path():
    path = sysimage_path_prefs_file()
    if os.path.isfile(path):
        with open(path) as f:
            sysimage_path = f.read()
        if isinstance(sysimage_path, bytes):  # pragma: no cover
            sysimage_path = sysimage_path.decode('utf-8')
        return sysimage_path
    else:
        return None


# Saving replacement command

def sysimage_replace_prefs_file():
    return os.path.join(get_prefs_dir(), 'IAI-replacedefault')


def sysimage_save_replace_command(image_path, target_path):
    with open(sysimage_replace_prefs_file(), 'w') as f:
        print(image_path, file=f)
        print(target_path, file=f)


def sysimage_do_replace(image_path, target_path):
    print('Replacing default system image at {0} with IAI system image'.format(target_path), file=sys.stderr)
    os.chmod(target_path, 0o777)
    os.remove(target_path)
    shutil.copyfile(image_path, target_path)


# Top-level system image installation

def install_system_image(version='latest', replace_default=False,
                         prefix=sysimage_default_install_dir()):
    """Download and install the IAI system image automatically.

    Parameters
    ----------
    version : string, optional
        The version of the IAI system image to install (e.g. `'2.1.0'`).
        Defaults to `'latest'`, which will install the most recent release.
    replace_default : bool
        Whether to replace the default Julia system image with the downloaded
        IAI system image. Defaults to `False`.
    prefix : string, optional
        The directory where Julia will be installed. Defaults to a location
        determined by
        `appdirs.user_data_dir <https://pypi.org/project/appdirs/>`.

    Examples
    --------
    >>> install_system_image(**kwargs)
    """
    if version == 'latest':
        version = get_latest_iai_version()

    Main = iai_run_julia_setup()

    julia_version = Main.string(Main.VERSION)

    url = iai_download_url(julia_version, version)

    print('Downloading {0}'.format(url), file=sys.stderr)
    filename, _ = urllib.request.urlretrieve(url)

    if version != 'dev':
        version = 'v{0}'.format(version)
    dest = os.path.join(prefix, version)
    if os.path.exists(dest):  # pragma: no cover
        shutil.rmtree(dest)

    with zipfile.ZipFile(filename) as f:
        f.extractall(dest)

    if islinux():
        image_name = 'sys.so'
    elif isapple():
        image_name = 'sys.dylib'
    elif iswindows():
        image_name = 'sys.dll'
    else:  # pragma: no cover
        raise Exception(
            'Unsupported operating system: {0}'.format(appdirs.system))
    image_path = os.path.join(dest, image_name)

    sysimage_save_install_path(image_path)
    print('Installed IAI system image to {0}'.format(dest), file=sys.stderr)

    if replace_default:
        target_path = os.path.join(
            Main.eval('unsafe_string(Base.JLOptions().julia_bindir)'),
            '..', 'lib', 'julia', image_name,
        )
        # Windows can't replace the current sysimg as it is loaded into this
        # session so we save a command to run later
        if iswindows():
            sysimage_save_replace_command(image_path, target_path)
        else:
            sysimage_do_replace(image_path, target_path)

    # Need to restart R to load with the system image before IAI can be used
    global NEEDS_RESTART
    NEEDS_RESTART = True
    return True
