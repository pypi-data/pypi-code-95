import os
import sys
import shutil
import subprocess

__version__ = "1.2021.10"

def _find_java_path():
    _path = os.environ.get("PATH", "").split(os.pathsep)

    _java_home = os.environ.get("JAVA_HOME", "")
    if _java_home != "":
        _path.insert(0, os.sep.join([_java_home, "bin"]))

    _java_bin = os.environ.get("JAVA_BINDIR", "")
    if _java_bin != "":
        _path.insert(0, _java_bin)

    found = shutil.which('java', path=os.pathsep.join(filter(len, _path)))

    return found

def run_plantuml():
    _java = _find_java_path()
    if _java is None:
        raise FileNotFoundError("java not found in JAVA_HOME nor PATH")
    cmd = [_java, "-jar", os.sep.join([
        os.path.dirname(__file__), "plantuml." + __version__ + ".jar"]),
           *sys.argv[1:]]
    exit(subprocess.run(cmd).returncode)
