import argparse
import logging
from arkive import __version__
from pathlib import Path


def cli() -> argparse.Namespace:
    cloud = argparse.ArgumentParser(add_help=False)

    cloud.add_argument('-c', '--cloud', type=str, metavar='SERVICE', choices=['pcloud'])

    auth = cloud.add_argument_group('authentication')
    auth.add_argument('-t', '--token', type=str)
    auth.add_argument('-u', '--username', type=str)
    auth.add_argument('-p', '--password', type=str)

    cloud.add_argument("-v", "--verbosity", action="count", help="increase output verbosity", default=0)

    parser = argparse.ArgumentParser(prog='arkive')

    commands = parser.add_subparsers(dest='cmd', title='commands')

    show = commands.add_parser('show', parents=[cloud], help='display actions collection inside a given folder.')
    show.add_argument('folder', type=Path)

    flat = commands.add_parser('flat', parents=[cloud], help='flatten actions files inside a given folder.')
    flat.add_argument('folder', type=Path)
    flat.add_argument('-o', '--output', type=Path)

    nest = commands.add_parser('nest', parents=[cloud], help='nesting actions files inside a given folder.')
    nest.add_argument('folder', type=Path)
    nest.add_argument('-o', '--output', type=Path)

    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}')

    return parser.parse_args()


def create_drive(service: str, auth: dict):
    if service == 'pcloud':
        from arkive.drives.pcloud import PCloudDrive
        return PCloudDrive(auth)

    from arkive.drives.local import LocalDrive
    return LocalDrive()


def music_show(folder: Path, cloud: str = None, auth: dict = None):
    from arkive.actions.show import show_music_collection
    from arkive.utility.table import make_table

    drive = create_drive(cloud, auth)
    header, content = show_music_collection(drive, folder)
    table = make_table(header, content)
    print(table)


def music_flat(folder: Path, output: Path = None, cloud: str = None, auth: dict = None):
    from arkive.actions.flat import flat_music_collection

    if not output:
        output = folder

    drive = create_drive(cloud, auth)
    flat_music_collection(drive, folder, output)


def music_nest(folder: Path, output: Path = None, cloud: str = None, auth: dict = None):
    from arkive.actions.nest import nest_music_collection

    if not output:
        output = folder

    drive = create_drive(cloud, auth)
    nest_music_collection(drive, folder, output)


def main():
    args = cli()

    logging.basicConfig(level=logging.ERROR)
    if "verbosity" in args:
        if args.verbosity >= 3:
            logging.basicConfig(level=logging.DEBUG)
        elif args.verbosity == 2:
            logging.basicConfig(level=logging.INFO)
        elif args.verbosity == 1:
            logging.basicConfig(level=logging.WARNING)

    auth = {}
    if args.cmd and args.cloud:
        if args.token:
            auth = {'auth': args.token}
        elif args.username and args.password:
            auth = {'username': args.username, 'password': args.password}

    if args.cmd == 'show':
        music_show(args.folder, args.cloud, auth)
    elif args.cmd == 'flat':
        music_flat(args.folder, args.output, args.cloud, auth)
    elif args.cmd == 'nest':
        music_nest(args.folder, args.output, args.cloud, auth)


if __name__ == '__main__':
    main()
