import argparse
import json

from infiniguard_health.cli_tools.config import health_check_configurations
from infiniguard_health.system_state_read_write import read_system_state_from_file_as_native_object, \
    is_latest_system_health_state_stale, JSON_FILE_NAME
from infiniguard_health.cli_tools.json_printer import print_faulty_components, print_system_layout
from infiniguard_health.data_collection.sources import service_status


def get_all_cli_tags():
    tags = []
    for health_check_configuration in health_check_configurations:
        tags.extend(health_check_configuration.tags)

    return list(set(tags))


def get_health_check_configurations(check_tags):
    """
    Returns all check configurations that are associated with the given tags (as defined in the config file)
    """
    return [health_check for health_check in health_check_configurations
            if set(health_check.tags).intersection(set(check_tags))]


def run_health_checks(selected_health_check_configurations, path=JSON_FILE_NAME):
    """
    Runs health check functions, as appear in each given check configuration.
    Each such check function can either pass or fail.
    If any check fails, returns (False, dict mapping failed check descriptions to failure description).
    If all checks succeed, returns (True, None).
    """
    try:
        system_state = read_system_state_from_file_as_native_object(path=path)
    except Exception:
        return False, 'Failed to load system state from file.'

    failed_checks_to_failure_description = {}
    for check_configuration in selected_health_check_configurations:
        check_result, failure_description = check_configuration.check_function(system_state)
        if not check_result:
            failed_checks_to_failure_description[check_configuration.check_description] = failure_description

    if failed_checks_to_failure_description:
        return False, failed_checks_to_failure_description

    else:
        return True, None


def get_string_of_check_descriptions(failover_health_check_configurations):
    passed_checks_descriptions = '\n * ' + '\n * '.join([check.check_description
                                                        for check in failover_health_check_configurations])
    return f"The following checks completed successfully:\n {passed_checks_descriptions}"


def is_infiniguard_health_running():
    return service_status('infiniguard-health.service') == 'active'


def _run_cli(tags):
    if not is_infiniguard_health_running():
        print(f"Infiniguard Health service is not running")
        exit(1)

    if is_latest_system_health_state_stale():
        print(f'Latest system state {JSON_FILE_NAME} is stale.')
        exit(1)

    selected_health_check_configurations = get_health_check_configurations(tags)
    all_checks_passed, failed_checks_to_failure_description = run_health_checks(selected_health_check_configurations)

    if all_checks_passed:
        print(get_string_of_check_descriptions(selected_health_check_configurations))
    else:
        print(json.dumps(failed_checks_to_failure_description))
        exit(1)


def run_regular_cli():
    """
    The CLI tool runs a subset of the checks defined in health_checks.py.
    If all checks pass correctly, ends successfully (logging the checks that were run).
    If any check fails, end with exit code 1, and returns a JSON of the checks that failed, along with their failure
    description, as given by the check function.

    The file config.py assigns tags to the various checks. Thus, the tag arguments passed to the CLI tool determine the
    checks that are to be run.

    Note that the health checks only read the data existing in the JSON file created by the health
    monitor.
    The check then makes a decision if the check has passed or not (e.g do all volumes have multipath connectivity).
    """
    description = "CLI tool for running checks based on the data collected by the health monitor. " \
                  "If all checks pass, the CLI tool finishes successfully. If not, error code 1 is " \
                  "returned."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('tags', nargs='+', choices=get_all_cli_tags(),
                        help='Tags of health checks for the CLI to run.')
    args = parser.parse_args()
    tags = args.__dict__['tags']

    _run_cli(tags)


def run_failover_cli():
    """
    Specialized CLI tool that only runs the 'failover' tag. For use by the manual failover process, which needs to
    verify that a certain amount of checks pass.
    """
    _run_cli(['failover'])


def run_debug_cli():
    """
    Pretty prints the contents of the current SystemState, as given by the JSON file.
    Can either print the data of all faulty components, or give an outline of all components being tracked.
    """
    description = "CLI tool viewing the state of the DDE, as tracked by the health monitor service. " \
                  "Pretty prints the data of all faulty components in the DDE." \

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--view_system_layout', help='View all components tracked by the health monitor',
                        action='store_true')
    parser.add_argument('--custom_json_path', help="If custom JSON path isn't provided, uses the default file stored"
                                                   " by the health monitor in /run")
    args = parser.parse_args()

    if args.custom_json_path:
        json_path = args.custom_json_path
    else:
        json_path = JSON_FILE_NAME

    if not args.view_system_layout:
        print_faulty_components(json_path)
    else:
        print_system_layout(json_path)
