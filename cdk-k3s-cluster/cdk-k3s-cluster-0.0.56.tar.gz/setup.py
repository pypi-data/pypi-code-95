import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-k3s-cluster",
    "version": "0.0.56",
    "description": "A JSII construct lib to deploy a K3s cluster on AWS with CDK",
    "license": "MIT",
    "url": "https://github.com/aws-samples/aws-cdk-for-k3scluster",
    "long_description_content_type": "text/markdown",
    "author": "Massimo Re Ferre<mreferre@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws-samples/aws-cdk-for-k3scluster"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_k3s_cluster",
        "cdk_k3s_cluster._jsii"
    ],
    "package_data": {
        "cdk_k3s_cluster._jsii": [
            "cdk-k3s-cluster@0.0.56.jsii.tgz"
        ],
        "cdk_k3s_cluster": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-autoscaling>=1.62.0, <2.0.0",
        "aws-cdk.aws-ec2>=1.62.0, <2.0.0",
        "aws-cdk.aws-iam>=1.62.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.62.0, <2.0.0",
        "aws-cdk.aws-logs>=1.62.0, <2.0.0",
        "aws-cdk.aws-s3>=1.62.0, <2.0.0",
        "aws-cdk.core>=1.62.0, <2.0.0",
        "aws-cdk.custom-resources>=1.62.0, <2.0.0",
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
