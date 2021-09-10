# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tikzify',
 'tikzify.foundation',
 'tikzify.function_graph',
 'tikzify.function_graph.curve_source',
 'tikzify.node_graph']

package_data = \
{'': ['*']}

install_requires = \
['more_itertools>=8,<9',
 'networkx>=2.5,<3.0',
 'numpy>=1.21,<2.0',
 'tjax>=0.7.11']

setup_kwargs = {
    'name': 'tikzify',
    'version': '0.12.2',
    'description': 'Utilities for programmatically generating TikZ code.',
    'long_description': '=======\nTikzify\n=======\n.. image:: https://badge.fury.io/py/tikzify.svg\n    :target: https://badge.fury.io/py/tikzify\n\n.. role:: bash(code)\n    :language: bash\n\nA set of utilities for programmatically generating TikZ code.\n\nContribution guidelines\n=======================\n\n- Conventions\n\n  - Naming conventions are according to PEP8.\n\n- How to clean the source:\n\n  - :bash:`isort .`\n  - :bash:`pylint tikzify`\n  - :bash:`flake8 tikzify`\n\nRunning\n=======\n\n- This macro is helpful for running examples:\n\n.. code-block:: bash\n\n    function dm {\n        python "$1.py" $2 && pdflatex -shell-escape $1 && open $1.pdf\n    }\n\n- The basal ganglia example can be run by doing :bash:`dm basal_ganglia` from the examples folder.  It should produce :bash:`examples/basal_ganglia.pdf`, which shows all of the output, as well as :bash:`examples/figures/basal_ganglia-*.pdf`, which are the individual diagrams to be included.\n\n- A copy of the `pdf <examples/basal_ganglia.pdf>` is provided.  It shows three programmatically-generated diagrams, with various sections highlighted.\n\nWhom do I talk to?\n==================\n\n- Neil Girdhar\n',
    'author': 'Neil Girdhar',
    'author_email': 'mistersheik@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NeilGirdhar/tikzify',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
