# -*- coding: utf-8 -*-

import ray

from outflow.core.pipeline import config, context, settings
from outflow.core.pipeline.context_manager import PipelineContextManager
from outflow.ray.add_message_source_info import AddMessageSourceInfo


@ray.remote
def remote_run(run_func, *, pipeline_states, **kwargs):
    init_remote(pipeline_states)
    return run_func(**kwargs)


def set_pipeline_state(*, context_state, config_state, settings_state):
    context.setstate(context_state)
    config.setstate(config_state)
    settings.setstate(settings_state)


def init_remote(pipeline_states):
    PipelineContextManager().__enter__()
    set_pipeline_state(**pipeline_states)

    import logging.handlers

    from outflow.core.logging import set_plugins_loggers_config

    set_plugins_loggers_config()

    logging.config.dictConfig(config["logging"])

    socket_handler = logging.handlers.SocketHandler(
        context.redis_address, context.logger_port
    )
    socket_handler.setLevel(logging.DEBUG)
    socket_handler.addFilter(AddMessageSourceInfo())

    for logger_name in config["logging"].get("loggers", {}):
        if logger_name == "":
            continue
        _logger = logging.getLogger(logger_name)
        # logger.debug(f"adding socket handler {socket_handler} to logger {_logger}")
        _logger.handlers = [socket_handler]
