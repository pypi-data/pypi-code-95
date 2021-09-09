import logging
from itertools import cycle

from infiniguard_health.blueprints.components import SystemState
from infiniguard_health.data_collection.loaders import initialize_loaders
from infiniguard_health.health_monitor.exceptions import send_fatal_exception_event
from infiniguard_health.health_monitor.job_order import job_order, all_loaders
from infiniguard_health.health_rules.rules import initialize_rules
from infiniguard_health.jobs.monitor_jobs import run_loaders
from infiniguard_health.message_queue.message_queue_infra import MessageQueue, VALIDATE_NEW_SYSTEM_STATE_MESSAGE
from infiniguard_health.utils import load_iba_mgmt_path

_logger = logging.getLogger(__name__)


def main_loop():
    """
    Receives a list of job runners from the list in jobs_order. Runs jobs given jobs in that order in an endless loop.
    """
    try:
        load_iba_mgmt_path()
        initialize_rules()
        initialize_loaders()

        _logger.info("========Starting Service==========")
        initial_system_state = SystemState()

        _logger.info(
            "Run collection of all data_collection in order to get initial state of the system and validate data")
        run_loaders(initial_system_state, all_loaders)

        # Dispatch message in order to run all rules that perform initial data validation.
        message_queue = MessageQueue()
        message_queue.dispatch_message(VALIDATE_NEW_SYSTEM_STATE_MESSAGE, initial_system_state)

        _logger.info("Finished initial stage. System state has been collected validated.")
        current_system_state = initial_system_state
        for job_runner in cycle(job_order):
            current_system_state = job_runner.run_monitor_jobs(current_system_state, message_queue)

    except BaseException as e:
        _logger.exception(f'infiniguard-health has encountered an unrecoverable exception, and is about to crash. '
                          f'systemd is excepted to restart the service\n')
        send_fatal_exception_event(e)
        raise e
