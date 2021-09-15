import logging
import os
import time
from logstash_async.handler import AsynchronousLogstashHandler


logger = logging.getLogger(config["name"])


def init_logger(config):
    logger = logging.getLogger(config["name"])
    logger.setLevel(logging.INFO)
    if config["host"] == "HOST":
        config["host"] = os.environ["HOST"]
    logger.addHandler(AsynchronousLogstashHandler(
        config["host"],
        config["port"],
        None
    ))
    logger.info(f"Started {config['name']}", extra={
        "log_event": "system started"
    })


def process_log(name):
    def ultra_wrapper(func):
        def wrapper(data):
            s = time.time()
            input_str = str(data)
            try:
                result = func(data)
                logger.info(f"Processed {name}", extra={
                    "log_event": f"{name}",
                    "user_id": data["user_id"],
                    "process_input": input_str,
                    "process_output": str(result),
                    "time": time.time() - s
                })
                return result
            except Exception as e:
                logger.error(f"Processed {name}", extra={
                    "log_event": f"{name} failed",
                    "user_id": data["user_id"],
                    "process_input": input_str,
                    "process_output": e,
                    "time": time.time() - s
                })
                raise e
        return wrapper
    return ultra_wrapper
