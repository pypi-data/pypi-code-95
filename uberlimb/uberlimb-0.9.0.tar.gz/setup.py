# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['uberlimb',
 'uberlimb.model',
 'uberlimb.post_fx',
 'uberlimb.post_fx.palette',
 'uberlimb.video']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<1.9.0', 'tqdm>=4.61.2,<5.0.0']

extras_require = \
{':extra == "api"': ['uvicorn[standard]>=0.15.0,<0.16.0',
                     'fastapi>=0.68.1,<0.69.0',
                     'ray[serve]>=1.6.0,<1.7.0'],
 ':extra == "runtime"': ['tensorflow>=2.6,<2.7',
                         'numpy>=1.19,<1.20',
                         'Pillow>=8.3.1,<8.4.0',
                         'scikit-image>=0.18.1,<0.19.0',
                         'Wand>=0.6.6,<0.7.0',
                         'ffmpeg-python>=0.2.0,<0.3.0'],
 ':extra == "streamlit"': ['streamlit>=0.88.0,<0.89.0']}

setup_kwargs = {
    'name': 'uberlimb',
    'version': '0.9.0',
    'description': 'Generative art with CPPN networks.',
    'long_description': '# ÜberLimb\n\nGenerative art with CPPN networks.\n\n# Get started\nInstall package with `pip install uberlimb[runtime]`\n\n```python\nfrom uberlimb.renderer import Renderer\nfrom uberlimb.parameters import RendererParams\n\nrenderer = Renderer(RendererParams())\nrenderer.render_frame().as_pillow().show()\n```\n\nExpected output:\n\n![](https://cai-misc.s3.eu-central-1.amazonaws.com/uberlimb/uberlimb_splash.png)\n\n# TODO\n- [ ] video pipeline\n- [ ] color schemes, both predefined and custom (will require varying\n  the number of output channels)',
    'author': 'Vladimir Sotnikov',
    'author_email': 'vladimir.sotnikov@jetbrains.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://cai.jetbrains.com',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
