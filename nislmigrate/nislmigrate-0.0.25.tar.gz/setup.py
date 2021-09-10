# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nislmigrate',
 'nislmigrate.extensibility',
 'nislmigrate.facades',
 'nislmigrate.logs',
 'nislmigrate.migrators',
 'nislmigrate.utility']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0', 'pymongo>=3.12.0,<4.0.0']

entry_points = \
{'console_scripts': ['nislmigrate = nislmigrate.migration_tool:main']}

setup_kwargs = {
    'name': 'nislmigrate',
    'version': '0.0.25',
    'description': 'The tool for migrating SystemLink data.',
    'long_description': '# NI-SystemLink-Migration tool `nislmigrate`\n`nislmigrate` is a command line utility for migration, backup, and restore of supported SystemLink services.\n# Installation\n### Prerequisites\n#### 1. SystemLink\n- This tool currently supports migration from a SystemLink 2020R1 server, migration between other versions has not been tested.\n- **We assume the server you are migrating to is clean with no data. Migrating to a server with existing data will result in data loss.**\n- Not all services are supported yet, see **Supported Services** for details.\n- This tool assumes a single-box SystemLink installation. \n- This tool must be run on the same machines as the SystemLink installations.\n#### 2. Python\n- This tool requires [Python 3.8](https://www.python.org/downloads/release/python-3811/) to run.\n- The documentation in this repository assumes Python has been added to your [**PATH**](https://datatofish.com/add-python-to-windows-path/).\n### Installation\nThe latest released version of the tool can be installed by running:\n```bash\npip install nislmigrate\n```\n# Usage\n### Backup\nTo backup the data for a service listed in the **Supported Services** section run the tool with elevated permissions and the `capture` option and the corresponding flag for each of the services you want to back up (e.g. `--tags`):\n```bash\nnislmigrate capture --tags\n```\nThis will backup the data corresponding with each service into the default migration directory (`C:\\Users\\[user]\\Documents\\migration\\`). You can specify a different migration directory using the `--dir [path]` option:\n```bash\nnislmigrate capture --tags --dir C:\\custom-backup-location\n```\n\n### Restore\nTo restore the data for a service listed in the **Supported Services** section run the tool with elevated permissions and the `restore` option and the corresponding flag for each of the services you want to restore (e.g. `--tags`):\n```bash\nnislmigrate capture --tags\n```\nThis will restore the data corresponding with each service from the default migration directory (`C:\\Users\\[user]\\Documents\\migration\\`). If your captured data is in a different directory that can be specified with the `--dir [path]` option:\n```bash\nnislmigrate capture --tags --dir C:\\custom-backup-location\n```\n### Migration\nTo migrate from one SystemLink server instance (server A) to a different instance (server B):\n1. Install the migration tool on server A and server B.\n1. Follow the backup instructions to backup the data from server A.\n1. Copy the data produced by the backup of server A on server B.\n1. Ensure server B is a clean SystemLink install with no existing data.\n1. Follow the restore instructions to restore the backed up data onto server B.\n\n# Development\nSee `CONTRIBUTING.MD` for detailed instructions on developing, testing, and releasing the tool.\n\n# Supported Services\nThe following services can be migrated with this utility:\n\n- Tag Ingestion and Tag History: `--tags`\n- File Ingestion: `--files` \n    - Must migrate file to the same storage location on the new System Link server.\n    - To captured/restore only the database but not the files themselves, use `--files --files-metadata-only`. This could be useful if, for example, files are stored on a file server with separate backup.\n- Notifications: `--notification`\n\nThere are plans to support the following services in the near future:\n- Tag Alarm Rules: `--tagrule`\n- Alarm Instances: `--alarms`\n- OPC UA Client: `--opc`\n- Test Monitor: `--tests`\n- Asset Management: `--assets`\n    - Cannot be migrated between 2020R1 and 2020R2 servers\n- Repository: `--repo`\n    - Feeds may require additional updates if servers used for migration have different domain names\n- User Data: `--userdata`\n- States: `--states`\n    - Feeds may require additional updates if servers used for migration have different domain names\n    - Cannot be migrated between 2020R1 and 2020R2 servers\n- Security `--security`\n  \nThe following list of services is explicitly not supported because of issues that arose when developing and testing migrating the service that will require changes to the service rather than the migration utility to enable support:\n- Cloud Connector\n',
    'author': 'cnunnall',
    'author_email': 'christian.nunnally@ni.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.8,<4.0.0',
}


setup(**setup_kwargs)
