# -*- coding: utf-8 -*-
"""
Created on Tue May 25 11:32:02 2021

@author: chris.kerklaan

Objects for using the threedi-api simplified.

"""

# First-party import
import os
import json
import time
import requests
import logging
from pathlib import Path
from datetime import datetime

# from getpass import getpass

# Third-party imports
import datetime as dt

try:
    from threedidepth.calculate import calculate_waterdepth

    THREEDIDEPTH_EXISTS = True
except ImportError:
    THREEDIDEPTH_EXISTS = False


from openapi_client import ApiException, SimulationsApi
from openapi_client.api import AuthApi
from openapi_client.api import ThreedimodelsApi
from openapi_client.models import (
    TimeseriesWind,
    StableThresholdSavedState,
    TimedSavedStateUpdate,
    InitialSavedState,
    TimeStepSettings,
    NumericalSettings,
    PhysicalSettings,
)
from threedi_api_client.threedi_api_client import ThreediApiClient

# local imports
from .variables import (
    HHNK_UUID,
    NENS_UUID,
    HHNK_BWN_UUID,
    API_HOST,
    LIZARD_RAINFALL_UUID,
    DESIGN_TIMESTEP,
    AREA_WIDE_RAIN,
)
from .conversion import mm_5_min_to_ms
from .model import add_control_from_sqlite, add_laterals_1d_from_sqlite

# GLOBALS - check if file exists otherwise, ask for it
CREDENTIALS_FILE = str(Path(__file__).parent.absolute() / "credentials.json")
if os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE) as json_file:
        data = json.load(json_file)
        USERNAME = data["username"]
        PASSWORD = data["password"]


# Globals - Logger
logger = logging.getLogger(__name__)

# pyflakes
HHNK_UUID
NENS_UUID
HHNK_BWN_UUID


class Simulation:
    def __init__(
        self,
        organisation_uuid,
        username,
        password,
        simulation=None,
        api_host=API_HOST,
    ):
        config = {
            "API_HOST": api_host,
            "API_USERNAME": username,
            "API_PASSWORD": password,
        }

        self.client = ThreediApiClient(config=config)

        self.auth_api = AuthApi(self.client)
        self.models_api = ThreedimodelsApi(self.client)
        self.simulation_api = SimulationsApi(self.client)
        self.organisation_uuid = organisation_uuid

        try:
            user = self.auth_api.auth_profile_list()
        except ApiException:
            raise ValueError("Oops, something went wrong. Maybe you made a typo?")
        else:
            logger.info(f"Successfully logged in as {user.username}!")

        if simulation:
            self.simulation = simulation

    @classmethod
    def from_id(cls, simulation_id, organisation_uuid):
        client = ThreediApiClient(
            config={
                "API_HOST": API_HOST,
                "API_USERNAME": USERNAME,
                "API_PASSWORD": PASSWORD,
            }
        )
        api = SimulationsApi(client)
        return cls(organisation_uuid, api.simulations_read(int(simulation_id)))

    def filter(self, results, filtering):
        """returns the id based on the filtering, if nothing is found returns the original"""

        if len(filtering) == 0:
            return results

        for field_key, field_value in filtering.items():
            break

        if not hasattr(results, "results"):
            r = results
        else:
            r = results.results

        if len(r) == None:
            raise ValueError("got no results")

        all_results = []
        for result in r:
            for key, value in result.to_dict().items():
                if key == field_key and value == field_value:
                    all_results.append(result)

        return all_results

    def __repr__(self):
        return f"""ThreediAPI Simulation ({self.organisation_uuid}) @ {self.items}"""

    @property
    def name(self):
        return self.simulation.name

    @property
    def id(self):
        return self.simulation.id

    @property
    def progress(self):
        return self.simulation_api.simulations_progress_list(self.simulation.id)

    @property
    def is_finished(self):
        return self.status.name in ["finished"]

    @property
    def is_running(self):
        return self.status.name in ["starting", "initialized"]

    @property
    def is_remote_pending(self):
        return self.status.name in ["pending"]

    @property
    def is_local_pending(self):
        return self.status.name in ["created"]

    @property
    def items(self):
        return {
            self.id: {
                "status": self.status.name,
                "name": self.name,
                "progress": self.progress_percentage,
                "created": self.status.created.isoformat(),
            }
        }

    @property
    def progress_percentage(self):
        try:
            return self.progress.percentage
        except Exception:
            return 0

    @property
    def status(self):
        return self.simulation_api.simulations_status_list(self.simulation.id)

    @property
    def available_models(self):
        return self.models_api.threedimodels_list()

    def get_simulation(self, simulation_id):
        return Simulation(
            self.organisation_uuid,
            self.simulation_api.simulations_read(int(simulation_id)),
        )

    def get_simulations(
        self, name_contains, search_limit=None, return_objects=False, **filtering
    ):
        """retrieves simulations as a simulation instance"""

        count = self.simulation_api.simulations_list(
            name__icontains=name_contains
        ).count

        simulations = []
        i = 0
        if search_limit == None:
            search_limit = count
        while i < search_limit and i < count:
            simulations.extend(
                self.simulation_api.simulations_list(
                    name__icontains=name_contains, limit=100, offset=i
                ).results
            )
            i += 100

        filtered = self.filter(simulations, filtering)
        if return_objects:
            return [Simulation(self.organisation_uuid, s) for s in filtered]

        return filtered

    def get_models(self, name_contains, **filtering):
        return self.filter(
            self.models_api.threedimodels_list(name__icontains=name_contains),
            filtering,
        )

    def get_structures(self):
        return self.simulation_api.simulations_events_structure_control_table_list(
            self.simulation.id
        )

    def get_breaches(self, **filtering):
        breaches = []
        for i in range(0, int(self.model.breach_count), 250):
            breaches.extend(
                self.models_api.threedimodels_potentialbreaches_list(
                    self.model.id, limit=250, offset=i
                ).results
            )
        return self.filter(breaches, filtering)

    def get_initial_water_level_2d(self, **filtering):
        return self.filter(
            self.models_api.threedimodels_initial_waterlevels_list(self.model.id),
            filtering,
        )

    def get_saved_states(self, **filtering):
        return self.filter(
            self.models_api.threedimodels_saved_states_list(self.model.id),
            filtering,
        )

    def get_lateral_timeseries(self, **filtering):
        return self.filter(
            self.simulation_api.simulations_events_lateral_timeseries_list(
                self.model.id
            ),
            filtering,
        )

    def set_model(self, model):
        self.model = model

    def set_simulation(self, simulation):
        self.simulation = simulation

    def create(self, name, duration, start_datetime=datetime.now()):
        self.simulation = self.simulation_api.simulations_create(
            data={
                "name": name,
                "threedimodel": self.model.id,
                "organisation": self.organisation_uuid,
                "start_datetime": start_datetime,
                "duration": duration,  # in seconds, so we simulate for 1 hour
            }
        )

    def add_saved_state_threshold(self, variable, value):
        """creates a saved state when a variable becomes stable"""
        threshold_state = StableThresholdSavedState(
            name="saved state",
            thresholds=[{"variable": variable, "value": value}],
        )

        self.saved_state = (
            self.simulation_api.simulations_create_saved_states_stable_threshold_create(
                self.simulation.id, threshold_state
            )
        )

    def add_saved_state_timed(self, name, time):
        """creates a saved state after a time in seconds"""
        timed_state = TimedSavedStateUpdate(name=name, time=time)

        self.saved_state = (
            self.simulation_api.simulations_create_saved_states_timed_create(
                self.simulation.id, timed_state
            )
        )

    def add_saved_state(self, saved_state_id):
        saved_state = InitialSavedState(saved_state=saved_state_id)

        self.initial_state = self.simulation_api.simulations_initial_saved_state_create(
            self.simulation.id, saved_state
        )

    def add_rain_design(self, design_id):
        series = AREA_WIDE_RAIN[str(design_id)]
        series.append(0.0)

        rain_event = []
        for i, serie in enumerate(series):
            rain_event.append([i * DESIGN_TIMESTEP, mm_5_min_to_ms(serie)])

        self.simulation_api.simulations_events_rain_timeseries_create(
            simulation_pk=self.simulation.id,
            data={"offset": 0, "values": rain_event, "units": "m/s"},
        )

    def add_rain_timeseries(self, values, offset=0, units="m/s"):
        """adds timeseries rain to the simulation
        {
            "values": [
                [ 0, 0.1],    # time in seconds, rain in units (m/s)
                [ 100, 0.5]      # time in seconds, rain in units (m/s)
                ],
            }

        """
        self.simulation_api.simulations_events_rain_timeseries_create(
            simulation_pk=self.simulation.id,
            data={"offset": offset, "values": values, "units": "m/s"},
        )

    def add_rain_lizard(self, start_datetime, duration):
        self.simulation_api.simulations_events_rain_rasters_lizard_create(
            self.simulation.id,
            data={
                "offset": 0,
                "duration": duration,
                "reference_uuid": LIZARD_RAINFALL_UUID,
                "start_datetime": start_datetime,
                "units": "m/s",
            },
        )

    def add_wind(self, event: list, offset=0, units="m/s", drag_coefficient=0.05):
        """event is a list in the form of:
        {
            "values": [
                [ 0, 80, 220],    # time, speed, direction
                [ 400, 0, 0]      # time, speed, direction
                ],
            }
        """

        wind = TimeseriesWind(
            simulation=self.simulation.id,
            offset=offset,
            values=event,
            units=units,
        )
        self.simulation_api.simulations_events_wind_timeseries_create(
            self.simulation.id, wind
        )

        self.simulation_api.simulations_initial_wind_drag_coefficient_create(
            self.simulation.id, data={"value": drag_coefficient}
        )

    def add_initial_waterlevel_1d(self):
        self.simulation_api.simulations_initial1d_water_level_predefined_create(
            simulation_pk=self.simulation.id, data={}, async_req=False
        )

    def add_initial_waterlevel_2d(self, waterlevel_id, aggregation="max"):
        self.simulation_api.simulations_initial2d_water_level_raster_create(
            simulation_pk=self.simulation.id,
            data={
                "aggregation_method": aggregation,
                "initial_waterlevel": waterlevel_id,
            },
        )

    def add_breach(
        self,
        breach_id,
        duration_till_max_depth=100,
        initial_width=15,
        offset=0,
    ):
        """find your breach id with self.get_breach"""
        self.simulation_api.simulations_events_breaches_create(
            simulation_pk=self.simulation.id,
            data={
                "potential_breach": breach_id,
                "duration_till_max_depth": duration_till_max_depth,
                "initial_width": initial_width,
                "offset": offset,
            },
        )

    def add_boundary_conditions_file(self, file_path):
        """first you'll have to create a link and use requests put to uploade the file"""

        url = self.simulation_api.simulations_events_boundaryconditions_file_create(
            simulation_pk=self.simulation.id,
            data={"filename": "bc.text"},
        )

        r = requests.put(
            url.put_url,
            data=open(file_path, "rb"),
            headers={"Content-type": "application/json", "Slug": "bc.text"},
            auth=(USERNAME, PASSWORD),
        )
        self.r = r
        return r.status_code

    def add_lateral_timeseries(self, timeseries, coords):
        """coords in epsg 4326, timeseries in [[seconds, m3/s],[seconds, m3/s]]"""
        self.simulation_api.simulations_events_lateral_timeseries_create(
            simulation_pk=self.simulation.id,
            data={
                "offset": 0,
                "interpolate": True,
                "values": timeseries,
                "units": "m3/s",
                "point": {
                    "type": "Point",
                    "coordinates": [coords[0], coords[1]],
                },
            },
        )

    def add_sqlite_control(self, sqlite_path):
        controls = add_control_from_sqlite(sqlite_path, self.simulation.duration)
        for control in controls:
            self.simulation_api.simulations_events_structure_control_table_create(
                self.simulation.id, data=control
            )

    def add_sqlite_lateral_1d(self, sqlite_path):
        laterals = add_laterals_1d_from_sqlite(sqlite_path, self.simulation.duration)
        for lateral in laterals:
            self.simulation_api.simulations_events_lateral_timeseries_create(
                self.simulation.id, data=lateral
            )

    def set_timestep_settings(
        self,
        time_step,
        max_time_step,
        min_time_step,
        output_time_step,
        use_time_step_stretch=False,
    ):

        self.timestep_settings = (
            self.simulation_api.simulations_settings_time_step_create(
                self.simulation.id,
                TimeStepSettings(
                    max_time_step=max_time_step,
                    min_time_step=min_time_step,
                    output_time_step=output_time_step,
                    time_step=time_step,
                    use_time_step_stretch=use_time_step_stretch,
                ),
            )
        )

    def set_numerical_settings(self):

        data = NumericalSettings(
            cfl_strictness_factor_1d=1,
            cfl_strictness_factor_2d=1,
            convergence_cg=1.0e-9,
            flooding_threshold=0.000001,
            flow_direction_threshold=1e-06,
            friction_shallow_water_depth_correction=0,
            general_numerical_threshold=1.0e-8,
            limiter_slope_crossectional_area_2d=0,
            limiter_slope_friction_2d=0,
            limiter_slope_thin_water_layer=0,
            limiter_waterlevel_gradient_1d=1,
            limiter_waterlevel_gradient_2d=1,
            max_degree_gauss_seidel=700,
            max_non_linear_newton_iterations=20,
            min_friction_velocity=0.01,
            min_surface_area=1.0e-8,
            preissmann_slot=0,
            pump_implicit_ratio=0,
            time_integration_method=0,
            use_nested_newton=True,
            use_of_cg=20,
            use_preconditioner_cg=1,
        )

        self.simulation_api.simulations_settings_numerical_create(
            self.simulation.id, data
        )

    def set_physical_settings(self):
        data = PhysicalSettings(use_advection_1d=0, use_advection_2d=0)  #
        self.simulation_api.simulations_settings_physical_create(
            self.simulation.id, data
        )

    def set_pumpstation_capacity(self, structure_id, capacity, start, duration):
        """change a pumpcapacity structure_id is the id in the model"""
        data = {
            "offset": start,
            "duration": duration,
            "value": [capacity],
            "type": "set_pump_capacity",
            "structure_id": structure_id,
            "structure_type": "v2_pumpstation",
        }

        self.simulation_api.simulations_events_structure_control_timed_create(
            simulation_pk=self.simulation.id, data=data, async_req=False
        )

    def set_orifice_discharge(self, structure_id, positive, negative, start, duration):
        """change a orifice structure_id is the id in the model"""
        data = {
            "offset": start,
            "duration": duration,
            "value": [positive, negative],
            "type": "set_discharge_coefficients",
            "structure_id": structure_id,
            "structure_type": "v2_orifice",
        }

        self.simulation_api.simulations_events_structure_control_timed_create(
            simulation_pk=self.simulation.id, data=data, async_req=False
        )

    def set_weir_discharge(self, structure_id, positive, negative, start, duration):
        """change a orifice structure_id is the id in the model"""
        data = {
            "offset": start,
            "duration": duration,
            "value": [positive, negative],
            "type": "set_discharge_coefficients",
            "structure_id": structure_id,
            "structure_type": "v2_weir",
        }

        self.simulation_api.simulations_events_structure_control_timed_create(
            simulation_pk=self.simulation.id, data=data, async_req=False
        )

    def post_processing(
        self,
        name=None,
        uuid=None,
        basic=True,
        arrival=False,
        damage=False,
        damage_cost_type="avg",
        damage_flood_month="jan",
        inundation_period=12.0,
        damage_repair_time_infrastructure=60,
        damage_repair_time_buildings=120,
    ):

        if basic or arrival or damage:
            self.simulation_api.simulations_results_post_processing_lizard_basic_create(
                self.simulation.id,
                data={
                    "process_basic_results": True,
                    "scenario_name": name,
                },
            )
        if damage:
            self.simulation_api.simulations_results_post_processing_lizard_damage_create(
                self.simulation.id,
                data={
                    "cost_type": damage_cost_type,
                    "flood_month": damage_flood_month,
                    "inundation_period": inundation_period,
                    "repair_time_infrastructure": damage_repair_time_infrastructure,
                    "repair_time_buildings": damage_repair_time_buildings,
                },
            )

        if arrival:
            self.simulation_api.simulations_results_post_processing_lizard_arrival_create(
                self.simulation.id, data={}
            )

    def start(self):
        self.simulation_api.simulations_actions_create(
            self.simulation.id, data={"name": "start"}
        )

    def stop(self):
        self.simulation_api.simulations_actions_create(
            self.simulation.id, data={"name": "shutdown"}
        )

    def status_history(self):
        return self.simulation_api.simulations_status_history_list(self.simulation.id)

    def status_settings(self):
        return self.simulation_api.simulations_settings_overview(self.simulation.id)

    def event_status(self):
        return self.simulation_api.simulations_events(self.simulation.id)

    def event_post_process_status(self):
        return self.simulation_api.simulations_results_post_processing_lizard_overview_list(
            self.simulation.id
        )

    def post_process_status(self):
        return (
            self.simulation_api.simulations_results_post_processing_lizard_status_list(
                self.simulation.id
            )
        )

    def results_available(self):

        result_files = self.simulation_api.simulations_results_files_list(
            self.simulation.id
        )
        available = [file.file.filename for file in result_files.results]
        if "results_3di.nc" in available:
            try:
                self.simulation_api.simulations_results_files_download(
                    id=result_files.results[0].id,
                    simulation_pk=self.simulation.id,
                )

            except Exception as e:
                print("Result file not available (uploaded), error:", e)
            else:
                return True

        return False

    def download_file(self, path, url):
        r = requests.get(url)
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    def download(self, folder, sleep_time=30, waiting_count=10, skip_aggregation=True):
        """download files if availabe"""
        # waiting until at least the results_3di.nc is present

        count = 0
        while not self.results_available and count < waiting_count:
            time.sleep(sleep_time)
            print(f"Results not available, waiting ({count})")
            count += 1

        if count == waiting_count and not not self.results_available:
            raise ValueError(
                f"Results not available even after waiting {waiting_count*sleep_time} seconds"
            )

        path = os.path.join(folder, self.name)
        download_folder = Path(path)
        download_folder.mkdir(exist_ok=True)

        result_files = self.simulation_api.simulations_results_files_list(
            self.simulation.id
        )
        for file in result_files.results:

            if skip_aggregation:
                if file.filename == "aggregate_results_3di.nc":
                    continue

            url = self.simulation_api.simulations_results_files_download(
                id=file.id, simulation_pk=self.simulation.id
            )
            self.download_file(download_folder / file.filename, url.get_url)

        url = self.models_api.threedimodels_gridadmin_download(
            self.simulation.threedimodel_id
        )

        self.download_file(download_folder / "gridadmin.h5", url.get_url)


class Batch:
    """class used for:
        - Running simulations in a certain order
        - With a maximum amount of simulations at the same time
        - Downloads the results in a certain folder afterwards
        - Calculate waterdepth maps

    params:
        simulation_list: list of Simulation objects
        batch_folder: Folder for downloads and logging

    """

    def __init__(self, simulation_list, batch_folder):
        self.simulations = simulation_list
        self.folder = batch_folder

        folder = Path(self.folder)
        folder.mkdir(exist_ok=True)

        self.logging_path = self.folder + "/batch.log"
        self.log()

        self.max_running = 1

    @classmethod
    def from_folder(cls, folder, organisation_uuid):
        with open(folder + "/batch.log") as json_file:
            log = json.load(json_file)
        sim_list = [Simulation.from_id(sid, organisation_uuid) for sid in log.keys()]

        return cls(sim_list, folder)

    def __iter__(self):
        for simulation in self.simulations:
            yield simulation

    def __getitem__(self, name):
        if type(name) == str:
            return self.simulations[self.names.index(name)]
        elif type(name) == int:
            return self.simulations[name]
        else:
            raise TypeError("type should be integer or string/name")

    def __repr__(self):
        return str(f"ThreediAPI Batch @ {self.folder}, {self.simulations}")

    def is_downloaded(self, simulation):
        return (Path(self.folder) / simulation.name / "results_3di.nc").exists()

    def log(self):
        """writes the log file based on current status"""

        data = {
            sim.id: {
                "status": sim.status.name,
                "name": sim.name,
                "progress": sim.progress_percentage,
                "created": sim.status.created.isoformat(),
            }
            for sim in self
        }
        self.log_data = data
        with open(self.logging_path, "w") as outfile:
            json.dump(data, outfile)
        return self.log_data

    def get_status_history(self):
        self.history = self.simulations[0].status_history()

    @property
    def local_pending_simulations(self):
        return len(self.local_pending) > 0

    @property
    def remote_pending_simulations(self):
        return len(self.remote_pending) > 0

    @property
    def free_node(self):
        return len(self.running) < self.max_running

    @property
    def total_simulations(self):
        return len(self.simulations)

    @property
    def total_finished(self):
        return len(self.finished)

    @property
    def finished(self):
        return [s for s in self if s.is_finished]

    @property
    def running(self):
        return [s for s in self if s.is_running]

    @property
    def local_pending(self):
        return [s for s in self if s.is_local_pending]

    @property
    def remote_pending(self):
        return [s for s in self if s.is_remote_pending]

    @property
    def downloaded(self):
        return [s for s in self if self.is_downloaded(s)]

    @property
    def to_download(self):
        return [s for s in self if not self.is_downloaded(s) and s.is_finished]

    @property
    def names(self):
        return [s.name for s in self.simulations]

    @property
    def iso_date(self):
        return dt.datetime.now().isoformat()

    def wait(self, sleep_time):
        """waits only if pending simulations and no free node"""
        if self.local_pending_simulations and not self.free_node:
            logger.info(
                f"Waiting: {self.iso_date} pending simulations and no free simulation nodes"
            )
            time.sleep(sleep_time)

    def add(self, simulation):
        """you can add a simulation object here"""
        self.simulations.append(simulation)
        self.log()

    def start_simulation(self, robust=True):
        """starts a simulation if a possible
        params:
            robust: if True, starts simulations even if no self.free_node
        """

        simulation = self.local_pending[0]
        if robust:
            if self.local_pending_simulations:
                logger.info(f"Starting: {simulation.name}")
                simulation.start()
        else:
            if self.free_node and self.local_pending_simulations:
                logger.info(f"Starting: {simulation.name}")
                simulation.start()

        self.log()

    def run(self, download=True, max_running=1, sleep=30, robust=True):
        """runs the simulation until all are finished
        params:
            download: Waits and downloads the results
            max_running: Maximum simulteneous simulations
            sleep: Sleep time if simulations are pending
            wait: if False, returns if no pending simulations
            robust: starts all local pending simulations and
            lets the api handle the waiting, no free nodes are considered

        """
        if robust:
            while self.local_pending_simulations:
                self.start_simulation(robust=True)
        else:
            self.max_running = max_running
            while self.local_pending_simulations:
                self.start_simulation(robust=False)
                self.wait(sleep)

                if download:
                    self.download()

        self.log()

    def download(self, wait_until_all_finished=False, skip_aggregation=True):
        """download all finished simulation results"""

        if wait_until_all_finished:
            while self.total_finished != self.total_simulations:
                time.sleep(600)

        for simulation in self.to_download:
            logger.info(f"Downloading: {simulation.name}")
            simulation.download(self.folder, skip_aggregation)

        self.log()

    def stop(self):
        """stops all running simulations"""
        for simulation in self.running:
            logger.info(f"Stopping: {simulation.name}")
            simulation.stop()

    def depths(self, dem_path, calculation_step=-1):
        if THREEDIDEPTH_EXISTS:
            for folder in [f.path for f in os.scandir(self.folder) if f.is_dir()]:
                depth = ThreediDepth(folder, dem_path)
                depth.calculate(calculation_step)
        else:
            logger.info("Please install threedidepth")


class ThreediDepth:
    def __init__(self, folder, dem_path):
        self.folder = folder
        self.nc_path = self.folder + "/results_3di.nc"
        self.ga_path = self.folder + "/gridadmin.h5"
        self.dem_path = dem_path
        self.folder_name = Path(self.folder).stem

    def calculate(self, calculation_step=-1):
        name = self.folder + f"/{self.folder_name}_depth_{calculation_step}.tif"
        calculate_waterdepth(
            self.ga_path,
            self.nc_path,
            self.dem_path,
            name,
            calculation_steps=[calculation_step],
        )
