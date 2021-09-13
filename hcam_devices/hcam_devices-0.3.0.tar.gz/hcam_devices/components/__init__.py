from ..wamp import ModelComponentMixin, WrapperComponentMixin
from ..models.slide import FocalPlaneSlide
from ..models.flow_sensor import FlowSensor
from ..models.compo import Compo
from ..models.meerstetter import Meerstetter
from ..models.vac_gauge import VacGauge
from ..models.ccd import CCDHead
from ..models.ngc import NGC
from ..models.telescope import GTC


class GTCComponent(ModelComponentMixin):
    def __init__(self, config):
        self._component_name = config.extra.get(
            'name',
            str(self.__class__).replace('Component', '')
        ).lower()
        super(GTCComponent, self).__init__(config)
        self.traceback_app = True
        emulation_mode = config.extra.get('emulate')
        path = config.extra.get('path', '/data')
        self.model = GTC(emulate=emulation_mode, path=path)


class NGCComponent(ModelComponentMixin):
    def __init__(self, config):
        self._component_name = config.extra.get(
            'name',
            str(self.__class__).replace('Component', '')
        ).lower()
        super(NGCComponent, self).__init__(config)
        self.traceback_app = True
        emulation_mode = config.extra.get('emulate')
        self.model = NGC(emulation_mode)


class CCDComponent(WrapperComponentMixin):
    def __init__(self, config):
        self._component_name = config.extra.get(
            'name',
            str(self.__class__).replace('Component', '')
        ).lower()
        pressure_topic = config.extra.get('pressure_topic')
        flow_topic = 'hipercam.flow'
        peltier_topic = config.extra.get('peltier_topic')
        pen_number = config.extra.get('pen_number')
        peltier_channel = config.extra.get('peltier_channel')

        super(CCDComponent, self).__init__(config)
        self.traceback_app = True
        self.model = CCDHead(pressure_topic, flow_topic, peltier_topic, pen_number, peltier_channel)


class PressureComponent(ModelComponentMixin):
    def __init__(self, config):
        super(PressureComponent, self).__init__(config)
        self.traceback_app = True
        self._component_name = config.extra.get(
            'name',
            str(self.__class__).replace('Component', '')
        ).lower()
        host = config.extra.get('host', None)
        port = config.extra.get('port', None)
        emulation_mode = config.extra.get('emulate')
        self.model = VacGauge(host, port, emulate=emulation_mode)


class FocalPlaneSlideComponent(ModelComponentMixin):
    def __init__(self, config):
        super(FocalPlaneSlideComponent, self).__init__(config)
        self.traceback_app = True
        self._component_name = config.extra.get(
            'name',
            str(self.__class__).replace('Component', '')
        ).lower()
        host = config.extra.get('host', None)
        port = config.extra.get('port', None)
        emulation_mode = config.extra.get('emulate')
        self.model = FocalPlaneSlide(host, port, emulate=emulation_mode)


class FlowSensorComponent(ModelComponentMixin):
    def __init__(self, config):
        super(FlowSensorComponent, self).__init__(config)
        self.traceback_app = True
        self._component_name = config.extra.get(
            'name',
            str(self.__class__).replace('Component', '')
        ).lower()
        host = config.extra.get('host', None)
        port = config.extra.get('port', None)
        emulation_mode = config.extra.get('emulate')
        self.model = FlowSensor(host, port, emulate=emulation_mode)


class CompoComponent(ModelComponentMixin):
    def __init__(self, config):
        super(CompoComponent, self).__init__(config)
        self.traceback_app = True
        self._component_name = config.extra.get(
            'name',
            str(self.__class__).replace('Component', '')
        ).lower()
        port = config.extra.get('port', None)
        emulation_mode = config.extra.get('emulate')
        self.model = Compo(port, emulate=emulation_mode)


class MeerstetterComponent(ModelComponentMixin):
    def __init__(self, config):
        super(MeerstetterComponent, self).__init__(config)
        self.traceback_app = True
        self._component_name = config.extra.get(
            'name',
            str(self.__class__).replace('Component', '')
        ).lower()
        host = config.extra.get('host', None)
        port = config.extra.get('port', None)
        emulation_mode = config.extra.get('emulate')
        self.model = Meerstetter(host, port, emulate=emulation_mode)
