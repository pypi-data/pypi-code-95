# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dsmigrator']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'click>=7.1.2,<8.0.0',
 'deep-security-api>=20.0.463,<21.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'requests>=2.25.1,<3.0.0',
 'rich>=10.9.0,<11.0.0',
 'urllib3>=1.26.5,<2.0.0']

entry_points = \
{'console_scripts': ['dsmg = dsmigrator.__main__:main',
                     'dsmg-rules = dsmigrator.rules_migrator:main']}

setup_kwargs = {
    'name': 'dsmigrator',
    'version': '1.0.0',
    'description': 'A cli tool to migrate Trend Micro Deep Security to the cloud.',
    'long_description': '<p align="center">\n  <img src="./logo.png" />\n</p>\n\n<h1 align="center" style="border-bottom: none">Trend Micro Policy Migrator</h1>\n<p align="center">\n  Moves your existing on-prem Deep Security deployment to CloudOne Workload Security.\n</p>\n<p align="center">Automatically.</p>\n\n<details>\n  <summary>TABLE OF CONTENTS</summary>\n\n- [Quickstart](#quickstart)\n- [Capabilities](#capabilities)\n  - [Known limitations](#known-limitations)\n- [Usage](#usage)\n  - [Command Reference](#command-reference)\n  - [Use Environment Variables](#use-environment-variables)\n- [Requirements](#requirements)\n- [Contributing](#contributing)\n- [Support](#support)\n- [License](#license)\n</details>\n\n## Quickstart\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install dsmigrator.\n\n1. Run ```pip install dsmigrator``` on a machine with access to your DSM.\n\n2. Run ```dsmg -k``` and fill out the credential prompts.\n\n## Capabilities\n\nHere\'s the current feature map of what the tool can migrate:\n\n- [x] Policies\n- [x] Policy settings\n- [x] Anti-Malware Scan Configurations\n- [x] IPS, LI, and IM custom rules\n- [x] Firewall rules\n- [x] Schedules\n- [x] Contexts\n- [x] IP lists\n- [x] MAC lists\n- [x] Port lists\n- [x] [BETA] Tasks (still quite buggy)\n- [x] [BETA] Computer Groups\n- [ ] Application Control (everything)\n- [ ] Self-signed certificate support for authenticated requests\n\n### Known limitations\n\n- Cannot migrate customized IM/LI/IP rules. Another tool will be incoming to help aid a manual process in identifying each rule that has been customized, but they will never migrate automatically due to an API limitation\n- Won\'t migrate cloud accounts. Must be reconfigured/reauthenticated in Cloud One\n- Doesn\'t migrate DSM settings, make sure to check these manually.\n- Application Control support is not on the roadmap currently. Please open an issue if this is \n\n## Usage\n\n### Command Reference\n\n```text\nUsage: dsmg [OPTIONS]\n\n  Moves your on-prem DS deployment to the cloud!\n\nOptions:\n  -ou, --original-url TEXT        A resolvable FQDN for the old DSM, with port\n                                  number (e.g. https://192.168.1.1:4119/)\n\n  -oa, --original-api-key TEXT    API key for the old DSM with Full Access\n                                  permissions\n\n  -nu, --new-url TEXT             Destination url  [default:\n                                  https://cloudone.trendmicro.com/]\n\n  -coa, --cloud-one-api-key TEXT  API key for Cloud One Workload Security with\n                                  Full Access permissions\n\n  -d, --delete-policies / --keep-policies\n                                  Wipes existing policies in Cloud One (not\n                                  required, but will give best results)\n\n  -t, --tasks                     (BETA) Enable the task migrator (may be\n                                  buggy)\n\n  -k, --insecure                  Suppress the InsecureRequestWarning for\n                                  self-signed certificates\n\n  -f, --filter TEXT               A list of policy names in form \'[name, name,\n                                  ...]\' which are the only ones which will be\n                                  transferred.\n\n  --help                          Show this message and exit.\n```\n### Use Environment Variables\n\nYou can optionally use the following environment variables to pass in your credentials:\n\n- `ORIGINAL_API_KEY`\n- `ORIGINAL_URL`\n- `CLOUD_ONE_API_KEY`\n\n## Requirements\n\n- Python3 (only tested on Python 3.7 or greater so far, so your mileage may vary)\n- One api key for your old Deep Security Manager with "Full Access" permissions\n- One api key for your Cloud One account with "Full Access" permissions\n- A resolvable FQDN to your old Deep Security Manager\n\n**NOTE:** DS Migrator currently only supports migrations from Deep Security 20 and 12.\n\n## Contributing\n\n1. Run ./dev-setup.sh, which will download nix and nix flakes.\n2. Run `nix develop` which will download and build dependencies, and drop you in a shell.\n\n## Support\n\nFor support, please open an issue on Github.\n\n## License\n\nGNU General Public License\n',
    'author': 'Alex Jackson',
    'author_email': 'alex_jackson@trendmicro.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ajaxbits/ds-migrator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
