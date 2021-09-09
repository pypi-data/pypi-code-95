# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eals']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.0.1,<2.0.0', 'numba>=0.53.1,<0.54.0', 'scipy>=1.5.4,<2.0.0']

setup_kwargs = {
    'name': 'eals',
    'version': '0.9.3',
    'description': 'eALS - Element-wise Alternating Least Squares',
    'long_description': '# eALS - Element-wise Alternating Least Squares\n\nA Python implementation of the element-wise alternating least squares (eALS) for fast online matrix factorization proposed by [arXiv:1708.05024](https://arxiv.org/abs/1708.05024).\n\n## Prerequisites\n\n- Python >= 3.8\n\n## Installation\n\n```sh\npip install eals\n```\n\n## Usage\n\n```python\nimport numpy as np\nimport scipy.sparse as sps\nfrom eals import ElementwiseAlternatingLeastSquares, load_model\n\n# batch training\nuser_items = sps.csr_matrix([[1, 2, 0, 0], [0, 3, 1, 0], [0, 4, 0, 4]], dtype=np.float32)\nmodel = ElementwiseAlternatingLeastSquares(factors=2)\nmodel.fit(user_items)\n\n# learned latent vectors\nmodel.user_factors\nmodel.item_factors\n\n# online training for new data (user_id, item_id)\nmodel.update_model(1, 0)\n\n# rating matrix and latent vectors will be expanded for a new user or item\nmodel.update_model(0, 5)\n\n# current rating matrix\nmodel.user_items\n\n# save and load the model\nmodel.save("model.joblib")\nmodel = load_model("model.joblib")\n```\n\nSee the [examples](examples/) directory for complete examples.\n\n## Development\n\n### Setup development environment\n\n```sh\ngit clone https://github.com/newspicks/eals.git\ncd eals\npoetry run pip install -U pip\npoetry install\n```\n\n### Tests\n\n```sh\npoetry run pytest\n```\n\nSet `USE_NUMBA=0` for faster testing without numba JIT overhead.\n\n```sh\nUSE_NUMBA=0 poetry run pytest\n```\n\nTo run tests against all supported Python versions, use [tox](https://tox.readthedocs.io/).\nYou may need to put the Python version numbers in the `.python-version` file.\n\n```sh\npoetry run tox\n```\n',
    'author': 'Akira Kitauchi',
    'author_email': 'kitauchi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/newspicks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
