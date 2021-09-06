import click
import configparser
import atrhub
import sys
from os.path import expanduser

DEFAULT_CONFIG_PATHS = [
    expanduser("~"),
    '/etc',
]
DEFAULT_CONFIG_FILE = "atrhub.ini"
_DEFAULT_CONFIG = [
    "{}/{}".format(str(a_path), DEFAULT_CONFIG_FILE) for a_path in DEFAULT_CONFIG_PATHS[::-1]
]

@click.command()
@click.option('--config', type=click.File('rb'), help='Provided configuration is not reachable')
@click.option('--path', type=click.Path())
def main(path, config):
    config_name = None
    if config:
        config_name = config.name

    result, _ = process_path(path, config_name)

    if not result:
        sys.exit(1)
    return result


def process_path(path=None, config=None):
    if not path:
        try:
            settings = configparser.ConfigParser()
            config_files_list = _DEFAULT_CONFIG
            if config:
                config_files_list = _DEFAULT_CONFIG + [config]
            settings.read(config_files_list)
            basedir = str(settings.get('DEFAULT', 'BASE_DIR'))
        except Exception as e:
            print (e)
            basedir = '/home/atrhub'

    else:
        basedir = path

    # Review global_log
    try:
        global_log = str(settings.get('DEFAULT', 'GLOBAL_LOG'))
    except Exception as e:
        print (e)
        global_log = '/home/atrhub/atrhub.log'

    try:
        atr_files = atrhub.ATRFiles(path=basedir, global_log=global_log)
        result = atr_files.deliver()
    except Exception as e:
        print (e)
        result = False

    return result, basedir


if __name__ == '__main__':
    main()
