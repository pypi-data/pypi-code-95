# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['srtools']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'srtools',
    'version': '0.1.10',
    'description': 'Serbian language Cyrillic ↔ Latin transliteration tools',
    'long_description': '#######\nsrtools\n#######\n\n.. image:: https://gitlab.com/andrejr/srtools/badges/master/pipeline.svg\n   :alt: pipeline status\n   :target: https://gitlab.com/andrejr/srtools/pipelines\n.. image:: https://gitlab.com/andrejr/srtools/badges/master/coverage.svg\n   :alt: coverage report\n   :target: https://andrejr.gitlab.io/srtools/coverage/index.html\n\nSrtools provides a CLI utility (``srts``) and a Python 3 (``^3.7``) package \nthat helps you transliterate Serbian texts between Cyrillic and Latin.\n\nHere\'s a demonstration of the CLI utility:\n\n.. code-block:: console\n\n   $ echo "Đače, uštedu plaćaj žaljenjem zbog džinovskih cifara." | srts --lc\n   Ђаче, уштеду плаћај жаљењем због џиновских цифара.\n   $ echo "Ђаче, уштеду плаћај жаљењем због џиновских цифара." | srts --cl\n   Đače, uštedu plaćaj žaljenjem zbog džinovskih cifara.\n\nHere\'s how you use the Python package:\n\n.. code-block:: python\n\n   from srtools import cyrillic_to_latin, latin_to_cyrillic\n\n   assert (\n       latin_to_cyrillic("Đače, uštedu plaćaj žaljenjem zbog džinovskih cifara.")\n       == "Ђаче, уштеду плаћај жаљењем због џиновских цифара."\n   )\n\n   assert (\n       cyrillic_to_latin("Ђаче, уштеду плаћај жаљењем због џиновских цифара.")\n       == "Đače, uštedu plaćaj žaljenjem zbog džinovskih cifara."\n   )\n\n\nMotivation\n==========\n\nI needed a simple commandline utility I can use to pipe in some text and change\nits script.\n\nI also use this tool to transliterate strings in Serbian LaTeX localization \npackages. That way I don\'t have to maintain individual sets of localization \nstrings for Cyrillic and Latin.\n\nDocumentation\n=============\n\nDocumentation (Sphinx) can be viewed on\n`GitLab pages for this package <https://andrejr.gitlab.io/srtools/>`_.\n\nChangelog\n=========\n\nThe changelog can be found within the documentation, \n`here <https://andrejr.gitlab.io/srtools/changes.html>`_.\n',
    'author': 'Andrej Radović',
    'author_email': 'r.andrej@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/andrejr/srtools',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
