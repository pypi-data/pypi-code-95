import argparse
from urllib.parse import urlparse

from structlog import get_logger

log = get_logger()


def install(args):
    # pylint:disable=C0415
    from .proto_handler import PyProtoHandler
    if args.all:
        PyProtoHandler.install_handler_global()
    else:
        PyProtoHandler.install_handler_user()


def open_url(args):
    log.info("Opening gnista url", url=args.url)
    parsed_url = urlparse(args.url)
    gnista_id = parsed_url.netloc
    log.info("Detected DataPointId", data_point_id=gnista_id)
    client = parsed_url.query.split("=")[1]
    if client == "visplore":
        log.info("Detected Visplore as client")
        # pylint:disable=C0415
        from .visplore_import import VisploreImport

        VisploreImport.start_import(gnista_id=gnista_id)
    else:
        log.error("Client not supported", client=client)
        raise Exception("Type " + client + " not supported")


def main():
    parser = argparse.ArgumentParser(prog="PROG")
    subparsers = parser.add_subparsers(help="actions")

    parser_a = subparsers.add_parser(
        "install", help="install url handler", aliases=["i"]
    )
    parser_a.add_argument(
        "-a", "--all", help="install for all users", action="store_true"
    )
    parser_a.set_defaults(func=install)

    parser_b = subparsers.add_parser(
        "open", help="open a gnista datapoint", aliases=["o"]
    )
    parser_b.add_argument("url", metavar="{url}", type=str, help="url to open")
    parser_b.set_defaults(func=open_url)
    try:
        args = parser.parse_args()
        if args.func is None:
            parser.print_help()
    # pylint:disable=W0703
    except Exception:
        parser.print_help()

    try:
        args.func(args)
    # pylint:disable=W0703
    except Exception as ex:
        log.critical("Excepton has been thrown", ex=ex, exc_info=True)
