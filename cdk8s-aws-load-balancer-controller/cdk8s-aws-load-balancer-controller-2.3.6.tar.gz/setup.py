import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk8s-aws-load-balancer-controller",
    "version": "2.3.6",
    "description": "cdk8s-aws-load-balancer-controller is an CDK8S construct library that provides AWS Alb Load Balancer Controller Configure.",
    "license": "Apache-2.0",
    "url": "https://github.com/neilkuan/cdk8s-aws-load-balancer-controller.git",
    "long_description_content_type": "text/markdown",
    "author": "Neil Kuan<guan840912@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/neilkuan/cdk8s-aws-load-balancer-controller.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk8s_aws_load_balancer_controller",
        "cdk8s_aws_load_balancer_controller._jsii"
    ],
    "package_data": {
        "cdk8s_aws_load_balancer_controller._jsii": [
            "cdk8s-aws-load-balancer-controller@2.3.6.jsii.tgz"
        ],
        "cdk8s_aws_load_balancer_controller": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-iam>=1.113.0, <2.0.0",
        "aws-cdk.core>=1.113.0, <2.0.0",
        "cdk8s==1.0.0.b10",
        "constructs>=3.3.147, <4.0.0",
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
