import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "kong-core",
    "version": "0.0.2",
    "description": "kong-core",
    "license": "Apache-2.0",
    "url": "https://github.com/Kong/kong-aws-cdk-core.git",
    "long_description_content_type": "text/markdown",
    "author": "Anuj Sharma<anshrma@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/Kong/kong-aws-cdk-core.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "kong_core",
        "kong_core._jsii"
    ],
    "package_data": {
        "kong_core._jsii": [
            "kong-core@0.0.2.jsii.tgz"
        ],
        "kong_core": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-autoscaling-hooktargets>=1.121.0, <2.0.0",
        "aws-cdk.aws-autoscaling>=1.121.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.121.0, <2.0.0",
        "aws-cdk.aws-eks>=1.121.0, <2.0.0",
        "aws-cdk.aws-elasticache>=1.121.0, <2.0.0",
        "aws-cdk.aws-events-targets>=1.121.0, <2.0.0",
        "aws-cdk.aws-events>=1.121.0, <2.0.0",
        "aws-cdk.aws-iam>=1.121.0, <2.0.0",
        "aws-cdk.aws-logs>=1.121.0, <2.0.0",
        "aws-cdk.aws-rds>=1.121.0, <2.0.0",
        "aws-cdk.aws-route53>=1.121.0, <2.0.0",
        "aws-cdk.aws-sqs>=1.121.0, <2.0.0",
        "aws-cdk.core>=1.121.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
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
