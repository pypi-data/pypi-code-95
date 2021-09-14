from __future__ import print_function

from distutils import spawn
import glob
import os
import subprocess
import sys
import versioneer
import pathlib

from setuptools import find_packages
from setuptools import setup

# Find the Protocol Compiler.
if "PROTOC" in os.environ and os.path.exists(os.environ["PROTOC"]):
    protoc = os.environ["PROTOC"]
elif os.path.exists("../src/protoc"):
    protoc = "../src/protoc"
elif os.path.exists("../src/protoc.exe"):
    protoc = "../src/protoc.exe"
elif os.path.exists("../vsprojects/Debug/protoc.exe"):
    protoc = "../vsprojects/Debug/protoc.exe"
elif os.path.exists("../vsprojects/Release/protoc.exe"):
    protoc = "../vsprojects/Release/protoc.exe"
else:
    protoc = spawn.find_executable("protoc")


def generate_proto(source, base_dir):
    """Invokes the Protocol Compiler to generate a _pb2.py."""

    output = source.replace(".proto", "_pb2.py")

    if not os.path.exists(output) or (
        os.path.exists(source)
        and os.path.getmtime(source) > os.path.getmtime(output)
    ):
        print("Generating %s..." % output)

        if not os.path.exists(source):
            sys.stderr.write("Cannot find required file: %s\n" % source)
            sys.exit(-1)

        if protoc is None:
            sys.stderr.write(
                "protoc is not installed nor found in ../src.  Please compile it "
                "or install the binary package.\n"
            )
            sys.exit(-1)

        protoc_command = [
            protoc,
            f"-I{base_dir}",
            f"--python_out={base_dir}",
            source,
        ]
        if subprocess.call(protoc_command) != 0:
            sys.exit(-1)


_PROTO_FILE_PATTERNS = [
    ("bmlx_components/proto/*.proto", "bmlx_components/proto"),
    (
        "bmlx_components/mlplat-protos/mlplat/feature/*.proto",
        "bmlx_components/mlplat-protos",
    ),
]

for (file_pattern, base_dir) in _PROTO_FILE_PATTERNS:
    for proto_file in glob.glob(file_pattern):
        generate_proto(proto_file, base_dir)

        # generate __init__.py
        parts = proto_file.split("/")
        for i in range(0, len(parts)):
            if i > 0:
                module_init_file = os.path.join(
                    "/".join(parts[0:i]), "__init__.py"
                )
                if not os.path.exists(module_init_file):
                    pathlib.Path(module_init_file).touch()


tpls = [n.as_posix() for n in pathlib.Path().rglob("*.yml")]

# Get various package dependencies list.
with open("bmlx_components/dependencies.py") as fp:
    globals_dict = {}
    exec(fp.read(), globals_dict)  # pylint: disable=exec-used
_make_required_install_packages = globals_dict["make_required_install_packages"]
_make_required_test_packages = globals_dict["make_required_test_packages"]


# Get the long description from the README file.
with open("README.md") as fp:
    _LONG_DESCRIPTION = fp.read()

commands = versioneer.get_cmdclass().copy()

setup(
    name="bmlx_components",
    version=versioneer.get_version(),
    author="",
    author_email="",
    license="Apache 2.0",
    cmdclass=commands,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    namespace_packages=[],
    install_requires=_make_required_install_packages(),
    extras_require={},
    setup_requires=["pytest-runner"],
    tests_require=_make_required_test_packages(),
    # python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,<4',
    python_requires="==3.7.*",
    packages=find_packages(),
    data_files=[("", tpls),],
    include_package_data=True,
    description="bmlx components is repo for components used in bmlx",
    long_description=_LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    keywords="bigo bmlx components",
    url="https://git.sysop.bigo.sg/mlplat/bmlx-components",
    download_url="https://git.sysop.bigo.sg/mlplat/bmlx-components",
    requires=[],
    dependency_links=[],
    zip_safe=False,
)
