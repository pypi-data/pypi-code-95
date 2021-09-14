import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pahud-cdktf-aws-ecs",
    "version": "0.1.7",
    "description": "CDKTF construct library for Amazon ECS",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdktf-aws-ecs",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<pahudnet@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdktf-aws-ecs"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pahud_cdktf_aws_ecs",
        "pahud_cdktf_aws_ecs._jsii"
    ],
    "package_data": {
        "pahud_cdktf_aws_ecs._jsii": [
            "cdktf-aws-ecs@0.1.7.jsii.tgz"
        ],
        "pahud_cdktf_aws_ecs": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "cdktf-cdktf-provider-aws>=2.0.9, <3.0.0",
        "cdktf>=0.5.0, <0.6.0",
        "constructs>=3.3.75, <4.0.0",
        "jsii>=1.34.0, <2.0.0",
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
