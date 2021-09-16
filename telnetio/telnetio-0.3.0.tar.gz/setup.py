# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['telnetio']

package_data = \
{'': ['*']}

extras_require = \
{':python_version == "3.6"': ['dataclasses>=0.8,<0.9'],
 'anyio': ['anyio>=3.2.0,<4.0.0'],
 'anyio:python_version == "3.6"': ['async_generator>=1.10,<2.0']}

setup_kwargs = {
    'name': 'telnetio',
    'version': '0.3.0',
    'description': 'Sans-IO telnet parser',
    'long_description': 'telnetio\n========\n\nA Sans-IO implementation of a telnet parser.\n\nIncludes an `anyio` server implementation.  To install use the `anyio` extra, such as `pip install telnetio[anyio]`.\n\n```python\nimport anyio\nfrom anyio.abc import AnyByteStream\n\nfrom telnetio import AnyioTelnetServer\n\nasync def handler(stream: AnyByteStream) -> None:\n    async with stream, AnyioTelnetServer(stream) as telnet:\n        async for data in telnet:\n            await telnet.send(data)\n\nasync def main() -> None:\n    listener = await anyio.create_tcp_listener(local_port=1234)\n    await listener.serve(handler)\n\nanyio.run(main)\n```\n\nSee the `examples` directory for more examples.\n',
    'author': 'Jordan Speicher',
    'author_email': 'jordan@jspeicher.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/uSpike/telnetio',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
