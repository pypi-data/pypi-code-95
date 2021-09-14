__all__ = ["loci"]

import os

import jpype

_BFJAR = os.path.join(os.path.dirname(__file__), "bioformats_package.jar")
JAR = os.getenv("BIOFORMATS_JAR", _BFJAR)
LOG_LEVEL = os.getenv("BIOFORMATS_LOG_LEVEL", "ERROR")
THREAD_ATTACH = os.getenv("BIOFORMATS_THREAD_ATTACH", True)

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=str(JAR))

loci = jpype.JPackage("loci")
loci.common.DebugTools.setRootLevel(LOG_LEVEL)
__version__ = loci.formats.FormatTools.VERSION

if THREAD_ATTACH:
    java = jpype.JPackage("java")
    if not java.lang.Thread.isAttached():
        java.lang.Thread.attach()
