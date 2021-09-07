# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aucampia', 'aucampia.rdflib_xtl']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'click-option-group>=0.5.3,<0.6.0',
 'click>=8.0.1,<9.0.0',
 'owlrl>=5.2.1,<6.0.0',
 'pyyaml>=5.3.1,<6.0.0',
 'rdflib-jsonld>=0.5.0,<0.6.0',
 'rdflib>=5.0.0,<6.0.0',
 'requests>=2.26.0,<3.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['rdflib-xtl = aucampia.rdflib_xtl.cli:main']}

setup_kwargs = {
    'name': 'aucampia.rdflib-xtl',
    'version': '0.5.0',
    'description': 'Extra tools for rdflib',
    'long_description': "# Extra command line tools for rdflib\n\nThis package provides some additional command line tools for rdflib:\n\n* SPARQL Query execution with optional reasoning using [OWL-RL](https://github.com/RDFLib/OWL-RL):\n    ```bash\n    rdflib-xtl sparql --help\n    ```\n* OWL Reasoning using [OWL-RL](https://github.com/RDFLib/OWL-RL)\n    ```bash\n    rdflib-xtl reason --help\n    ```\n\nUsage examples:\n\n```bash\n# Install pipx\npip3 install --user --upgrade pipx\n\n# (optionally) clear pipx cache if you want the latest version ...\n\\rm -vr ~/.local/pipx/.cache/\n\n# check version\npipx run --spec yocho.rdflib-xtl rdflib-xtl --version\n\n# Run SPARQL without reasoning ...\npipx run --spec yocho.rdflib-xtl \\\n  rdflib-xtl sparql \\\n  -q 'SELECT * WHERE { ?s rdfs:subClassOf owl:Thing. }' \\\n  http://xmlns.com/foaf/spec/index.rdf\n\n# Dump input graph with SPARQL query ...\npipx run --spec yocho.rdflib-xtl \\\n  rdflib-xtl sparql \\\n  -q 'CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }' \\\n  http://xmlns.com/foaf/spec/index.rdf\n\n# Run SPARQL with reasoning ...\npipx run --spec yocho.rdflib-xtl \\\n  rdflib-xtl sparql --reason \\\n  -q 'SELECT * WHERE { ?s rdfs:subClassOf owl:Thing. }' \\\n  http://xmlns.com/foaf/spec/index.rdf\n\n# Dump reasoned graph with SPARQL query ...\npipx run --spec yocho.rdflib-xtl \\\n  rdflib-xtl sparql --reason \\\n  -q 'CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }' \\\n  http://xmlns.com/foaf/spec/index.rdf\n\n# Run reasoning ...\npipx run --spec yocho.rdflib-xtl \\\n  rdflib-xtl reason http://xmlns.com/foaf/spec/index.rdf\n```\n",
    'author': 'Iwan Aucamp',
    'author_email': 'aucampia@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/aucampia/project/rdflib-xtl',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
