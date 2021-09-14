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
        name = 'rest3client',
        version = '0.3.5',
        description = 'An abstraction of the requests library providing a simpler API for consuming HTTP REST APIs',
        long_description = '# rest3client #\n[![GitHub Workflow Status](https://github.com/soda480/rest3client/workflows/build/badge.svg)](https://github.com/soda480/rest3client/actions)\n[![Code Coverage](https://codecov.io/gh/soda480/rest3client/branch/master/graph/badge.svg)](https://codecov.io/gh/soda480/rest3client)\n[![Code Grade](https://www.code-inspector.com/project/12271/status/svg)](https://frontend.code-inspector.com/project/12271/dashboard)\n[![PyPI version](https://badge.fury.io/py/rest3client.svg)](https://badge.fury.io/py/rest3client)\n\nrest3client is an abstraction of the HTTP requests library (https://pypi.org/project/requests/) providing a simpler API for consuming HTTP REST APIs.\n\nThe library further abstracts the underlying HTTP requests methods providing equivalent methods for GET, POST, PATCH, PUT and DELETE. The library includes a RESTclient class that implements a consistent approach for processing request responses, extracting error messages from responses, providing standard headers to request methods, and enabling resiliency through integration with the retrying library. The abstraction enables the consumer to focus on their business logic and less on the complexites of setting up requests and processing request responses.\n\nA subclass inheriting RESTclient can override the base methods providing further customization and flexibility including the ability to automatically retry on exceptions.\n\n\n### Supported Authentication Schemes\nThe library supports most popular authentication schemes:\n- No authentication\n- Basic authentication\n- API Key-based authentication\n- Bearer token authentication\n- Token authentication\n- Certificate-based authentication\n- JWT authentication\n\n### Installation ###\n```bash\npip install rest3client\n```\n\n### API Usage ###\nThe examples below show how RESTclient can be used to consume the GitHub REST API. However RESTclient can be used to consume just about any REST API.\n\n```python\n>>> from rest3client import RESTclient\n```\n\n`RESTclient` Authentication\n```python\n# no authentication\n>>> client = RESTclient(\'api.github.com\')\n\n# basic authentication\n>>> client = RESTclient(\'my-api.my-company.com\', username=\'--my-user--\', password=\'--my-password--\')\n\n# bearer token authentication\n>>> client = RESTclient(\'api.github.com\', bearer_token=\'--my-token--\')\n\n# token authentication\n>>> client = RESTclient(\'codecov.io\', token=\'--my-token--\')\n\n# certificate-based authentication\n>>> client = RESTclient(\'my-api.my-company.com\', certfile=\'/path/to/my-certificate.pem\', certpass=\'--my-certificate-password--\')\n\n# jwt authentication\n>>> client = RESTclient(\'my-api.my-company.com\', jwt=\'--my-jwt--\')\n```\n\n`GET` request\n```python\n# return json response\n>>> client.get(\'/rate_limit\')[\'resources\'][\'core\']\n{\'limit\': 60, \'remaining\': 37, \'reset\': 1588898701}\n\n# return raw resonse\n>>> client.get(\'/rate_limit\', raw_response=True)\n<Response [200]>\n```\n\n`POST` request\n```python\n>>> client.post(\'/user/repos\', json={\'name\': \'test-repo1\'})[\'full_name\']\n\'soda480/test-repo1\'\n\n>>> client.post(\'/repos/soda480/test-repo1/labels\', json={\'name\': \'label1\', \'color\': \'#006b75\'})[\'url\']\n\'https://api.github.com/repos/soda480/test-repo1/labels/label1\'\n```\n\n`PATCH` request\n```python\n>>> client.patch(\'/repos/soda480/test-repo1/labels/label1\', json={\'description\': \'my label\'})[\'url\']\n\'https://api.github.com/repos/soda480/test-repo1/labels/label1\'\n```\n\n`PUT` request\n```python\n>>> client.put(endpoint, data=None, json=None, **kwargs)\n```\n\n`DELETE` request\n```python\n>>> client.delete(\'/repos/soda480/test-repo1\')\n```\n\n`HEAD` request\n```python\n>>> response = client.head(\'/user/repos\', raw_response=True)\n>>> response.headers\n```\n\n#### Retries\nAdd support for retry using the `retrying` library: https://pypi.org/project/retrying/\n\nInstantiating RESTclient with a `retries` key word argument will decorate all request methods (`get`, `put`, `post`, `delete` and `patch`) with a retry decorator using the provided arguments. For example, to retry on any error waiting 2 seconds between retries and limiting retry attempts to 3.\n```python\n>>> client = RESTclient(\'api.github.com\', retries=[{\'wait_fixed\': 2000, \'stop_max_attempt_number\': 3}])\n```\nMultiple retry specifications can be provided, however the arguments provided **must** adhere to the retrying specification.\n\nSpecifying retries for specific exceptions in subclasses is simple. RESTclient will automatically discover all retry methods defined in subclasses and decorate all request methods accordingly. Arguments for the retry decorator must be provided in the docstring for the respective retry method. Retry methods must begin with `retry_`.\n\nFor example:\n\n```python\n@staticmethod\ndef retry_connection_error(exception):\n    """ return True if exception is ProxyError False otherwise\n         retry:\n            wait_random_min:10000\n            wait_random_max:20000\n            stop_max_attempt_number:6\n    """\n    if isinstance(exception, ProxyError):\n        return True\n    return False\n```\n\nAdding the method above to a subclass of RESTclient will have the affect of decorating all the request methods with the following decorator:\n\n```python\n@retry(retry_on_exception=retry_connection_error, \'wait_random_min\'=10000, \'wait_random_max\'=20000, \'stop_max_attempt_number\'=6)\n```\n\nYou also have the option of overriding any of the retry argument with environment variables. The environment variable must be of the form `${retry_method_name}_${argument}` in all caps. For example, setting the following environment variables will override the static settings in the `retry_connection_error` method docstring:\n\n```bash\nexport RETRY_CONNECTION_ERROR_WAIT_RANDOM_MIN = 5000\nexport RETRY_CONNECTION_ERROR_WAIT_RANDOM_MAX = 15000\n```\n\n#### Real Eamples\nSee [GitHub3API](https://github.com/soda480/github3api) for an example of how RESTclient can be subclassed to provide further custom functionality for a specific REST API (including retry on exceptions). \n\n### CLI Usage ###\nRESTclient comes packaged with a command line interace (CLI) that can be used to consume REST APIs using the RESTclient class. To consume the CLI simply build and run the Docker container as described below, except when building the image exclude the `--target build-image` argument.\n```bash\nusage: rest [-h] [--address ADDRESS] [--json JSON_DATA]\n            [--headers HEADERS_DATA] [--attributes ATTRIBUTES] [--debug]\n            [--raw] [--key]\n            method endpoint\n\nA CLI for rest3client\n\npositional arguments:\n  method                HTTP request method\n  endpoint              REST API endpoint\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --address ADDRESS     HTTP request web address\n  --json JSON_DATA      string representing JSON serializable object to send\n                        to HTTP request method\n  --headers HEADERS_DATA\n                        string representing headers dictionary to send to HTTP\n                        request method\n  --attributes ATTRIBUTES\n                        attributes to filter from response - if used with\n                        --raw will filter from headers otherwise will filter\n                        from JSON response\n  --debug               display debug messages to stdout\n  --raw                 return raw response from HTTP request method\n  --key                 return key value in response - only if response is a\n                        dictionary containing a single key value\n```\n\nSet environment variables prefixed with `R3C_`.\n\nTo set the web address of the API:\n```bash\nexport R3C_ADDRESS=my-api.my-company.com\n```\n\nFor bearer token authentication:\n```bash\nexport R3C_BEARER_TOKEN=--my-token--\n```\n\nFor token authentication:\n```bash\nexport R3C_TOKEN=--my-token--\n```\n\nFor basic authentication:\n```bash\nexport R3C_USERNAME=\'--my-username--\'\nexport R3C_PASSWORD=\'--my-password--\'\n```\n\nFor certificate-based authentication:\n```bash\nexport R3C_CERTFILE=\'/path/to/my-certificate.pem\'\nexport R3C_CERTPASS=\'--certificate-password--\'\n```\n\nFor jwt-based authentication:\n```bash\nexport R3C_JWT=--my-jwt--\n```\n\nSome examples for how to execute the CLI to consume the GitHUB API:\n\n```bash\nrest POST /user/repos --json "{\'name\': \'test-repo1\'}" --attributes "name, private, description, permissions"\n\nrest GET /user/repos --attributes "name, full_name, private, description, permissions"\n\nrest POST /repos/soda480/test-repo1/labels --json "{\'name\': \'label1\', \'color\': \'C7EFD5\'}" --attributes url\n\nrest PATCH /repos/soda480/test-repo1/labels/label1 --json "{\'description\': \'my label\'}" --attributes url\n\nrest DELETE /repos/soda480/test-repo1/labels/label1\n\nrest GET /repos/soda480/test-repo1/labels --attributes name\n\nrest DELETE /repos/soda480/test-repo1 --debug\n\nrest GET /rate_limit --raw\n```\n\n### Development ###\n\nEnsure the latest version of Docker is installed on your development server. Fork and clone the repository.\n\nBuild the Docker image:\n```sh\ndocker image build \\\n--target build-image \\\n--build-arg http_proxy \\\n--build-arg https_proxy \\\n-t \\\nrest3client:latest .\n```\n\nRun the Docker container:\n```sh\ndocker container run \\\n--rm \\\n-it \\\n-e http_proxy \\\n-e https_proxy \\\n-v $PWD:/code \\\nrest3client:latest \\\n/bin/sh\n```\n\nExecute the build:\n```sh\npyb -X\n```\n\nNOTE: commands above assume working behind a proxy, if not then the proxy arguments to both the docker build and run commands can be removed.\n',
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

        url = 'https://github.com/soda480/rest3client',
        project_urls = {},

        scripts = [],
        packages = ['rest3client'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {
            'console_scripts': ['rest = rest3client.rest:main']
        },
        data_files = [],
        package_data = {},
        install_requires = [
            'requests',
            'retrying'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '',
        obsoletes = [],
    )
