import os
from functools import lru_cache
from typing import TYPE_CHECKING, Any, List, Union

import jpype

if TYPE_CHECKING:
    import _loci as _locimod
    import _ome as _omemod

__all__ = [
    "start_jvm",
    "get_loci",
    "set_loci_log_level",
    "get_ome",
    "loci",
    "ome",
    "__version__",
]


_BFJAR = os.path.join(os.path.dirname(__file__), "bioformats_package.jar")
LOG_LEVEL = os.getenv("BIOFORMATS_LOG_LEVEL", "ERROR")
ATTACH_THREAD = os.getenv("BIOFORMATS_ATTACH_THREAD", True)
JAR = os.getenv("BIOFORMATS_JAR", _BFJAR)


@lru_cache()
def start_jvm(
    classpath: Union[str, List[str]] = JAR,
    attach_thread=ATTACH_THREAD,
    memory="1024m",
    **kwargs,
):
    """Start the Java virtual machine with `jpype.startJVM`.

    Parameters
    ----------
    classpath : str or List[str], optional
        jar path or list of jar paths, by default the bioformats_package.jar
    attach_thread : [type], optional
        If `True`, attaches the current thread to the JVM as a user thread. by default True.
        Can also be set with the "BIOFORMATS_ATTACH_THREAD" environment variable
    memory : str, optional
        Java memory to use, by default "1024m"
    """
    if jpype.isJVMStarted():
        return

    jpype.startJVM(f"-Xmx{memory}", classpath=classpath, **kwargs)

    if attach_thread:
        java = jpype.JPackage("java")
        if not java.lang.Thread.isAttached():
            java.lang.Thread.attach()


@lru_cache()
def get_loci(log_level: str = LOG_LEVEL) -> "_locimod.__module_protocol__":
    """Start JVM (if necessary) and get the `loci` module

    Parameters
    ----------
    log_level : str
        the logging level for loci tools.  by default "ERROR". Can also be set by setting
        the 'BIOFORMATS_LOG_LEVEL' environment variable.

    Returns
    -------
    loci
        the loci module from bioformats_package.jar
    """
    start_jvm()
    loci = jpype.JPackage("loci")
    loci.common.DebugTools.setRootLevel(log_level)
    loci.__version__ = loci.formats.FormatTools.VERSION
    return loci


def set_loci_log_level(level):
    """Set loging level for loci tools."""
    get_loci().common.DebugTools.setRootLevel(level)


@lru_cache()
def get_ome() -> "_omemod.__module_protocol__":
    """Start JVM (if necessary) and get the `ome` module"""
    start_jvm()
    return jpype.JPackage("ome")


def __getattr__(name: str) -> Any:
    if name == "__version__":
        return get_loci().__version__
    if name == "loci":
        return get_loci()
    if name == "ome":
        return get_ome()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
