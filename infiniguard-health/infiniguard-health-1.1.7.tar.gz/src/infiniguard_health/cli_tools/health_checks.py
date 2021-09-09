"""
Each check receives a SystemState object, and inspects the data to see if it is valid.
The check  is comparable to health rules, as it only inspects the data that is relevant to it, and makes
a decision regarding the validity of the data.

Important note - health checks and health rules, although they may have similar logic - are completely decoupled.
Often both rule and check must be updated in a similar way.

The checks must return a tuple of (check_result_boolean, failed_check_result_description).
For instance - (False, "DDE has no connection to volume 'dde1-boot'), or (True, None).
"""

from infiniguard_health.blueprints.components import ComponentContainer
from infiniguard_health.cli_tools.error_message_generators import (
    role_message_generator,
    ibox_connectivity_message_generator, remote_ddes_connectivity_message_generator,
    volume_active_paths_message_generator, remote_idracs_connectivity_message_generator,
    failover_services_up_message_generator
)
from infiniguard_health.health_rules.component_checks import (
    is_volume_connected,
    is_mgmt_ip_matching_role
)
from infiniguard_health.utils import get_current_ibox_time

STALE_TIMEOUT_MINUTES = 15

REQUIRED_FAILOVER_SERVICES = ['heartbeat.service']


class HealthCheck:
    def __init__(self, system_state_component_attr, is_component_healthy_func, error_message_generator):
        """
        The given is_component_healthy_func will be run on the given component (found by attribute name).
        If the component is a component container (e.g ethernet_ports), the function will be run on each individual
        component(e.g each port) separately, and will verify that they all pass.
        """
        self._system_state_component_attr = system_state_component_attr
        self._is_component_healthy = is_component_healthy_func
        self._error_message_generator = error_message_generator

    @staticmethod
    def _is_stale(component):
        return component.updated_at.shift(minutes=STALE_TIMEOUT_MINUTES) < get_current_ibox_time()

    def _staleness_check(self, system_state):
        if self._is_component_container(system_state):
            container = self._get_system_state_component_attr(system_state)
            stale_components = [component
                                for component in container
                                if self._is_stale(component)]
            is_stale = bool(stale_components)
            error_message = f"The following components of type {container.component_type} contain stale data:\n" + \
                            '\n'.join([f'* {component.printable_id}' for component in stale_components])
        else:
            independent = self._get_system_state_component_attr(system_state)
            is_stale = self._is_stale(independent)
            error_message = f"The following components of type {independent.__class__.__name__} contains stale data"

        if is_stale:
            return True, error_message
        else:
            return False, None

    def _get_system_state_component_attr(self, system_state):
        return getattr(system_state, self._system_state_component_attr)

    def _is_component_container(self, system_state):
        return isinstance(self._get_system_state_component_attr(system_state), ComponentContainer)

    def __call__(self, system_state):
        is_stale, message = self._staleness_check(system_state)
        if is_stale:
            return False, message

        if self._is_component_container(system_state):
            container = self._get_system_state_component_attr(system_state)
            faulty_components = [component for component in container if not self._is_component_healthy(component)]
            if faulty_components:
                return False, self._error_message_generator(faulty_components)
        else:
            independent = self._get_system_state_component_attr(system_state)
            if not self._is_component_healthy(independent):
                return False, self._error_message_generator(independent)

        return True, None


check_matching_mgmt_ip_and_role = HealthCheck(system_state_component_attr='role',
                                              is_component_healthy_func=lambda role: is_mgmt_ip_matching_role(role),
                                              error_message_generator=role_message_generator)

check_ibox_connectivity = HealthCheck(system_state_component_attr='ibox_connectivity',
                                      is_component_healthy_func=lambda ibox_connectivity:
                                      ibox_connectivity.is_connected,
                                      error_message_generator=ibox_connectivity_message_generator)

check_remote_ddes_connectivity = HealthCheck(system_state_component_attr='remote_ddes',
                                             is_component_healthy_func=lambda remote_dde: remote_dde.has_ssh_connection,
                                             error_message_generator=remote_ddes_connectivity_message_generator)

check_volume_active_paths = HealthCheck(system_state_component_attr='volumes',
                                        is_component_healthy_func=lambda volume: is_volume_connected(volume),
                                        error_message_generator=volume_active_paths_message_generator)

check_remote_idracs_connectivity = HealthCheck(system_state_component_attr='remote_idracs',
                                               is_component_healthy_func=lambda remote_idrac:
                                               remote_idrac.has_redfish_connection,
                                               error_message_generator=remote_idracs_connectivity_message_generator)
check_failover_services_up = HealthCheck(system_state_component_attr='services',
                                         is_component_healthy_func=lambda service:
                                         service.id not in REQUIRED_FAILOVER_SERVICES or service.status,
                                         error_message_generator=failover_services_up_message_generator)
