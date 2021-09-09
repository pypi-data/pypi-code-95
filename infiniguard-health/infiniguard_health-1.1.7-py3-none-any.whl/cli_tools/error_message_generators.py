from infiniguard_health.blueprints.components import ComponentContainer


class ErrorMessageGenerator:
    def __init__(self, head_of_message, error_message_per_component=None, delimiter='\n'):
        self._head_of_message = head_of_message
        self._error_message_per_component = error_message_per_component
        self._delimiter = delimiter

    @staticmethod
    def _is_component_container(component):
        return isinstance(component, ComponentContainer)

    def __call__(self, faulty_components):
        raise NotImplemented


class ContainerErrorMessageGenerator(ErrorMessageGenerator):
    def __call__(self, faulty_components):
        error_message = [self._head_of_message]
        for component in faulty_components:
            error_message.append(self._error_message_per_component.format(**component.to_primitive(),
                                                                          printable_id=component.printable_id))
        return self._delimiter.join(error_message)


class IndependentErrorMessageGenerator(ErrorMessageGenerator):
    def __call__(self, faulty_component):
        return self._head_of_message.format(**faulty_component.to_primitive(),
                                            printable_id=faulty_component.printable_id)


role_message_generator = IndependentErrorMessageGenerator(
    head_of_message='The current DDE is configured with a management IP which is not compatible with its role.\n'
                    'Management IP: {management_ip}\n'
                    'Role: {role_id}')

ibox_connectivity_message_generator = IndependentErrorMessageGenerator(
    head_of_message='The connection between this DDE and the InfiniBox API is disrupted')

remote_ddes_connectivity_message_generator = ContainerErrorMessageGenerator(
    head_of_message='Failed to ssh the following DDEs:',
    error_message_per_component='* DDE_ID: {role}, Error: {ssh_conn_error_msg}')

remote_idracs_connectivity_message_generator = ContainerErrorMessageGenerator(
    head_of_message='Failed to connect via redfish (HTTP) to the following iDRACs:',
    error_message_per_component='* iDRAC_ID: {idrac_id}, Error: {redfish_connect_error_msg}')

volume_active_paths_message_generator = ContainerErrorMessageGenerator(
    head_of_message="The following volumes don't have full multipath connectivity:",
    error_message_per_component='* VOLUME_ID: {printable_id}')

failover_services_up_message_generator = ContainerErrorMessageGenerator(
    head_of_message="The following services are required for failover, but are not active:",
    error_message_per_component='* {printable_id}')
