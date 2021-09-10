import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "kong-data-plane",
    "version": "0.0.0",
    "description": "kong-data-plane",
    "license": "Apache-2.0",
    "url": "https://github.com/Kong/kong-aws-cdk-dp.git",
    "long_description_content_type": "text/markdown",
    "author": "Anuj Sharma<anshrma@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/Kong/kong-aws-cdk-dp.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "kong_data_plane",
        "kong_data_plane._jsii"
    ],
    "package_data": {
        "kong_data_plane._jsii": [
            "kong-data-plane@0.0.0.jsii.tgz"
        ],
        "kong_data_plane": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-autoscaling>=1.122.0, <2.0.0",
        "aws-cdk.aws-eks>=1.122.0, <2.0.0",
        "aws-cdk.aws-iam>=1.122.0, <2.0.0",
        "aws-cdk.aws-kms>=1.122.0, <2.0.0",
        "aws-cdk.core>=1.122.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.34.0, <2.0.0",
        "kong-core<0.0.1",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
