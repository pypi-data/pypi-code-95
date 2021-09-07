"""This module contains a :class:`mosaik_api.Simulator` for the
flexiblity model, which is a wrapper for all models of the
pysimmods package.

"""
from datetime import datetime, timedelta

import mosaik_api
import numpy as np
from pysimmods.mosaik import LOG
from pysimmods.util.dateformat import GER
from pysimmods.other.flexibility.flexibility_model import FlexibilityModel
from .meta import META, MODELS


class FlexibilitySimulator(mosaik_api.Simulator):
    """The generic flexiblity mosaik simulator for all pysimmods."""

    def __init__(self):
        super().__init__(META)
        self.sid = None
        self.models = dict()
        self.num_models = dict()

        self.step_size = None
        self.now_dt = None

        self.planning_horizon = None
        self.num_schedules = 0

    def init(self, sid, **sim_params):
        """Called exactly ones after the simulator has been started.

        Parameters
        ----------
        sid : str
            Simulator ID for this simulator.
        start_date : str
            The start date as UTC ISO 8601 date string.
        step_size : int, optional
            Step size for this simulator. Defaults to 900.

        Returns
        -------
        dict
            The meta dict (set by *mosaik_api.Simulator*).

        """
        self.sid = sid
        if "step_size" not in sim_params:
            LOG.debug(
                "Param *step_size* not provided. "
                "Using default step size of 900."
            )
        self.step_size = sim_params.get("step_size", 900)
        self.now_dt = datetime.strptime(sim_params["start_date"], GER)

        self.unit = sim_params.get("unit", "kw")
        self.forecast_horizon_hours = sim_params.get(
            "forecast_horizon_hours", self.step_size / 3_600
        )

        self.provide_flexibilities = sim_params.get(
            "provide_flexibilities", False
        )
        self.flexibility_horizon_hours = sim_params.get(
            "flexibility_horizon_hours", 2
        )
        self.num_schedules = sim_params.get("num_schedules", 10)
        self.rng = np.random.RandomState(sim_params.get("seed", None))

        self._update_meta()

        return self.meta

    def create(self, num, model, **model_params):
        """Initialize the simulation model instance (entity).

        Parameters
        ----------
        num : int
            The number of models to create.
        model : str
            The name of the models to create. Must be present inside
            the simulator's meta.

        Returns
        -------
        list
            A list with information on the created entity.

        """
        entities = []
        params = model_params["params"]
        inits = model_params["inits"]
        self.num_models.setdefault(model, 0)

        for _ in range(num):
            eid = f"{model}-{self.num_models[model]}"
            self.models[eid] = FlexibilityModel(
                MODELS[model](params, inits),
                self.now_dt,
                self.step_size,
                self.forecast_horizon_hours,
                self.flexibility_horizon_hours,
                self.num_schedules,
                self.rng.randint(1_000_000),
                self.unit,
            )
            self.num_models[model] += 1
            entities.append({"eid": eid, "type": model})
        return entities

    def step(self, time, inputs, max_advance=0):
        """Perform a simulation step.

        Parameters
        ----------
        time : int
            The current simulation step (by convention in seconds since
            simulation start.
        inputs : dict
            A *dict* containing inputs for entities of this simulator.

        Returns
        -------
        int
            The next step this simulator wants to be stepped.

        """
        LOG.debug("At step %d: Received inputs: %s.", time, inputs)

        self._default_inputs()
        self._mosaik_inputs(inputs)

        for eid, model in self.models.items():
            model.step()

        self.now_dt += timedelta(seconds=self.step_size)
        self._generate_flexibilities()

        return time + self.step_size

    def get_data(self, outputs):
        """Returns the requested outputs (if feasible)"""

        data = dict()
        for eid, attrs in outputs.items():
            data[eid] = dict()
            model = eid.split("-")[0]
            for attr in attrs:

                if attr == "flexibilities":
                    value = self.models[eid].flexibilities
                elif attr == "schedule":
                    value = self.models[eid].schedule._data.loc[
                        self.now_dt : self.now_dt
                        + timedelta(hours=self.forecast_horizon_hours)
                        - timedelta(seconds=self.step_size)
                    ]
                elif attr == "target":
                    value = self.models[eid].schedule._data.loc[
                        self.now_dt - timedelta(seconds=self.step_size)
                    ]["target"]

                else:
                    # Apply correction of attr if necessary
                    if attr in ("p_mw", "p_th_mw", "q_mvar"):
                        attr = attr.replace("m", "k")

                    value = getattr(self.models[eid].state, attr)

                    # Apply correction of the value if necessary
                    if attr in ("p_kw", "p_th_kw", "q_kvar"):
                        attr = attr.replace("k", "m")
                        value *= 1e-3

                data.setdefault(eid, dict())[attr] = value

        LOG.debug("Gathered outputs: %s.", data)
        return data

    def _update_meta(self):
        for model in self.meta["models"].keys():
            self.meta["models"][model]["attrs"].append("flexibilities")
            self.meta["models"][model]["attrs"].append("schedule")
            self.meta["models"][model]["attrs"].append("target")

        self.meta["models"]["Photovoltaic"]["attrs"] += [
            "forecast_t_air_deg_celsius",
            "forecast_bh_w_per_m2",
            "forecast_dh_w_per_m2",
        ]
        self.meta["models"]["CHP"]["attrs"] += [
            "forecast_day_avg_t_air_deg_celsius"
        ]
        self.meta["models"]["HVAC"]["attrs"] += ["forecast_t_air_deg_celsius"]

    def _default_inputs(self):
        for eid, model in self.models.items():
            model.inputs.step_size = self.step_size
            model.inputs.now = self.now_dt

    def _mosaik_inputs(self, inputs):

        for eid, attrs in inputs.items():
            for attr, src_ids in attrs.items():

                if "forecast" in attr:
                    for forecast in src_ids.values():
                        self.models[eid].update_forecasts(forecast)
                    continue
                elif attr == "schedule":
                    for schedule in src_ids.values():
                        if schedule is not None:
                            self.models[eid].update_schedule(schedule)
                    continue

                # Aggregate inputs from different sources
                attr_sum = 0
                for val in src_ids.values():
                    if val is not None:
                        attr_sum += val
                attr_sum /= len(src_ids)

                if attr == "set_percent":
                    self.models[eid].set_percent = attr_sum
                else:
                    # Apply correction if necessary
                    if attr in ("p_mw", "p_th_mw", "q_mvar"):
                        attr = attr.replace("m", "k")
                        attr_sum *= 1e3

                    setattr(self.models[eid].inputs, attr, attr_sum)

    def _generate_flexibilities(self):
        if self.provide_flexibilities:
            for eid, model in self.models.items():
                model.generate_schedules(
                    self.now_dt.strftime(GER),
                    self.flexibility_horizon_hours,
                    self.num_schedules,
                )


if __name__ == "__main__":
    mosaik_api.start_simulation(FlexibilitySimulator())
