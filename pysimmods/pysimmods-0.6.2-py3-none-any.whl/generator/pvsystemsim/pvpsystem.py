"""This module contains a model of a pv system with pv modules and an
inverter"""
from pysimmods.other.invertersim.config import InverterConfig
from pysimmods.other.invertersim.inverter import Inverter
from pysimmods.model.generator import Generator
from pysimmods.generator.pvsim.pvp import PhotovoltaicPowerPlant
from pysimmods.generator.pvsystemsim.config import PVSystemConfig
from pysimmods.generator.pvsystemsim.inputs import PVSystemInputs
from pysimmods.generator.pvsystemsim.state import PVSystemState


class PVPlantSystem(Generator):
    """Pv system with pv modules and inverter"""

    def __init__(self, params, init_vals):
        self.config = PVSystemConfig(params)
        self.inputs = PVSystemInputs()
        self.state = PVSystemState(init_vals)
        self.pv = PhotovoltaicPowerPlant(params["pv"], init_vals["pv"])
        self.inverter = Inverter(params["inverter"])

    def step(self):
        """Perform simulation step"""

        # Step the pv plant
        self.pv.inputs.bh_w_per_m2 = self.inputs.bh_w_per_m2
        self.pv.inputs.dh_w_per_m2 = self.inputs.dh_w_per_m2
        self.pv.inputs.s_module_w_per_m2 = self.inputs.s_module_w_per_m2
        self.pv.inputs.t_air_deg_celsius = self.inputs.t_air_deg_celsius
        self.pv.inputs.step_size = self.inputs.step_size
        self.pv.inputs.now = self.inputs.now

        self.pv.step()

        # Step the inverter
        self.inverter.inputs.p_in_kw = self.pv.state.p_kw
        self.inverter.inputs.p_set_kw = self.inputs.p_set_kw
        self.inverter.inputs.q_set_kvar = self.inputs.q_set_kvar
        self.inverter.inputs.cos_phi_set = self.inputs.cos_phi_set

        self.inverter.step()

        # Update state
        self.state.t_module_deg_celsius = self.pv.state.t_module_deg_celsius
        self.state.p_kw = self.inverter.state.p_kw
        self.state.q_kvar = self.inverter.state.q_kvar
        self.state.cos_phi = self.inverter.state.cos_phi

        self.inputs.reset()

    def get_state(self):
        """Get state"""
        state_dict = {
            "pv": self.pv.get_state(),
            "inverter": self.inverter.get_state(),
        }
        return state_dict

    def set_state(self, state_dict):
        """Set state"""
        self.pv.set_state(state_dict["pv"])
        self.inverter.set_state(state_dict["inverter"])

        self.state.t_module_deg_celsius = self.pv.state.t_module_deg_celsius
        self.state.p_kw = self.inverter.state.p_kw
        self.state.q_kvar = self.inverter.state.q_kvar

    @property
    def set_percent(self):
        p_dominated = ["p_set", "pq_set"]
        q_dominated = ["q_set", "qp_set"]
        cos_phi_dominated = ["cos_phi_set"]
        mode = self.config.inverter.q_control

        if mode in p_dominated:
            p_kw = self.inputs.p_set_kw
            if p_kw is None:
                p_kw = self.state.p_kw

            return 100 * abs(
                p_kw / abs(self.config.p_max_kw - self.config.p_min_kw)
            )

        if mode in q_dominated:
            q_kvar = self.inputs.q_set_kvar
            if q_kvar is None:
                q_kvar = self.state.q_kvar

            return 100 * abs(
                q_kvar / abs(self.config.q_max_kvar - self.config.q_min_kvar)
            )

        if mode in cos_phi_dominated:
            cos_phi = self.inputs.cos_phi_set
            if cos_phi is None:
                cos_phi = self.state.cos_phi
            return cos_phi * 100

    @set_percent.setter
    def set_percent(self, set_percent):
        mode = self.config.inverter.q_control

        set_percent = max(min(abs(set_percent), 100.0), 0.0)
        if mode == "p_set":
            bounds = [abs(self.config.p_max_kw), abs(self.config.p_min_kw)]
            self.inputs.p_set_kw = min(bounds) + set_percent * 0.01 * (
                max(bounds) - min(bounds)
            )

        elif mode == "q_set":
            bounds = [abs(self.config.q_max_kvar), abs(self.config.q_min_kvar)]
            self.inputs.q_set_kvar = min(bounds) + set_percent * 0.01 * (
                max(bounds) - min(bounds)
            )

        elif mode == "pq_set":
            bounds = [abs(self.config.p_max_kw), abs(self.config.p_min_kw)]
            self.inputs.p_set_kw = min(bounds) + set_percent * 0.01 * (
                max(bounds) - min(bounds)
            )
            self.inputs.q_set_kvar = (
                self.config.inverter.sn_kva ** 2 - self.inputs.p_set_kw ** 2
            ) ** 0.5

        elif mode == "qp_set":
            bounds = [abs(self.config.q_max_kvar), abs(self.config.q_min_kvar)]
            self.inputs.q_set_kvar = min(bounds) + set_percent * 0.01 * (
                max(bounds) - min(bounds)
            )
            self.inputs.p_set_kw = (
                self.config.inverter.sn_kva ** 2 - self.inputs.q_set_kvar ** 2
            ) ** 0.5

        elif mode == "cos_phi_set":
            self.inputs.cos_phi_set = set_percent * 0.01
