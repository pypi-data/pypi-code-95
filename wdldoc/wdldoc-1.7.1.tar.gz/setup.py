# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wdldoc', 'wdldoc.bin', 'wdldoc.miniwdl', 'wdldoc.templates']

package_data = \
{'': ['*']}

install_requires = \
['cachecontrol[filecache]>=0.12.6,<0.13.0',
 'logzero>=1.5.0,<2.0.0',
 'miniwdl>=1.2.2,<2.0.0',
 'python-semantic-release>=5.1.0,<6.0.0',
 'requests>=2.23.0,<3.0.0']

entry_points = \
{'console_scripts': ['wdldoc = wdldoc.__main__:main']}

setup_kwargs = {
    'name': 'wdldoc',
    'version': '1.7.1',
    'description': 'Create WDL documentation using Markdown.',
    'long_description': '<p align="center">\n  <h1 align="center">\n  wdldoc\n  </h1>\n\n  <p align="center">\n    Convert WDL documentation to Markdown for rendering.\n    <br />\n    <a href="https://github.com/stjudecloud/wdldoc/issues">Request Feature</a>\n    ·\n    <a href="https://github.com/stjudecloud/wdldoc/issues">Report Bug</a>\n    ·\n    ⭐ Consider starring the repo! ⭐\n    <br />\n  </p>\n</p>\n\n## 📚 Getting Started\n\nFor an example of what the results can look like, check out the [GitHub Pages](https://stjudecloud.github.io/workflows/) for the [St Jude Cloud Workflows](https://github.com/stjudecloud/workflows) repo! The documentation is automatically built for each release using `wdldoc`.\n\n### Installation\n\nwdldoc is only available for Python 3.8 or higher.\n\nSuggested install method:\n\n```bash\nconda create -n wdldoc python=3.8\nconda activate wdldoc\npip install wdldoc\n```\n\n## Usage\n\nwdldoc is designed to be simple, and require as little work as possible. Once installed, simply call `wdldoc .` at the root of your WDL project, and Markdown files will be generated in the `./documentation` directory for each WDL file found. There are `tasks/` and `workflows/` subdirectories, with documentation for WDL workflow files in `workflows/`, and documentation for WDL task files in `tasks/`.\n\nAny valid WDL file will have the inputs, outputs, and meta information individually documented for all its tasks and workflows. There\'s no need to conform to any standards we dictate; if it runs, we\'ll document it.\n\nAny strings found in meta fields will be treated as Markdown, so feel free to add custom bolding, italicizing, code snippets, etc.\n\nIf there\'s any information you want to include for a file that doesn\'t fit into a meta field of one of it\'s tasks or workflows, you can include a header section of your WDL file, and we\'ll convert it to Markdown and prepend it to the documentation. This is a good place to document the uses for the file and any licensing information. Simply start a line with `##` followed by a space, and the rest of the line will be parsed as Markdown. There\'s no limit to the number of header lines. It\'s good practice to break up the header into sections using Markdown titles.\n\n```text\nusage: wdldoc [-h] [-o OUTPUT_DIRECTORY] [-d DESCRIPTION] [-c CHOICES] [-v] [--debug] sources [sources ...]\n\nGenerate clean WDL documentation from source.\n\npositional arguments:\n  sources               Top level directories to search for WDL files, or the WDL files themselves.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -o OUTPUT_DIRECTORY, --output_directory OUTPUT_DIRECTORY\n                        Directory to store markdown files. Default is `./documentation`\n  -d DESCRIPTION, --description DESCRIPTION\n                        If parameter meta fields use a JSON object, the key for the field containing the input description. Default is \'help\'. Ignored if only strings are used.\n  -c CHOICES, --choices CHOICES\n                        If parameter meta fields use a JSON object, the key for the field containing the input choices. Default is \'choices\'. Ignored if only strings are used.\n  -v, --verbose         Sets the log level to INFO.\n  --debug               Sets the log level to DEBUG.\n```\n\nEither directories or individual files can be supplied. When directories are supplied,\nwdldoc will recursively search the input directories searching for all `.wdl` files, and generate documentation for them.\n\nWDL `parameter_meta` info can be anything that conforms to the WDL spec, but we recommend one of two formats. The first is simply `input_name: "descriptive string"`. The other is a JSON object containing a description key with a string value and optionally a choices key with a list of options. The value of the "description" and "choices" keys can be specified with the `--description` and `--choices` arguments. Below is an example of both formats in one parameter meta block.\n\n```text\nparameter_meta {\n    in_bams: {\n        help: "Provide bams to run for comparison"\n    }\n    tissue_type: {\n        help: "Provide the tissue type to compare against",\n        choices: [\'blood\', \'brain\', \'solid\']\n    }\n    output_filename: "Name for the output HTML t-SNE plot"\n}\n```\n\n## 🖥️ Development\n\nIf you are interested in contributing to the code, please first review\nour [CONTRIBUTING.md][contributing-md] document. To bootstrap a\ndevelopment environment, please use the following commands.\n\n```bash\n# Clone the repository\ngit clone git@github.com:stjudecloud/wdldoc.git\ncd wdldoc\n\n# Install the project using poetry\npoetry install\n\n# Ensure pre-commit is installed to automatically format\n# code using `black`.\nbrew install pre-commit\npre-commit install\npre-commit install --hook-type commit-msg\n```\n\n## 📝 License\n\nCopyright © 2020 [St. Jude Cloud Team](https://github.com/stjudecloud).\n\nThis project is [MIT][license-md] licensed.\n\n[contributing-md]: https://github.com/stjudecloud/wdldoc/blob/master/CONTRIBUTING.md\n[license-md]: https://github.com/stjudecloud/wdldoc/blob/master/LICENSE.md\n',
    'author': 'Clay McLeod',
    'author_email': 'Clay.McLeod@STJUDE.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stjudecloud/wdldoc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
