# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['lcdoc',
 'lcdoc.mkdocs',
 'lcdoc.mkdocs.blacklist',
 'lcdoc.mkdocs.changelog',
 'lcdoc.mkdocs.credits',
 'lcdoc.mkdocs.custom_dir',
 'lcdoc.mkdocs.find_pages',
 'lcdoc.mkdocs.lp',
 'lcdoc.mkdocs.lp.plugs',
 'lcdoc.mkdocs.page_tree',
 'lcdoc.mkdocs.replace',
 'lcdoc.mkdocs.stats']

package_data = \
{'': ['*'],
 'lcdoc': ['assets/mkdocs/*',
           'assets/mkdocs/lcd/partials/*',
           'assets/mkdocs/lcd/src/_snippets/*',
           'assets/mkdocs/lcd/src/md/keepachangelog/*'],
 'lcdoc.mkdocs.changelog': ['assets/keepachangelog/*'],
 'lcdoc.mkdocs.lp': ['assets/*',
                     'assets/arch/*',
                     'assets/css/*',
                     'assets/javascript/*',
                     'assets/plantuml/*'],
 'lcdoc.mkdocs.lp.plugs': ['assets/*']}

install_requires = \
['anybadge>=1.7.0,<2.0.0',
 'git-changelog>=0.4.0,<0.5.0',
 'httpx>=0.17.1,<0.18.0',
 'markdown-include>=0.6.0,<0.7.0',
 'mkdocs-exclude>=1.0.2,<2.0.0',
 'mkdocs-macros-plugin>=0.5.12,<0.6.0',
 'mkdocs-material>=6.1.0,<7.0.0',
 'mkdocs-pymdownx-material-extras>=1.1.3,<2.0.0',
 'mkdocs>=1.1.2,<2.0.0',
 'plantuml-markdown>=3.4.2,<4.0.0',
 'pycond',
 'pytest-cov>=2.10.1,<3.0.0',
 'pytest-randomly>=3.4.1,<4.0.0',
 'pytest-sugar>=0.9.4,<0.10.0',
 'pytest-xdist>=2.1.0,<3.0.0',
 'pytest>=6.0.1,<7.0.0',
 'toml>=0.10.1,<0.11.0']

entry_points = \
{'mkdocs.plugins': ['lcd-blacklist = lcdoc.mkdocs.blacklist:BlacklistPlugin',
                    'lcd-changelog = lcdoc.mkdocs.changelog:ChangeLogPlugin',
                    'lcd-credits = lcdoc.mkdocs.credits:CreditsPlugin',
                    'lcd-custom-dir = lcdoc.mkdocs.custom_dir:CustomDirPlugin',
                    'lcd-find-pages = '
                    'lcdoc.mkdocs.find_pages:MDFindPagesPlugin',
                    'lcd-lp = lcdoc.mkdocs.lp:LPPlugin',
                    'lcd-md-replace = lcdoc.mkdocs.replace:MDReplacePlugin',
                    'lcd-page-tree = lcdoc.mkdocs.page_tree:PageTreePlugin',
                    'lcd-stats = lcdoc.mkdocs.stats:StatsPlugin']}

setup_kwargs = {
    'name': 'docutools',
    'version': '2021.9.14',
    'description': 'Documentation Tools for the Mkdocs Material Framework',
    'long_description': '#  docutools\n\n<!-- id: 58ce0e4068dce84983a2caa8a1e87f12 -->\n[![docs pages][docs pages_img]][docs pages] [![gh-ci][gh-ci_img]][gh-ci] [![pkg][pkg_img]][pkg] [![code_style][code_style_img]][code_style] \n\n[docs pages]: https://AXGKl.github.io/docutools\n[docs pages_img]: https://AXGKl.github.io/docutools/img/badge_docs.svg\n[gh-ci]: https://github.com/AXGKl/docutools/actions/workflows/ci.yml\n[gh-ci_img]: https://github.com/AXGKl/docutools/actions/workflows/ci.yml/badge.svg\n[pkg]: https://pypi.org/project/docutools/2021.9.14/\n[pkg_img]: https://AXGKl.github.io/docutools/img/badge_pypi.svg\n[code_style]: https://pypi.org/project/axblack/\n[code_style_img]: https://AXGKl.github.io/docutools/img/badge_axblack.svg\n\n<!-- id: 58ce0e4068dce84983a2caa8a1e87f12 -->\n\n\n## [Documentation](https://axgkl.github.io/docutools/) building tools\n\nThis repo is providing a set of plugins for [mkdocs material](https://squidfunk.github.io/mkdocs-material/) compatible documentation.\n\nIt is meant to be used as a development dependency for projects.\n\nMost notable feature: **[Literate Programming](./features/lp/)**.\n\n> Most plugins should work in other mkdocs variants as well. No guarantees though.\n\nNote: Some features are not yet documented.\n\n\nLast modified: Tue, 14 Sep 2021 23h GMT\n ',
    'author': 'Gunther Klessinger',
    'author_email': 'gkle_ss_ing_er@gmx.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://axgkl.github.io/docutools/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
