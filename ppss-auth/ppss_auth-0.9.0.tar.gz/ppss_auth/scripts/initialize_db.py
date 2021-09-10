import argparse
import sys,os
import configparser
import transaction

from .. import models

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

import logging
l = logging.getLogger('ppssauth.scripts')


from . alchemyutils import (
    get_engine,
    get_session_factory,
    get_tm_session
)


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config_uri',
        help='Configuration file, e.g., development.ini',
    )
    return parser.parse_args(argv[1:])

here = "../"
def main(argv=sys.argv):
    from ppss_auth import __path__
    here = os.path.join(str(__path__[0]),"..")
    config_uri = os.path.join(here,"alembic.ini")

    setup_logging(config_uri)

    config = configparser.ConfigParser()
    config.read(config_uri)
    config["alembic"]["here"] = here
    settings = config

    engine = get_engine(settings)
    session_factory = get_session_factory(engine)
    print ("got engine and session factory")
    models.Base.metadata.create_all( engine )
    print ("created")
