import logging
import threading
from types import GeneratorType
from munch import munchify

from infiniguard_health.blueprints.component_blueprints.dynamic_blueprints import NOOPBlueprint
from infiniguard_health.blueprints.components import ComponentContainer, IndependentComponent
from infiniguard_health.data_collection.collectors import (
    lshw_data, omr_memory, omr_power_supplies, omr_fans,
    omr_bmc, omr_raid_controller,
    syscli_eth_data, ethtool_data, omr_temps, volumes_data,
    check_ssh_connection_to_ddes,
    check_redfish_connection_to_idracs, services_info,
    ibox_connectivity_info, role_info, fc_ports_gc,
    fc_ports_lspci, fc_ports_sysfs, fc_ports_sfp_info,
    fc_ports_driver_version, proc_net_bonding_data, snapshots_capacity_data, snapshots_data,
    dde_capacity_data, policies_data, snapshot_suspend_delete_data
)
from infiniguard_health.data_collection.load_configs import (
    omr_memory_load_config, omr_psus_load_config,
    omr_fans_load_config, ethtool_load_config, eth_lshw_load_config, temps_load_config, syscli_eth_load_config,
    services_load_config, volumes_load_config,
    omr_bmc_load_config, omr_raidcontroller_load_config, ibox_connectivity_load_config, role_load_config,
    remote_idracs_load_config, remote_ddes_load_config, fcports_gc_load_config, fcports_driver_version_load_config,
    fcports_lspci_load_config, fcports_sysfs_load_config, fcports_sfp_info_load_config, bonds_load_config,
    snapshots_capacity_load_config, snapshots_load_config, polices_load_config, snapshot_suspend_delete_load_config,
    dde_capacity_load_config
)
from infiniguard_health.health_monitor.exceptions import (
    InvalidIDFieldOrData, PreLoadParserFunctionError,
    CollectorReturnedNone, RuntimeCollectorError, handle_data_collection_exceptions
)
from infiniguard_health.logger_config import is_test
from infiniguard_health.utils import is_standby_app

threading_lock = threading.Lock()

_logger = logging.getLogger(__name__)


class Loader:
    is_enabled = True

    def __init__(self, loader_id, collector, load_configs):
        self._loader_id = loader_id
        self._collector = collector
        self._system_state = None

        if not isinstance(load_configs, (list, tuple)):
            load_configs = [load_configs]
        self._load_configs = load_configs

    def __str__(self):
        return self._loader_id

    def __repr__(self):
        return self.__str__()

    @property
    def loader_id(self):
        return self._loader_id

    @property
    def exception_str(self):
        return f'Loader: {self}\n' \
               f'Collector Function: {self._collector.__name__}'

    def _is_component_container(self, component_name):
        return isinstance(getattr(self._system_state, component_name), ComponentContainer)

    def _convert_to_id_data_pair(self, load_config, data):
        """Loader should receive 3 'types' of data structures:
           1. dict of data - IndependentComponent
           2. list of dicts - ComponentContainer data
           3. dict of dicts - ComponentContainer data which is already 'identified' - meaning the keys
              of the parent dict provided are already the values of each id_field of the AssociateComponents
              in the ComponentContainer.

           For cases 1 and 3 there is no need to 'identify' the data - convert to {id_field: data} pairs.
           Examples for each structure:
               1. omr_bmc
               2. volumes_data
               3. syscli_eth_data

            This method transforms the data - a list of dicts to a dict of dicts which its keys are
            the values of each id_field of a component_data and the values are component_data respectivly.
        """
        if isinstance(data, dict):
            return data
        try:
            return {component_data[load_config.id_field]: component_data for component_data in data}
        except KeyError:
            raise InvalidIDFieldOrData(self, load_config,
                                       (f'A wrong id_field was given '
                                        f'or the data does not contain id_field for one of the components.\n'
                                        f'id_field: {load_config.id_field}\n'
                                        f'data: {list(data)}'))

    @staticmethod
    def _load_data_into_component(component_instance, data, fields_to_load):
        # Using ETL component to transform field names to fit with 'fields_to_load'
        # as Component.field(deserialize_from='old_field_name') will import data into the 'new_field_name'.
        component_class = component_instance.__class__
        etl_component = component_class()
        etl_component.import_data(data)

        data_to_load = {key: etl_component[key] for key in fields_to_load if etl_component[key] is not None}
        component_instance.fast_import_data(data_to_load)

    def _get_component_instance(self, component_name, component_id=None):
        """
        Returns a Component based on the component_name and component_id provided.
        If component_id is provided, an AssociateComponent is returned.
        else an IndependentComponent is returned.
        :param component_name: The component_id in SystemState._system_components that corresponds to the wanted Component.
        :param component_id: component_id of the component in its parent ComponentContainers dict.
        :return: AssociateComponent or IndependentComponent
        """
        component_or_container = getattr(self._system_state, component_name)
        if isinstance(component_or_container, ComponentContainer):
            return component_or_container[component_id]
        return component_or_container

    @staticmethod
    def _set_id_of_component(component_instance, component_id=None):
        """
        Component.id evaluation per subclass:
        AssociateComponent:
        id - The value of its id_field.

        IndependentComponent:
        id - Its subclass' class name.
        """
        if isinstance(component_instance, IndependentComponent):
            component_id = component_instance.__class__.__name__

        component_instance.id = component_id

    @staticmethod
    def _clear_fields_to_load_in_component(component, fields_to_load):
        cleared_data = {field_name: None for field_name in fields_to_load}
        component.fast_import_data(cleared_data)

    @staticmethod
    def _check_for_ids_not_in_blueprint(blueprint, data):
        return set(data) - set(blueprint)

    def mark_loader_components_as_missing(self):
        for load_config in self._load_configs:
            self.mark_load_config_components_as_missing(load_config)

    def mark_load_config_components_as_missing(self, load_config):
        if isinstance(load_config.component_blueprint, NOOPBlueprint):
            return  # If there is no blueprint, no components should be marked as missing

        with threading_lock:
            if self._is_component_container(load_config.component_name):
                for component_id in load_config.component_blueprint:
                    component_instance = self._get_component_instance(load_config.component_name, component_id)
                    _logger.warning(f'{load_config.component_type.__name__} with component_id: {component_id}'
                                    f' is missing. load_config: {load_config.config_id}')
                    component_instance.is_missing = True
                    self._set_id_of_component(component_instance, component_id=component_id)
            else:
                _logger.warning(f'{load_config.component_type.__name__} is missing. '
                                f'load_config: {load_config.config_id}')
                component_instance = self._get_component_instance(load_config.component_name)
                component_instance.is_missing = True
                self._set_id_of_component(component_instance)

    def _map_independent_component_data_to_system_state(self, component_data, load_config):
        """
        Loads component_data and metadata into the appropriate component in the system_state.
        """
        with threading_lock:
            component_instance = self._get_component_instance(load_config.component_name)

            if load_config.clear_data_when_missing:
                self._clear_fields_to_load_in_component(component_instance, load_config.fields_to_load)

            _logger.info(f'Loader {self._loader_id}: Loading data into component {load_config.component_type.__name__}')
            self._load_data_into_component(component_instance, component_data, load_config.fields_to_load)
            self._set_id_of_component(component_instance)

    def _map_component_container_data_to_system_state(self, data, load_config):
        """
        Loads data and metadata into the appropriate components of the ComponentContainer in the system_state.

        For each component_id in the mapping looks for its corresponding component_data in the data.
        This approach allows to identify missing data for a component, which in that case
        would be marked with AssociateComponent.is_missing = True
        """
        component_container = getattr(self._system_state, load_config.component_name)

        # Using the no-op blueprint imports all collected data into the component container.
        # If a component id that already exists in the container is not found in the current data,
        # it will be marked as missing.
        if isinstance(load_config.component_blueprint, NOOPBlueprint):
            collected_component_ids = data.keys()
            existing_component_ids = component_container.get_dict().keys()
            component_ids = set(collected_component_ids).union(set(existing_component_ids))

        else:
            component_ids = load_config.component_blueprint
            unidentified_ids = self._check_for_ids_not_in_blueprint(load_config.component_blueprint, data)
            if unidentified_ids:
                _logger.warning(f'load_config: {load_config.config_id} - The following identifiers were collected, '
                                f'but do not appear in the mapping.\n'
                                f'IDs in data but not in blueprint: {unidentified_ids}\n'
                                f'blueprint IDs: {load_config.component_blueprint}')

        with threading_lock:
            for component_id in component_ids:
                component_instance = self._get_component_instance(load_config.component_name, component_id)

                component_new_data = data.get(component_id)
                if component_new_data:
                    self._clear_fields_to_load_in_component(component_instance, load_config.fields_to_load)

                    _logger.info(f'Loader {self._loader_id}: Loading data '
                                 f'into component {load_config.component_type.__name__} with Id: {component_id}')
                    component_instance.is_missing = False
                    self._load_data_into_component(component_instance, component_new_data, load_config.fields_to_load)
                else:
                    if load_config.clear_data_when_missing:
                        self._clear_fields_to_load_in_component(component_instance, load_config.fields_to_load)

                        _logger.warning(f'{load_config.component_type.__name__} with component_id: {component_id}'
                                        f' is missing. load_config: {load_config.config_id}')
                    component_instance.is_missing = True
                    
                self._set_id_of_component(component_instance, component_id=component_id)

            # Updating each component sets the updated_at field. We need to do the same for the component container.
            component_container.set_updated_at_field_to_now()

    def _map_data_to_system_state(self, data, load_config):
        """
        * A ComponentContainer's load config must contain component_blueprint for the loading process.
          If component_blueprint is missing than it's a load config for an IndependentComponent.
        """
        if self._is_component_container(load_config.component_name):
            _logger.info(f'Loader {self._loader_id}: Mapping data into '
                         f'container component of {load_config.component_type.__name__}')
            self._map_component_container_data_to_system_state(data, load_config)
        else:
            _logger.info(f'Loader {self._loader_id}: Mapping data into '
                         f'independent component {load_config.component_type.__name__}')
            self._map_independent_component_data_to_system_state(data, load_config)

    @handle_data_collection_exceptions
    def _load(self, load_config, data):
        """
        pre_load_parser_function:
            handles the last parsing of the data pre-loading.
            As a source might contain multiple components data, it provides the ability to separate
            by the data by each load configuration or run last parsing steps post execution of a generic parser.

        _convert_to_id_data_pair:
            Go to the method's docstring.

        _map_data_to_system_state:
            Go to the method's docstring.
        """
        if load_config.pre_load_parser_function is not None:
            try:
                data = load_config.pre_load_parser_function(data)
            except Exception as e:
                raise PreLoadParserFunctionError(self, load_config, repr(e))

            if data is None:
                raise PreLoadParserFunctionError(self, load_config, 'The pre_load_parser function returned None.')

        identified_data = self._convert_to_id_data_pair(load_config, data)
        self._map_data_to_system_state(identified_data, load_config)

    @handle_data_collection_exceptions
    def __call__(self, system_state):
        """
        The main function of the Loader.
        Calls self._collector() to recieve the final data (post-parsing).
        Executes the loading processes based on every LoadConfig in self._load_configs.
        :param system_state
        :return: None - Modifies system_state in-place.
        """
        if not self.is_enabled:
            _logger.debug(f"Loader {self._loader_id} is disabled. Skipping its operation.")
            return

        self._system_state = system_state
        try:
            _logger.info(f'Loader {self._loader_id}: Executing collector {self._collector.__name__}')
            data = self._collector()
            if isinstance(data, GeneratorType):
                # Exhaust generator to catch collector exceptions here.
                data = list(data)
        except Exception as e:
            raise RuntimeCollectorError(self, repr(e))

        if data is None:
            raise CollectorReturnedNone(self, 'The collector function returned None.')

        for load_config in self._load_configs:
            _logger.info(f'Loader {self._loader_id}: Starting to load with load_config: {load_config.config_id}')
            self._load(load_config, data)


LOADER_IDS = munchify({
    'omr_memory_loader': 'omr_memory_loader',
    'omr_psus_loader': 'omr_psus_loader',
    'omr_fans_loader': 'omr_fans_loader',
    'ethtool_loader': 'ethtool_loader',
    'lshw_loader': 'lshw_loader',
    'fcports_gc_loader': 'fcports_gc_loader',
    'fcports_driver_version_loader': 'fcports_driver_version_loader',
    'fcports_lspci_loader': 'fcports_lspci_loader',
    'fcports_sysfs_loader': 'fcports_sysfs_loader',
    'fcports_sfp_info_loader': 'fcports_sfp_info_loader',
    'temps_loader': 'temps_loader',
    'syscli_ethernet_loader': 'syscli_ethernet_loader',
    'services_loader': 'services_loader',
    'volumes_loader': 'volumes_loader',
    'omr_bmc_loader': 'omr_bmc_loader',
    'omr_raidcontroller_loader': 'omr_raidcontroller_loader',
    'ibox_connectivity_loader': 'ibox_connectivity_loader',
    'role_loader': 'role_loader',
    'remote_ddes_loader': 'remote_ddes_loader',
    'remote_idracs_loader': 'remote_idracs_loader',
    'bonds_loader': 'bonds_loader',
    'snapshots_capacity_loader': 'snapshots_capacity_loader',
    'dde_capacity_loader': 'dde_capacity_loader',
    'snapshots_loader': 'snapshots_loader',
    'policies_loader': 'policies_loader',
    'snapshot_suspend_delete_loader': 'snapshot_suspend_delete_loader',
})

loaders_dict = {}


def initialize_loaders():
    loaders_list = [
        Loader(loader_id=LOADER_IDS.omr_memory_loader,
               collector=omr_memory,
               load_configs=omr_memory_load_config),
        Loader(loader_id=LOADER_IDS.omr_psus_loader,
               collector=omr_power_supplies,
               load_configs=omr_psus_load_config),
        Loader(loader_id=LOADER_IDS.omr_fans_loader,
               collector=omr_fans,
               load_configs=omr_fans_load_config),
        Loader(loader_id=LOADER_IDS.ethtool_loader,
               collector=ethtool_data,
               load_configs=ethtool_load_config),
        Loader(loader_id=LOADER_IDS.lshw_loader,
               collector=lshw_data,
               load_configs=eth_lshw_load_config),
        Loader(loader_id=LOADER_IDS.fcports_gc_loader,
               collector=fc_ports_gc,
               load_configs=fcports_gc_load_config),
        Loader(loader_id=LOADER_IDS.fcports_driver_version_loader,
               collector=fc_ports_driver_version,
               load_configs=fcports_driver_version_load_config),
        Loader(loader_id=LOADER_IDS.fcports_lspci_loader,
               collector=fc_ports_lspci,
               load_configs=fcports_lspci_load_config),
        Loader(loader_id=LOADER_IDS.fcports_sysfs_loader,
               collector=fc_ports_sysfs,
               load_configs=fcports_sysfs_load_config),
        Loader(loader_id=LOADER_IDS.fcports_sfp_info_loader,
               collector=fc_ports_sfp_info,
               load_configs=fcports_sfp_info_load_config),
        Loader(loader_id=LOADER_IDS.temps_loader,
               collector=omr_temps,
               load_configs=temps_load_config),
        Loader(loader_id=LOADER_IDS.syscli_ethernet_loader,
               collector=syscli_eth_data,
               load_configs=syscli_eth_load_config),
        Loader(loader_id=LOADER_IDS.services_loader,
               collector=services_info,
               load_configs=services_load_config),
        Loader(loader_id=LOADER_IDS.volumes_loader,
               collector=volumes_data,
               load_configs=volumes_load_config),
        Loader(loader_id=LOADER_IDS.omr_bmc_loader,
               collector=omr_bmc,
               load_configs=omr_bmc_load_config),
        Loader(loader_id=LOADER_IDS.omr_raidcontroller_loader,
               collector=omr_raid_controller,
               load_configs=omr_raidcontroller_load_config),
        Loader(loader_id=LOADER_IDS.ibox_connectivity_loader,
               collector=ibox_connectivity_info,
               load_configs=ibox_connectivity_load_config),
        Loader(loader_id=LOADER_IDS.role_loader,
               collector=role_info,
               load_configs=role_load_config),
        Loader(loader_id=LOADER_IDS.remote_ddes_loader,
               collector=check_ssh_connection_to_ddes,
               load_configs=remote_ddes_load_config),
        Loader(loader_id=LOADER_IDS.remote_idracs_loader,
               collector=check_redfish_connection_to_idracs,
               load_configs=remote_idracs_load_config),
        Loader(loader_id=LOADER_IDS.bonds_loader,
               collector=proc_net_bonding_data,
               load_configs=bonds_load_config),
        Loader(loader_id=LOADER_IDS.snapshots_capacity_loader,
               collector=snapshots_capacity_data,
               load_configs=snapshots_capacity_load_config),
        Loader(loader_id=LOADER_IDS.dde_capacity_loader,
               collector=dde_capacity_data,
               load_configs=dde_capacity_load_config),
        Loader(loader_id=LOADER_IDS.snapshots_loader,
               collector=snapshots_data,
               load_configs=snapshots_load_config),
        Loader(loader_id=LOADER_IDS.policies_loader,
               collector=policies_data,
               load_configs=polices_load_config),
        Loader(loader_id=LOADER_IDS.snapshot_suspend_delete_loader,
               collector=snapshot_suspend_delete_data,
               load_configs=snapshot_suspend_delete_load_config),
    ]

    for loader in loaders_list:
        loaders_dict[loader.loader_id] = loader

    # Disabling cyber recovery loaders when running on standby or attached DDE
    CYBER_RECOVER_LOADERS = (LOADER_IDS.snapshots_loader, LOADER_IDS.policies_loader,
                             LOADER_IDS.snapshot_suspend_delete_loader, LOADER_IDS.snapshots_capacity_loader)
    if not is_test() and is_standby_app():
        for loader_id in CYBER_RECOVER_LOADERS:
            loaders_dict[loader_id].is_enabled = False
