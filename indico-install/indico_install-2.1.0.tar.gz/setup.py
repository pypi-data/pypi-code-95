#!/usr/bin/env python3
import os
from subprocess import check_call

from setuptools import find_packages, setup

setup(
    name="indico_install",
    version="2.1.0",
    description="An indico install platform",
    author="Indico",
    author_email="engineering@indico.io",
    packages=find_packages(),
    install_requires=[
        "click==8.0.1",
        "pyyaml==5.1.2",
        "requests==2.25.1",
        "cached_property==1.5.2",
        "setuptools==46.1.3",
        "google-cloud-storage==1.25.0",
        "tabulate==0.8.6",
        "untangle==1.1.1",
    ],
    extras_require={
        "aks": ["azure-cli==2.25.0"],
        "eks": ["boto3==1.9.176"],
        "indico": ["whatthepatch==1.0.2"],
        "saml": ["python3-saml==1.9.0"],
    },
    include_package_data=True,
    entry_points="""
        [console_scripts]
        indico=indico_install:indico_cli
    """,
    scripts=["bin/kube", "bin/cluster_info.sh"]
    + [f"bin/kube_bin/{filename}" for filename in os.listdir("bin/kube_bin")],
)

check_call(
    [
        "bash",
        "-c",
        'azcomm=$(command -v az); if ! [ -z "$azcomm" ]; then sed -i "s/^python /python3 /g" $azcomm; fi',
    ]
)
