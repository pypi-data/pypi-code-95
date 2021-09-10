from setuptools import setup, find_packages

setup(
    name="betterproto-twirp",
    version="1.2.16",
    description="A better Protobuf / Twirp generator & library",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="http://github.com/danielgtaylor/python-betterproto",
    author="lvhaitao, yunshu",
    author_email="xiewangming@bilibili.com",
    license="MIT",
    entry_points={
        "console_scripts": ["protoc-gen-python_betterproto=betterproto.plugin:main"]
    },
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "output", "output.*"]
    ),
    package_data={"betterproto": ["py.typed", "templates/template.py"]},
    python_requires=">=3.6",
    install_requires=[
        'dataclasses; python_version<"3.7"',
        'backports-datetime-fromisoformat; python_version<"3.7"',
        "grpclib",
        "stringcase",
        'requests',
        'python-box',
        'jsonpath-rw',
        'betterproto-twirp[compiler]'
    ],
    extras_require={"compiler": ["black", "jinja2", "protobuf"]},
    zip_safe=False,
)
