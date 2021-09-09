import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from infiniguard_health.event_engine.event_engine_infra import EventEngine
from infiniguard_health.system_state_read_write import write_system_state_to_file
from infiniguard_health.data_collection.loaders import loaders_dict

_logger = logging.getLogger(__name__)


def run_loaders(new_system_state, source_loaders_ids):
    """
    Runs the given collectors in parallel (using threads) and fills the data of the given SystemState accordingly.
    :param new_system_state:
    :param source_loaders_ids:
    :return:
    """
    _logger.debug(f"Preparing to run source collectors {source_loaders_ids}")
    with ThreadPoolExecutor(max_workers=len(source_loaders_ids)) as executor:
        futures = []
        for source_loader_id in source_loaders_ids:
            _logger.debug(f"Running {source_loader_id} as independent thread")
            # Each source_loader is expected to modify some part of the new_system_state with updated information.
            source_loader = loaders_dict[source_loader_id]
            futures.append(executor.submit(source_loader, new_system_state))

        for future in as_completed(futures):
            future.result()  # Allows throwing exceptions that were generated in the threads


def monitor_job(old_system_state, source_loaders_ids, message_queue):
    """
    The monitor job performs the entire task of collecting data from given data_collection, updating the overall system state
    and alerting if there is any change that requires user attention.
    :param old_system_state: SystemState object which holds all the current Components objects of the system
    :param source_loaders_ids: List of ids of source collectors (as strings).
    :param message_queue the MessageQueue object containing all health_rules subscribed to component-changed messages.
    :return: An updated system_state object.
    """
    _logger.info("Starting monitor job")
    _logger.debug("Creating copy of system state for future comparison")
    new_system_state = copy.deepcopy(old_system_state)

    new_system_state.reset_data_collection_cycle()
    run_loaders(new_system_state, source_loaders_ids)

    _logger.info("All source collection threads have completed successfully")
    write_system_state_to_file(new_system_state)

    _logger.debug("Comparing new system state's data with previous state")
    differences = new_system_state.difference(old_system_state)

    # Note - Messages will be dispatched here according to the Component priority value.
    if differences:
        for new_component, old_component in differences:
            _logger.debug(f"Dispatching message {new_component.component_change_message}")
            message_queue.dispatch_message(new_component.component_change_message, new_system_state, old_system_state)

    EventEngine().resolve_and_emit_infinibox_events()
    _logger.info(f"Finished running monitor job of data_collection {source_loaders_ids}")

    _logger.info("Computing new states for components and entire system")
    new_system_state.compute_state()

    return new_system_state
