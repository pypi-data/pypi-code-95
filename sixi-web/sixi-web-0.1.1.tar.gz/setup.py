# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sixi_web']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'WebOb>=1.8.7,<2.0.0',
 'parse>=1.19.0,<2.0.0',
 'requests-wsgi-adapter>=0.4.1,<0.5.0',
 'requests>=2.26.0,<3.0.0',
 'whitenoise>=5.3.0,<6.0.0']

setup_kwargs = {
    'name': 'sixi-web',
    'version': '0.1.1',
    'description': 'A simple web framework built for learning purpose.',
    'long_description': '# sixi-web [![CI](https://github.com/kadaliao/sixi-web/actions/workflows/main-ci.yml/badge.svg?branch=main)](https://github.com/kadaliao/sixi-web/actions/workflows/main-ci.yml)\n\nA simple web framework built for learning purpose.\n\n\n## Installation\n\n```sh\npip install sixi-web\n```\n\n<!-- USAGE EXAMPLES -->\n## Usage\n\n1. Import the Sixi web api instance to route. If you’ve used Flask before, you\'ll find it easy.\n\n    ```python\n    # app.py\n\n    from sixi_web import API, Middleware\n\n    app = API(templates_dir="templates", static_dir="static")\n\n\n    @app.route("/")\n    @app.route("/home")\n    def index(req, resp):\n        resp.text = "Hello world"\n\n\n    @app.route("/about")\n    def about(req, resp):\n        resp.text = "A vegetable dog passing by."\n\n\n    @app.route("/hello/{name}")\n    def hello(req, resp, name):\n        resp.text = f"Hello, {name}"\n\n\n    @app.route("/add/{a:d}/{b:d}")\n    def add(req, resp, a, b):\n        result = int(a) + int(b)\n        resp.text = f"{a} + {b} = {result}"\n\n\n    @app.route("/todo")\n    class TodoResource:\n        def get(self, req, resp):\n            resp.text = "Get a task"\n\n        def post(self, req, resp):\n            resp.text = "Create a task"\n\n\n    @app.route("/html")\n    def html(req, resp):\n        resp.html = app.template("index.html", context=dict(title="hi", name="kada"))\n\n\n    @app.route("/text")\n    def text(req, resp):\n        resp.text = "This is plain text"\n\n\n    @app.route("/json")\n    def json(req, resp):\n        resp.json = dict(content="this is json")\n\n\n    @app.error_handler(AttributeError)\n    def attributeerror_handler(req, resp, e):\n        resp.text = f"I got it, {e}"\n\n\n    class PrintingMiddleware(Middleware):\n        def process_request(self, req):\n            print(f"request: {req}\\n\\n")\n\n        def process_response(self, req, resp):\n            print(f"response: {resp}\\n\\n")\n\n\n    app.add_middleware(PrintingMiddleware)\n    ```\n\n2. Run with any WSGI application server such as Gunicorn.\n\n\n    ```sh\n    gunicorn app:app\n    ```\n\n\n<!-- ROADMAP -->\n## Roadmap\n\n\n- <del>Request handler</del>\n- <del>Routing</del>\n- <del>Class based view</del>\n- <del>Unit tests</del>\n- <del>CI</del>\n- CD\n- <del>Template support</del>\n- <del>Custom exception handler</del>\n- <del>Static files serving</del>\n- <del>Middleware</del>\n- <del>Custom response</del>\n- <del>Pypi</del>\n- Authentication\n- Demo app\n- ORM\n- Cli\n- Session and Cookies\n\n<!-- CONTRIBUTING -->\n## Contributing\n\nAny contributions you make are **greatly appreciated**.\n\n1. Fork the Project\n2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)\n3. Commit your Changes (`git commit -m \'Add some AmazingFeature\'`)\n4. Push to the Branch (`git push origin feature/AmazingFeature`)\n5. Open a Pull Request\n\n\n\n<!-- LICENSE -->\n## License\n\nDistributed under the MIT License. See `LICENSE` for more information.\n',
    'author': 'Kada Liao',
    'author_email': 'kadaliao@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kadaliao/sixi-web',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
