

import os
import logging
import sys
from loguru import logger

from uvicorn import Config, Server
from fastapi.staticfiles import StaticFiles


LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO"))
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    logger.configure(handlers=[{"sink": sys.stdout, "serialize": JSON_LOGS}])
    logger.add("/var/log/ebs/netconfig.log", level="INFO",
               rotation="1 week", retention="14 days")


from ebs.linuxnode.netconfig.core import api_app
from ebs.linuxnode.netconfig.core import app


def build_server():
    from ebs.linuxnode.netconfig.core import auth_router
    api_app.include_router(auth_router)
    from ebs.linuxnode.netconfig.wifi import wifi_router
    api_app.include_router(wifi_router)
    static_files_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    app.mount('/api', api_app)
    app.mount('/', StaticFiles(directory=static_files_path, html=True), name="static")


build_server()


def run_server():
    server = Server(
        Config(
            "ebs.linuxnode.netconfig.server:app",
            host="0.0.0.0",
            port=8039,
            log_level=LOG_LEVEL,
        ),
    )
    # setup logging last, to make sure no library overwrites it
    # (they shouldn't, but it happens)
    setup_logging()
    server.run()


if __name__ == '__main__':
    run_server()
