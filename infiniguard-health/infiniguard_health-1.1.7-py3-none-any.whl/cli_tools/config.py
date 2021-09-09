"""
This config file holds one nametuple for each check in health_checks.py
The nametuple has the following attributes:
* check_description - General description of the check. Will be printed back as is.
* check_function - The relevant function in health_checks.py
* tags - A list of tags that this check should be part of.

When the CLI tool is run with a certain tag, all checks associated with that tag will be run (with each check simply
querying the collected data and making a decision if the check has passed or not).
The CLI tool will return a JSON containing all the checks relevant to the requested tag,
along with the checks' results and the check_id/description as defined here.
"""
from collections import namedtuple

from infiniguard_health.cli_tools.health_checks import (
    check_volume_active_paths,
    check_ibox_connectivity,
    check_matching_mgmt_ip_and_role,
    check_remote_ddes_connectivity,
    check_remote_idracs_connectivity,
    check_failover_services_up
)

HealthCheckConfig = namedtuple('HealthCheckConfig', ['check_description', 'check_function', 'tags'])

health_check_configurations = [
    HealthCheckConfig('Check volumes connectivity', check_volume_active_paths, ['volumes']),
    HealthCheckConfig('Check ibox connectivity', check_ibox_connectivity, ['ibox', 'failover']),
    HealthCheckConfig('Check matching role and mgmt ip', check_matching_mgmt_ip_and_role, ['role', 'failover']),
    HealthCheckConfig('Check remote DDEs connectivity', check_remote_ddes_connectivity, ['remote_ddes']),
    HealthCheckConfig('Check remote iDRACs connectivity', check_remote_idracs_connectivity, ['remote_idracs', 'failover']),
    HealthCheckConfig('Check that required services are up', check_failover_services_up,
                      ['failover_services', 'failover']),
]

for health_check_configuration in health_check_configurations:
    health_check_configuration.tags.append('all')
