# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['makeline',
 'resources',
 'resources.profile',
 'resources.sparv',
 'resources.templates',
 'scripts',
 'workflow',
 'workflow.annotate',
 'workflow.config',
 'workflow.model',
 'workflow.model.dehyphenation',
 'workflow.model.deprecated',
 'workflow.model.utility',
 'workflow.rules',
 'workflow.rules.xslt_rules']

package_data = \
{'': ['*'],
 'resources': ['xslt/*'],
 'scripts': ['wip/*'],
 'workflow.rules': ['archive/*']}

install_requires = \
['Jinja2>=2.11.3,<3.0.0',
 'click>=7.1.2,<8.0.0',
 'cookiecutter>=1.7.2,<2.0.0',
 'dehyphen>=0.3.4,<0.4.0',
 'loguru>=0.5.3,<0.6.0',
 'pandas>=1.2.3,<2.0.0',
 'pygit2>=1.5.0,<2.0.0',
 'rich>=10.0.1,<11.0.0',
 'snakefmt>=0.3.1,<0.4.0',
 'snakemake>=6.0.5,<7.0.0',
 'spacy==2.3.7',
 'stanza>=1.2.3,<2.0.0',
 'transformers>=4.3.3,<5.0.0',
 'untangle>=1.1.1,<2.0.0']

entry_points = \
{'console_scripts': ['config_value = scripts.config_value:main',
                     'parla_frequencies = scripts.parla_frequencies:main',
                     'parla_transform = scripts.parla_transform:main']}

setup_kwargs = {
    'name': 'westac-parlaclarin-pipeline',
    'version': '2021.9.3',
    'description': 'Pipeline that transforms Parla-Clarin XML files',
    'long_description': '# Parla-Clarin Workflow\n\nThis package implements Stanza part-of-speech annotation of ParlaClarin XML files.\n\n## Prerequisites\n\n- Git\n- Python 3.8.5^\n- GNU make\n- Poetry\n\n## Install\n\nClone this repository:\n\n1. cd a-project-directory-of-your-choosing\n1. git clone git@github.com:welfare-state-analytics/westac_parlaclarin_pipeline\n1. cd westac_parlaclarin_pipeline\n\nOr install python package:\n\n1. poetry init --python 3.8.5\n1. poetry install westac_parlaclarin_pipeline\n1. poetry install westac_parlaclarin_pipeline\n\n## Run annotation\n\nUpdate repository:\n\n```bash\nmake update-repository\nmake update-repository-timestamps\n```\n\nUpdate all (changed) annotations:\n\n```bash\nmake annotate\n```\n\nUpdate a single year (and set cpu count):\n\n```bash\nmake annotate YEAR=1960 CPU_COUNT=1\n```\n\n## Configuration\n\n\n```yaml\nwork_folders: !work_folders &work_folders\n  data_folder: /data/riksdagen_corpus_data\n\nparla_clarin: !parla_clarin &parla_clarin\n  repository_folder: /data/riksdagen_corpus_data/riksdagen-corpus\n  repository_url: https://github.com/welfare-state-analytics/riksdagen-corpus.git\n  repository_branch: dev\n  folder: /data/riksdagen_corpus_data/riksdagen-corpus/corpus\n\nextract_speeches: !extract_speeches &extract_speeches\n  folder: /data/riksdagen_corpus_data/riksdagen-corpus-exports/speech_xml\n  template: speeches.cdata.xml\n  extension: xml\n\nword_frequency: !word_frequency &word_frequency\n  <<: *work_folders\n  filename: riksdagen-corpus-term-frequencies.pkl\n\ndehyphen: !dehyphen &dehyphen\n  <<: *work_folders\n  whitelist_filename: dehyphen_whitelist.txt.gz\n  whitelist_log_filename: dehyphen_whitelist_log.pkl\n  unresolved_filename: dehyphen_unresolved.txt.gz\n\nconfig: !config\n    work_folders: *work_folders\n    parla_clarin: *parla_clarin\n    extract_speeches: *extract_speeches\n    word_frequency: *word_frequency\n    dehyphen: *dehyphen\n    annotated_folder: /data/riksdagen_corpus_data/annotated\n```\n',
    'author': 'Roger Mähler',
    'author_email': 'roger.mahler@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://westac.se',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '==3.8.5',
}


setup(**setup_kwargs)
