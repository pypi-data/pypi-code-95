# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['basedosdados',
 'basedosdados.cli',
 'basedosdados.download',
 'basedosdados.upload']

package_data = \
{'': ['*'],
 'basedosdados': ['configs/*',
                  'configs/templates/dataset/*',
                  'configs/templates/table/*']}

install_requires = \
['Jinja2==2.11.2',
 'click==7.1.2',
 'google-cloud-bigquery-storage==1.1.0',
 'google-cloud-bigquery==1.28.0',
 'google-cloud-storage==1.31.2',
 'pandas-gbq==0.13.2',
 'pandas==1.2.4',
 'pyaml==20.4.0',
 'ruamel.yaml==0.17.4',
 'tomlkit==0.7.0',
 'tqdm==4.50.2']

entry_points = \
{'console_scripts': ['basedosdados = basedosdados.cli.cli:cli']}

setup_kwargs = {
    'name': 'basedosdados',
    'version': '1.5.7a0',
    'description': 'Organizar e facilitar o acesso a dados brasileiros através de tabelas públicas no BigQuery.',
    'long_description': '# Python Package\n\n## Desenvolvimento\n\n#### Suba o ambiente localmente\n\n```sh\nmake create-env\n. .mais/bin/activate\npython setup.py develop\n```\n\n### Desenvolva uma nova feature\n\n1. Abra uma branch com o nome issue-<X>\n2. Faça as modificações necessárias\n3. Suba o Pull Request apontando para a branch `python-next-minor` ou `python-next-patch`. \n  Sendo, minor e patch referentes ao bump da versão: v1.5.7 --> v\\<major>.\\<minor>.\\<patch>.\n4. O nome do PR deve seguir o padrão\n  `[infra] <titulo explicativo>`\n\n### O que uma modificação precisa ter\n  \n- Resolver o problema\n- Lista de modificações efetuadas\n    1. Mudei a função X para fazer Y\n    2. Troquei o nome da variavel Z\n- Referência aos issues atendidos\n- Documentação e Docstrings\n- Testes\n  \n#### Versionamento\n\nPublique nova versão\n\n```sh\npoetry version [patch|minor|major]\npoetry publish --build\n```\n',
    'author': 'Joao Carabetta',
    'author_email': 'joao.carabetta@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/base-dos-dados/bases',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
