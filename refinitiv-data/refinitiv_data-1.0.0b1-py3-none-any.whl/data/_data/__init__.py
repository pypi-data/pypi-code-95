from .. import __version__
from . import configure
from . import log


from .errors import *
from .core import *  # noqa
from .content import *  # noqa
from .delivery import *  # noqa
from .factory import *  # noqa
from .pricing import *  # noqa
from .content import ipa  # noqa
from .content import search
from . import fin_coder_layer

del get_chain_async
del get_headlines
del get_headlines_async
del get_story
del get_story_async
del News
del State
del Lock
del endpoint_request

import sys

logger = log.root_logger
logger.debug(f"RD version is {__version__}; Python version is {sys.version}")

try:
    import pkg_resources

    installed_packages = pkg_resources.working_set
    installed_packages = sorted([f"{i.key}=={i.version}" for i in installed_packages])
    logger.debug(
        f"Installed packages ({len(installed_packages)}): {','.join(installed_packages)}"
    )
except Exception as e:
    logger.debug(f"Cannot log installed packages, {e}")

logger.debug(f'Read configs: {", ".join(configure._config_files_paths)}')
