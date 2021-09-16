#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'kubernator',
        version = '0.0.1.dev20210916012146',
        description = 'Kubernator is the a pluggable framework for K8S provisioning',
        long_description = '# Kubernator\n\nKubernator™ (Ktor™) is an integrated solution for the Kubernetes state management. It operates on directories,\nprocessing their content via a collection of plugins, generating Kubernetes resources in the process, validating them,\ntransforming them and then applying against the Kubernetes cluster.\n\n## Notices\n\n### License\n\nThe product is licensed under the Apache License, Version 2.0. Please see LICENSE for further details.\n\n### Warranties and Liability\n\nKubernator and its plugins are provided on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,\nincluding, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR\nA PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing\nKubernator and assume any risks associated with doing so.\n\n### Trademarks\n\n"Kubernator" and "Ktor" are trademarks or registered trademarks of Express Systems USA, Inc and Karellen, Inc. All other\ntrademarks are property of their respective owners.\n\n## Problem Statement\n\n## Solution\n\n## Mode of Operation\n\nKubernator is a command line utility. Upon startup and processing of the command line arguments and initializing\nlogging, Kubernator initializes plugins. Current plugins include:\n\n0. Kubernator App\n1. Terraform\n2. kOps\n3. Kubernetes\n4. Helm\n5. Template\n\nThe order of initialization matters as it\'s the order the plugin handlers are executed!\n\nThe entire application operates in the following stages by invoking each plugin\'s stage handler in sequence:\n\n1. Plugin Init Stage\n2. Pre-start script (if specified)\n3. Plugin Start Stage\n4. For each directory in the pipeline:\n    1. Plugin Before Directory Stage\n    2. If `.kubernator.py` is present in the directory:\n        1. Plugin Before Script Stage\n        2. `.kubernator.py` script\n        3. Plugin After Script Stage\n    3. Plugin After Directory Stage\n5. Plugin End Stage\n\nEach plugin individually plays a specific role and performs a specific function which will be described in a later\nsection.\n\n## State/Context\n\nThere is a global state that is carried through as the application is running. It is a hierarchy of objects (`context`)\nthat follows the parent-child relationship as the application traverses the directory structure. For example, given the\ndirectory structure `/a/b`, `/a/c`, and `/a/c/d` any value of the context set or modified in context scoped to\ndirectory `/a` is visible in directories `/a/b`, `/a/c` and `/a/c/d`, while the same modified or set in `/a/b` is only\nvisible there, while one in `/a/c` is visible in `/a/c` and in `/a/c/d` but not `/a` or `/a/b`.\n\nAdditionally, there is a `context.globals` which is the top-most context that is available in all stages that are not\nassociated with the directory structure.\n\nNote, that in cases where the directory structure traversal moves to remote directories (that are actualized by local\ntemporary directories), such remote directory structure enters the context hierarchy as a child of the directory in\nwhich remote was registered.\n\nAlso note, that context carries not just data by references to essential functions.\n\nIn pre-start and `.kubernator.py` scripts the context is fully available as a global variable `ktor`.\n\n### Plugins\n\n#### Kubernator App Plugin\n\nThe role of the Kubernator App Plugin is to traverse the directory structure, expose essential functions through context\nand to run Kubernator scripts.\n\nIn the *After Directory Stage* Kubernator app scans the directories immediately available in the current, sorts them in\nthe alphabetic order, excludes those matching any of the patterns in `context.app.excludes` and then queues up the\nremaining directories in the order the match the patterns in `context.app.includes`.\n\nThus, for a directory content `/a/foo`, `/a/bal`, `/a/bar`, `/a/baz`, excludes `f*`, and includes `baz` and `*`, the\nresulting queue of directories to traverse will be `/a/baz`, `/a/bal`, `/a/bar`.\n\nNotice, that user can further interfere with processing order of the directory queue by asking Kubernator to walk\narbitrary paths, both local and remote.\n\n##### Context\n\n* `ktor.app.args`\n  > Namespace containing command line argument values\n* `ktor.app.walk_local(*paths: Union[Path, str, bytes])`\n  > Immediately schedules the paths to be traversed after the current directory by adding them to the queue\n  > Relative path is relative to the current directory\n* `ktor.app.walk_remote(repo, *path_prefixes: Union[Path, str, bytes])`\n  > Immediately schedules the path prefixes under the remote repo URL to be traversed after the current directory by\n  > adding them to the queue. Only Git URLs are currently supported.\n  > All absolute path prefixes are relativized based on the repository.\n* `ktor.app.repository_credentials_provider(func: Callable)`\n  > Sets a repository credentials provider function `func` that sets/overwrites credentials for URLs being specified by\n  > `walk_remote`. The callable `func` accepts a single argument containing a parsed URL in a form of tuple. The `func`\n  > is expected to return a tuple of three elements representing URL schema, username and password. If the value should\n  > not be changed it should be None. To convert from `git://repo.com/hello` to HTTPS authentication one should write\n  > a function returning `("https", "username", "password")`. The best utility is achieved by logic that allows running\n  > the plan both in CI and local environments using different authentication mechanics in different environments.\n\n#### Terraform\n\nThis is exclusively designed to pull the configuration options out of Terraform and to allow scripts and plugins to\nutilize that data.\n\n##### Context\n\n* `ktor.tf`\n  > A dictionary containing the values from Terraform output\n\n#### Kops\n\n##### Context\n\n#### Kubernetes\n\n##### Context\n\n#### Helm\n\n##### Context\n\n#### Templates\n\n##### Context\n\n## Examples\n\n### Adding Remote Directory\n\n```python\nktor.app.repository_credentials_provider(lambda r: ("ssh", "git", None))\nktor.app.walk_remote("git://repo.example.com/org/project?ref=dev", "/project")\n```\n\n### Adding Local Directory\n\n```python\nktor.app.walk_local("/home/username/local-dir")\n```\n\n### Using Transformers\n\n```python\ndef remove_replicas(resources, r: "K8SResource"):\n    if (r.group == "apps" and r.kind in ("StatefulSet", "Deployment")\n            and "replicas" in r.manifest["spec"]):\n        logger.warning("Resource %s in %s contains `replica` specification that will be removed. Use HPA!!!",\n                       r, r.source)\n        del r.manifest["spec"]["replicas"]\n\n\nktor.k8s.add_transformer(remove_replicas)\n```\n',
        long_description_content_type = 'text/markdown',
        classifiers = [
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 3.9',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX',
            'Operating System :: POSIX :: Linux',
            'Environment :: Console',
            'Topic :: Utilities',
            'Topic :: System :: Monitoring',
            'Topic :: System :: Distributed Computing',
            'Topic :: System :: Clustering',
            'Topic :: System :: Networking',
            'Intended Audience :: System Administrators',
            'Intended Audience :: Developers',
            'Development Status :: 4 - Beta'
        ],
        keywords = 'kubernetes k8s kube top provisioning kOps terraform tf AWS',

        author = 'Express Systems USA, Inc.',
        author_email = '',
        maintainer = 'Karellen, Inc., Arcadiy Ivanov',
        maintainer_email = 'supervisor@karellen.co,arcadiy@karellen.co',

        license = 'Apache License, Version 2.0',

        url = 'https://github.com/karellen/kubernator',
        project_urls = {
            'Bug Tracker': 'https://github.com/karellen/kubernator/issues',
            'Documentation': 'https://github.com/karellen/kubernator/',
            'Source Code': 'https://github.com/karellen/kubernator/'
        },

        scripts = [],
        packages = ['kubernator'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {
            'console_scripts': ['kubernator = kubernator:main']
        },
        data_files = [],
        package_data = {
            'kubernator': ['LICENSE']
        },
        install_requires = [
            'appdirs~=1.4',
            'coloredlogs~=15.0',
            'gevent>=21.1.2',
            'jinja2~=2.11',
            'json-log-formatter~=0.3',
            'jsonpatch~=1.32',
            'jsonpath-ng~=1.5',
            'kubernetes~=17.0',
            'openapi-schema-validator~=0.1',
            'openapi-spec-validator~=0.3',
            'requests~=2.25'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '>=3.9',
        obsoletes = [],
    )
