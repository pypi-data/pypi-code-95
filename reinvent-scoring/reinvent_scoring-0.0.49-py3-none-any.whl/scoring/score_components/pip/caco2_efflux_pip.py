from reinvent_scoring.scoring.component_parameters import ComponentParameters
from reinvent_scoring.scoring.score_components.pip.base_pip_component import BasePiPComponent


class CACO2EffluxPiP(BasePiPComponent):
    def __init__(self, parameters: ComponentParameters):
        super().__init__(parameters)

    def _parse_compound(self, compound):
        return float(compound["Caco2_Efflux_Ratio"])
