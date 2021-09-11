# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bareclient', 'bareclient.acgi', 'bareclient.middlewares']

package_data = \
{'': ['*']}

install_requires = \
['baretypes>=3.5,<4.0',
 'bareutils>=3.7,<4.0',
 'h11>=0.12.0,<0.13.0',
 'h2>=4.0,<5.0']

setup_kwargs = {
    'name': 'bareclient',
    'version': '5.0.0a0',
    'description': 'A lightweight asyncio HTTP client',
    'long_description': '# bareClient\n\nA simple asyncio http Python client package supporting HTTP versions 1.0, 1.1\nand 2 (read the [docs](https://rob-blackbourn.github.io/bareClient/)).\n\nThis is the client companion to the ASGI server side web framework\n[bareASGI](https://github.com/rob-blackbourn/bareASGI) and follows the same\n"bare" approach. It makes little attempt to provide any helpful features which\nmight do unnecessary work, providing a foundation for whatever feature set is\nrequired.\n\nIt was written to allow a web server which had negotiated the HTTP/2 protocol\nfor make outgoing HTTP/2 calls. This increases performance and simplifies proxy\nconfiguration in a micro-service architecture.\n\n## Features\n\nThe client has the following notable features:\n\n* Lightweight\n* Uses asyncio\n* Supports HTTP versions 1.0, 1.1, 2\n* Supports middleware\n\n## Installation\n\nThe package can be installed with pip.\n\n```bash\npip install bareclient\n```\n\nThis is a Python3.7 and later package.\n\nIt has dependencies on:\n\n* [bareTypes](https://github.com/rob-blackbourn/bareTypes)\n* [bareUtils](https://github.com/rob-blackbourn/bareUtils)\n* [h11](https://github.com/python-hyper/h11)\n* [h2](https://github.com/python-hyper/hyper-h2)\n\n## Usage\n\nThe basic usage is to create an `HttpClient`.\n\n```python\nimport asyncio\nfrom typing import List, Optional\nfrom bareclient import HttpClient\n\nasync def main(url: str) -> None:\n    async with HttpClient(url, method=\'GET\') as response:\n        if response[\'status_code\'] == 200 and response[\'more_body\']:\n            async for part in response[\'body\']:\n                print(part)\n\nasyncio.run(main(\'https://docs.python.org/3/library/cgi.html\'))\n```\n\nThere is also an `HttpSession` for maintaining session cookies.\n\n```python\n"""Simple GET"""\n\nimport asyncio\nimport json\n\nfrom bareutils import text_reader\nimport bareutils.header as header\nimport bareutils.response_code as response_code\nfrom bareclient import HttpSession\n\n\nasync def main() -> None:\n    """Session example"""\n\n    session = HttpSession(\'https://jsonplaceholder.typicode.com\')\n    async with session.request(\'/users/1/posts\', method=\'GET\') as response:\n        # We expect a session cookie to be sent on the initial request.\n        set_cookie = header.find(b\'set-cookie\', response[\'headers\'])\n        print("Session cookie!" if set_cookie else "No session cookie")\n\n        if not response_code.is_successful(response[\'status_code\']):\n            raise Exception("Failed to get posts")\n\n        posts = json.loads(await text_reader(response[\'body\']))\n        print(f\'We received {len(posts)} posts\')\n\n        for post in posts:\n            path = f\'/posts/{post["id"]}/comments\'\n            print(f\'Requesting comments from "{path}""\')\n            async with session.request(path, method=\'GET\') as response:\n                # As we were sent the session cookie we do not expect to receive\n                # another one, until this one has expired.\n                set_cookie = header.find(b\'set-cookie\', response[\'headers\'])\n                print("Session cookie!" if set_cookie else "No session cookie")\n\n                if not response_code.is_successful(response[\'status_code\']):\n                    raise Exception("Failed to get comments")\n\n                comments = json.loads(await text_reader(response[\'body\']))\n                print(f\'We received {len(comments)} comments\')\n\n\nasyncio.run(main())\n```\n\nFinally there is a single helper function to get json.\n\n```python\nimport asyncio\n\nfrom bareclient import get_json\n\n\nasync def main(url: str) -> None:\n    """Get some JSON"""\n    obj = await get_json(url, headers=[(b\'accept-encoding\', b\'gzip\')])\n    print(obj)\n\n\nasyncio.run(main(\'https://jsonplaceholder.typicode.com/todos/1\'))\n```\n',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rob-blackbourn/bareClient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
