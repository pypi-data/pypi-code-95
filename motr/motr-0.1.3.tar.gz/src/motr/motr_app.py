from cement import App
from cement import init_defaults

import motr.controllers.base

# configuration defaults
CONFIG = init_defaults("motr")
CONFIG["motr"]["foo"] = "bar"


class MOTR(App):
    """Max's Obvious Task Runner primary application."""

    class Meta:
        label = "motr"

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            "yaml",
            "colorlog",
            "jinja2",
            "motr.ext.ext_maybe_fmt",
        ]

        # configuration handler
        config_handler = "yaml"

        # configuration file suffix
        config_file_suffix = ".yml"

        # set the log handler
        log_handler = "colorlog"

        # set the output handler
        output_handler = "jinja2"

        # register handlers
        handlers = [motr.controllers.base.Base]
