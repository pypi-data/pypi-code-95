import logging
from pprint import pformat

from .models.cli import CLI
from .models.inputs import Inputs
from .services.finders import gather_collections
from .services.introspection import introspect_state
from .services.logging import init_root_logger
from .services.mutations import generate_collections
from .utils.strings.formatters import notice
from .utils.strings.literals import (APPLYING_MUTATIONS, GATHERING_COLLECTIONS,
                                     INTROSPECTING_STATE, PLUG,
                                     RECEIVED_INPUTS, TITLE)

logger = logging.getLogger(__file__)


def main() -> None:
    cli = CLI.parse()
    inputs = Inputs.parse(cli)

    init_root_logger(inputs.flags.loglevel)
    logger.debug("Initialized logger at level %s.", inputs.flags.loglevel)

    logger.info(TITLE)
    logger.info(RECEIVED_INPUTS)

    logger.debug("Settings: %s", pformat(inputs.settings.__dict__))
    logger.debug("Flags: %s", pformat(inputs.flags.__dict__))

    logger.info(GATHERING_COLLECTIONS)
    collections = gather_collections(inputs.settings)

    for collection in collections:
        logger.debug(pformat(collection.__dict__))

    logger.info(INTROSPECTING_STATE)
    introspect_state(inputs.settings, collections)

    logger.info(APPLYING_MUTATIONS)
    generate_collections(inputs, collections)

    logger.info(notice("Completed successfully."))
    logger.info(notice("Congratulations!"))

    logger.info(PLUG)


if __name__ == "__main__":
    main()
