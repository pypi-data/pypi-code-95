from logging import getLogger

from infiniguard_health.blueprints.component_blueprints.dynamic_blueprints_functions import bonds_blueprint_func

_logger = getLogger(__name__)


class DynamicBlueprint:
    def __init__(self, blueprint_retrival_func):
        self._blueprint_retrival_func = blueprint_retrival_func
        self._blueprint_cache = []

    def generate_blueprint(self):
        try:
            blueprint = list(self._blueprint_retrival_func())
            self._blueprint_cache = blueprint
        except:
            _logger.exception(f'Failed to generate blueprint.\n'
                              f'Using cache instead: {self._blueprint_cache}.\n'
                              f'blueprint retrival function: {self._blueprint_retrival_func.__name__}')
        return self._blueprint_cache

    def __iter__(self):
        yield from self.generate_blueprint()

    def __str__(self):
        return str(list(self._blueprint_cache))


class NOOPBlueprint:
    """
    No-Op blueprint. When this blueprint is selected, all collected data of the relevant component is inserted into
    the SystemState.
    """
    pass


BONDS_BLUEPRINT = DynamicBlueprint(bonds_blueprint_func)
SNAPSHOTS_BLUEPRINT = NOOPBlueprint()
