# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reactant', 'reactant.orm']

package_data = \
{'': ['*'], 'reactant': ['templates/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'black>=21.8b0,<22.0',
 'click>=8.0.1,<9.0.0',
 'pydantic>=1.8.2,<2.0.0']

entry_points = \
{'console_scripts': ['reactant = reactant.run:runner']}

setup_kwargs = {
    'name': 'reactant',
    'version': '0.2.1',
    'description': 'Generate code for models, views, and urls based on Python type annotations.',
    'long_description': '<p align="center">\n    <a href="https://pypi.org/project/reactant">\n        <img width="1200" src="https://raw.githubusercontent.com/neil-vqa/reactant/main/reactant-logo-banner.png">\n    </a>\n</p>\n\nGenerate code for *models, views, and urls* based on Python type annotations. Powered by [pydantic](https://github.com/samuelcolvin/pydantic/). Influenced by [SQLModel](https://github.com/tiangolo/sqlmodel).\n\n*reactant* aims to give usable and sensible code defaults. It does **not enforce** a particular application structure. Instead, it follows the default/minimal/common structure of the supported frameworks, and it is up to the developer to make use of the generated code to fit it to their application. Contributions are warmly welcomed if you believe a particular structure is widely used and can benefit from code generation.\n\n## Supported Frameworks\n\n*reactant* currently generates code for the following:\n\n**Django REST** (in Django\'s *default* project structure i.e. by *apps*)\n\n- [X] models\n- [X] views (class-based API views, filename=*views_class.py*)\n- [ ] views (function-based API views, filename=*views_function.py*)\n- [X] serializers\n- [X] urls (from class-based API views, filename=*urls_class.py*)\n- [ ] urls (from function-based API views, filename=*urls_function.py*)\n\n**Flask**\n\n- [ ] models (Flask-SQLAlchemy)\n\n**SQLAlchemy**\n\n- [ ] models in Declarative Mapping\n\n**Peewee**\n\n- [X] models\n\n## Installation\n\n```cli\n$ pip install reactant\n```\n\n## Get Started\n\nCreate *reactant* models by inheriting from `Reactant` , and from another auxiliary class: `DjangoORM`, `SQLAlchemyORM`, `PeeweeORM`. The example below uses `DjangoORM`. Your choice of ORM will determine what code and files will be generated.\n\n```python\n# generate.py\n\nfrom typing import Optional\nfrom reactant import Reactant, DjangoORM, Field, generate\n\n\nclass RocketEngine(Reactant, DjangoORM):\n    name: str = Field(max_length=32, title="engine_name")\n    manufacturer: str = Field(max_length=64)\n    power_cycle: Optional[str] = Field("gas-generator", blank=True, max_length=32)\n    thrust_weight_ratio: Optional[int] = None\n\n\nclass LaunchVehicle(Reactant, DjangoORM):\n    name: str = Field(max_length=32)\n    country: str = Field(blank=True, max_length=32)\n    status: str\n    total_launches: Optional[int]\n    engine: str = Field(foreign_key="RocketEngine")\n\n# Don\'t forget this block.\nif __name__ == "__main__":\n    generate()\n\n```\n\nDon\'t forget `generate()`. Run the code. \n\n```cli\n$ reactant generate.py\n\nRunning generate.py\nFound 2 Django reactants.\nDjango models.py finished rendering.\nDjango views_class.py finished rendering.\nDjango serializers.py finished rendering.\nDjango urls_class.py finished rendering.\nSuccess! Please check "reactant_products" directory.\n```\n\n**BOOM!** With just the above code, the models, views, serializers, and urls (the *products*, for Django atleast) are generated. See images of the code below.\n\n## Sample Code Generated\n\n### Django REST\n\n<section>\n    <div style="display:flex;">\n        <div>\n            <img src="https://raw.githubusercontent.com/neil-vqa/reactant/main/screenshots/dj_01.png" width="auto">\n        </div>\n        <div>\n            <img src="https://raw.githubusercontent.com/neil-vqa/reactant/main/screenshots/dj_02.png" width="auto">\n        </div>\n    </div>\n    <div style="display:flex; height:auto;">\n        <div>\n            <img src="https://raw.githubusercontent.com/neil-vqa/reactant/main/screenshots/dj_03.png" width="auto">\n        </div>\n        <div>\n            <img src="https://raw.githubusercontent.com/neil-vqa/reactant/main/screenshots/dj_04.png" width="auto">\n        </div>\n    </div>\n</section>\n\n## Development\n\nThe project uses Poetry to package and manage dependencies.\n\n```cli\n(venv)$ poetry install\n```\n\nRun tests.\n```cli\npytest\n```\n\n## License\n\nMIT License. For more information and legal terms, see the LICENSE file.\n',
    'author': 'Neil Van',
    'author_email': 'nvq.alino@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
