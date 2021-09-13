import argparse

from frase.api.main import Server
from frase.api.appbuilder import BuildServerApp


def api(args):
    s = Server()

    options = {
        'bind': "{}:{}".format(args.host, args.port),
        'workers': args.workers,
        'timeout': args.timeout
    }

    BuildServerApp(s.app, options).run()


def execute():
    parser = argparse.ArgumentParser(prog="frase_api", description='Frase API')

    subparsers = parser.add_subparsers(help='sub-command help')

    api_parser = subparsers.add_parser('api', help='API server')
    api_parser.add_argument("-a", "--host", type=str, default="127.0.0.1", help='Bind address')
    api_parser.add_argument("-p", "--port", type=str, default="8080", help='Bind port')
    api_parser.add_argument("-w", "--workers", type=int, default=1, help='Number of workers')
    api_parser.add_argument("-t", "--timeout", type=int, default=300, help='Timeout value')
    api_parser.set_defaults(func=api)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    execute()
