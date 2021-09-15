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
        name = 'github3api',
        version = '0.1.2',
        description = 'An advanced REST client for the GitHub API',
        long_description = '# github3api #\n[![GitHub Workflow Status](https://github.com/soda480/github3api/workflows/build/badge.svg)](https://github.com/soda480/github3api/actions)\n[![Code Coverage](https://codecov.io/gh/soda480/github3api/branch/master/graph/badge.svg)](https://codecov.io/gh/soda480/github3api)\n[![Code Grade](https://www.code-inspector.com/project/13337/status/svg)](https://frontend.code-inspector.com/project/13337/dashboard)\n[![PyPI version](https://badge.fury.io/py/github3api.svg)](https://badge.fury.io/py/github3api)\n\nAn advanced REST client for the GitHub API. It is a subclass of [rest3client](https://pypi.org/project/rest3client/) tailored for the GitHub API with special optional directives for GET requests that can return all pages from an endpoint or return a generator that can be iterated over (for paged requests). By default all requests will be retried if ratelimit request limit is reached.\n\nSupport for executing Graphql queries including paging; Graphql queries are also retried if Graphql rate limiting occurs.\n\n\n### Installation ###\n```bash\npip install github3api\n```\n\n### Example Usage ###\n\n```python\n>>> from github3api import GitHubAPI\n```\n\n`GitHubAPI` instantiation\n```python\n# instantiate using no-auth\n>>> client = GitHubAPI()\n\n# instantiate using a token\n>>> client = GitHubAPI(bearer_token=\'****************\')\n```\n\n`GET` request\n```python\n# GET request - return JSON response\n>>> client.get(\'/rate_limit\')[\'resources\'][\'core\']\n{\'limit\': 60, \'remaining\': 37, \'reset\': 1588898701}\n\n# GET request - return raw resonse\n>>> client.get(\'/rate_limit\', raw_response=True)\n<Response [200]>\n```\n\n`POST` request\n```python\n>>> client.post(\'/user/repos\', json={\'name\': \'test-repo1\'})[\'full_name\']\n\'soda480/test-repo1\'\n\n>>> client.post(\'/repos/soda480/test-repo1/labels\', json={\'name\': \'label1\', \'color\': \'#006b75\'})[\'url\']\n\'https://api.github.com/repos/soda480/test-repo1/labels/label1\'\n```\n\n`PATCH` request\n```python\n>>> client.patch(\'/repos/soda480/test-repo1/labels/label1\', json={\'description\': \'my label\'})[\'url\']\n\'https://api.github.com/repos/soda480/test-repo1/labels/label1\'\n```\n\n`DELETE` request\n```python \n>>> client.delete(\'/repos/soda480/test-repo1\')\n```\n\n`GET all` directive - Get all pages from an endpoint and return list containing only matching attributes\n```python\nfor repo in client.get(\'/user/repos\', _get=\'all\', _attributes=[\'full_name\']):\n    print(repo[\'full_name\'])\n```\n\n`GET page` directive - Yield a page from endpoint\n```python\nfor page in client.get(\'/user/repos\', _get=\'page\'):\n    for repo in page:\n        print(repo[\'full_name\'])\n```\n\n`total` - Get total number of resources at given endpoint\n```python\nprint(client.total(\'/user/repos\'))\n6218\n```\n\n`graphql` - execute graphql query\n```python\nquery = """\n  query($query:String!, $page_size:Int!) {\n    search(query: $query, type: REPOSITORY, first: $page_size) {\n      repositoryCount\n      edges {\n        node {\n          ... on Repository {\n            nameWithOwner\n          }\n        }\n      }\n    }\n  }\n"""\nvariables = {"query": "org:edgexfoundry", "page_size":100}\nclient.graphql(query, variables)\n```\n\n`graphql paging` - execute paged graphql query\n```python\nquery = """\n  query ($query: String!, $page_size: Int!, $cursor: String!) {\n    search(query: $query, type: REPOSITORY, first: $page_size, after: $cursor) {\n      repositoryCount\n      pageInfo {\n        endCursor\n        hasNextPage\n      }\n      edges {\n        cursor\n        node {\n          ... on Repository {\n            nameWithOwner\n          }\n        }\n      }\n    }\n  }\n"""\nvariables = {"query": "org:edgexfoundry", "page_size":100}\nfor page in client.graphql(query, variables, page=True, keys=\'data.search\'):\n    for repo in page:\n        print(repo[\'node\'][\'nameWithOwner\'])\n```\n\nFor Graphql paged queries:\n- the query should include the necessary pageInfo and cursor attributes\n- the keys method argument is a dot annotated string that is used to access the resulting dictionary response object\n- the query is retried every 60 seconds (for up to an hour) if a ratelimit occur\n\n### Projects using `github3api` ###\n\n* [edgexfoundry/sync-github-labels](https://github.com/edgexfoundry/cd-management/tree/git-label-sync) A script that synchronizes GitHub labels and milestones\n\n* [edgexfoundry/prune-github-tags](https://github.com/edgexfoundry/cd-management/tree/prune-github-tags) A script that prunes GitHub pre-release tags\n\n* [edgexfoundry/create-github-release](https://github.com/edgexfoundry/cd-management/tree/create-github-release) A script to facilitate creation of GitHub releases\n\n* [soda480/prepbadge](https://github.com/soda480/prepbadge) A script that creates multiple pull request workflows to update a target organization repos with badges\n\n* [soda480/github-contributions](https://github.com/soda480/github-contributions) A script to get contribution metrics for all members of a GitHub organization using the GitHub GraphQL API\n\n\n### Development ###\n\nEnsure the latest version of Docker is installed on your development server. Fork and clone the repository.\n\nBuild the Docker image:\n```sh\ndocker image build \\\n--target build-image \\\n--build-arg http_proxy \\\n--build-arg https_proxy \\\n-t \\\ngithub3api:latest .\n```\n\nRun the Docker container:\n```sh\ndocker container run \\\n--rm \\\n-it \\\n-e http_proxy \\\n-e https_proxy \\\n-v $PWD:/code \\\ngithub3api:latest \\\n/bin/sh\n```\n\nExecute the build:\n```sh\npyb -X\n```\n\nNOTE: commands above assume working behind a proxy, if not then the proxy arguments to both the docker build and run commands can be removed.\n',
        long_description_content_type = 'text/markdown',
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: System :: Networking',
            'Topic :: System :: Systems Administration'
        ],
        keywords = '',

        author = 'Emilio Reyes',
        author_email = 'emilio.reyes@intel.com',
        maintainer = '',
        maintainer_email = '',

        license = 'Apache License, Version 2.0',

        url = 'https://github.com/soda480/github3api',
        project_urls = {},

        scripts = [],
        packages = ['github3api'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = ['rest3client'],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '',
        obsoletes = [],
    )
