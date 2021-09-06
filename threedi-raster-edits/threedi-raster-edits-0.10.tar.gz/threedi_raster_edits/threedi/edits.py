# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 08:43:02 2020

@author: chris.kerklaan

ThreediEdits is a class based on vector.py and raster.py to edit threedi models
The class always edits the model in memory and you'll have to write the model
to show the results

# TODO:cd
    2. correcte types moeten al in model zitten, voordat je het model from scratch maakt
    3. Laad je gehele model in geheugen, voor de snelheid, 
    wanneer een connectie wordt gemaakt met de postgrestabellen maak je weer verbinding
# Bug:
    
# Bugs solved

# Opmerkingen

"""

__version__ = "0.1"
__author__ = "Chris Kerklaan - Nelen & Schuurmans"

# System imports
import os
import copy
import logging
import pathlib

# Third-party imports
from osgeo import ogr
from tqdm import tqdm

# Local imports
from threedi_raster_edits.threedi.rastergroup import ThreediRasterGroup
from threedi_raster_edits.threedi.vectorgroup import ThreediVectorGroup
from threedi_raster_edits.threedi.tables.constants import TABLES, raster_fields
from threedi_raster_edits.threedi.tables.models import MODEL_MAPPING

# Globals
# Drivers
OGR_SQLITE_DRIVER = ogr.GetDriverByName("SQLite")
OGR_MEM_DRIVER = ogr.GetDriverByName("Memory")

# logger
logger = logging.getLogger(__name__)


class ThreediEdits(ThreediVectorGroup):
    """An object for editing a threedi model,
    can be openen from scratch, from any ogr format (sqlite, postgres, geopackage).
    If rasters are present in the right folder, they are editable
    and can be written as well

    """

    def __init__(
        self,
        sqlite_path=None,
        pg_str=None,
        mode="copy",
        scenario=1,
    ):

        if sqlite_path is not None and not os.path.exists(str(sqlite_path)):
            raise FileNotFoundError("Path does not exist")

        if sqlite_path:
            ogr_ds = ogr.Open(str(sqlite_path), 0)
            self.model_dir = os.path.dirname(sqlite_path) + "/"
            self.name = pathlib.Path(sqlite_path).stem
            self.path = os.path.join(os.getcwd(), sqlite_path)

        if pg_str:
            ogr_ds = ogr.Open(pg_str, 0)

        if mode == "empty":
            ogr_ds = None

        super().__init__(ogr_ds, mode, scenario)
        self.scenario = scenario
        self.rastergroup = ThreediRasterGroup()
        self.reset = False

    @classmethod
    def from_pg(
        cls,
        dbname,
        host="nens-3di-db-03.nens.local",
        port="5432",
        user="threedi",
        password="1S418lTYWLFsYxud4don",
        scenario=1,
    ):

        pg_str = ("PG:host={} port={} user='{}'" "password='{}' dbname='{}'").format(
            host, port, user, password, dbname
        )
        return cls(pg_str=ogr.Open(pg_str), scenario=scenario)

    @classmethod
    def from_scratch(cls):
        return cls(mode="empty", scenario=1)

    def __getitem__(self, table):
        table_model = MODEL_MAPPING[table]

        if hasattr(table_model, "required"):
            required = copy.deepcopy(table_model.required)
            for key, value in table_model.required.items():
                required[key] = getattr(self, key)
        else:
            required = {}
        return MODEL_MAPPING[table](self.ds, table, **required)

    def set_scenario(self, scenario):
        self.scenario = scenario

    @property
    def scenario_exists(self):
        try:
            global_settings = self.ds.GetLayerByName("v2_global_settings")
        except IndexError:
            return False
        if global_settings.GetFeature(self.scenario) == None:
            return False
        return True

    def get_raster_files(self, scenario):
        global_settings = self.ds.GetLayerByName("v2_global_settings")
        gs = global_settings.GetFeature(scenario)
        paths = {field: gs[field] for field in raster_fields if field}
        infiltration_settings = self.ds.GetLayerByName("v2_simple_infiltration")
        infiltration_id = gs["simple_infiltration_settings_id"]
        if type(infiltration_id) == int:
            infiltration = infiltration_settings.GetFeature(infiltration_id)
            if infiltration is not None:
                paths["infiltration_rate_file"] = infiltration["infiltration_rate_file"]
                paths["max_infiltration_capacity_file"] = infiltration[
                    "max_infiltration_capacity_file"
                ]
        return paths

    @property
    def raster_files(self):
        if not self.scenario_exists:
            return {}
        return self.get_raster_files(self.scenario)

    @property
    def existing_raster_paths(self):
        if not hasattr(self, "model_dir"):
            return {}
        else:
            paths = {}
            for k, v in self.raster_files.items():
                if v is not None and os.path.exists(self.model_dir + v):
                    paths[k] = self.model_dir + v
            return paths

    @property
    def placed_rasters(self):
        return self.rasters.count > 0

    @property
    def has_existing_rasters(self):
        return len(self.existing_raster_paths) > 0

    @property
    def rasters(self):
        group_name = f"rastergroup_{self.scenario}"
        if (
            self.has_existing_rasters
            and self.rastergroup.count == 0
            and not hasattr(self, f"rastergroup_{self.scenario}")
        ):
            setattr(self, group_name, ThreediRasterGroup(**self.existing_raster_paths))

        if not self.has_existing_rasters:
            return self.rastergroup

        return getattr(self, group_name)

    @rasters.setter
    def rasters(self, group):
        setattr(self, f"rastergroup_{self.scenario}", group)

    def write(self, path, check=True, rasters=False, rasters_correct=True):
        path = str(path)

        if (self.has_existing_rasters or self.placed_rasters) and rasters:

            for scenario in self.scenarios:
                self.scenario = scenario
                group = self.rasters

                if rasters_correct:
                    group.correct()

                group.write(str(pathlib.Path(path).parent), self.raster_files)

        self.write_model(path, check)

    @property
    def scenarios(self):
        return self.global_settings.fids

    @property
    def scenario_count(self):
        return self.global_settings.count

    @property
    def epsg(self):
        return self.global_setting["epsg"]

    @property
    def nodes(self):
        if not hasattr(self, "model_nodes") or self.reset:
            self.model_nodes = self["v2_connection_nodes"]
        return self.model_nodes

    @property
    def manholes(self):
        if not hasattr(self, "model_manholes") or self.reset:
            self.model_manholes = self["v2_manhole"]
        return self.model_manholes

    @property
    def pipes(self):
        if not hasattr(self, "model_pipes") or self.reset:
            self.model_pipes = self["v2_pipe"]
        return self.model_pipes

    @property
    def global_setting(self):
        if not hasattr(self, "model_global_setting") or self.reset:
            self.model_global_setting = self["v2_global_settings"][self.scenario]
        return self.model_global_setting

    @property
    def global_settings(self):
        if not hasattr(self, "model_global_settings") or self.reset:
            self.model_global_settings = self["v2_global_settings"]
        return self.model_global_settings

    @property
    def simple_infiltration(self):
        if not hasattr(self, "model_simple_infiltration") or self.reset:
            self.model_simple_infiltration = self["v2_simple_infiltration"]
        return self.model_simple_infiltration

    @property
    def numerical_settings(self):
        if not hasattr(self, "model_numerical_settings") or self.reset:
            self.model_numerical_settings = self["v2_numerical_settings"]
        return self.model_numerical_settings

    @property
    def aggregation_settings(self):
        if not hasattr(self, "model_aggregation_settings") or self.reset:
            self.model_aggregation_settings = self["v2_aggregation_settings"]
        return self.model_aggregation_settings

    @property
    def obstacles(self):
        if not hasattr(self, "model_obstacles") or self.reset:
            self.model_obstacles = self["v2_obstacle"]
        return self.model_obstacles

    @property
    def channels(self):
        if not hasattr(self, "model_channels") or self.reset:
            self.model_channels = self["v2_channel"]
        return self.model_channels

    @property
    def cross_section_definitions(self):
        if not hasattr(self, "model_cross_section_definitions") or self.reset:
            self.model_cross_section_definitions = self["v2_cross_section_definition"]
        return self.model_cross_section_definitions

    @property
    def cross_section_locations(self):
        if not hasattr(self, "model_cross_section_locations") or self.reset:
            self.model_cross_section_locations = self["v2_cross_section_location"]
        return self.model_cross_section_locations

    @property
    def grid_refinement_areas(self):
        if not hasattr(self, "model_grid_refinement_area") or self.reset:
            self.model_grid_refinement_area = self["v2_grid_refinement_area"]
        return self.model_grid_refinement_area

    @property
    def grid_refinements(self):
        if not hasattr(self, "model_grid_refinement") or self.reset:
            self.model_grid_refinement = self["v2_grid_refinement"]
        return self.model_grid_refinement

    @property
    def boundary_conditions_1d(self):
        if not hasattr(self, "model_1d_boundary_conditions") or self.reset:
            self.model_1d_boundary_conditions = self["v2_1d_boundary_conditions"]
        return self.model_1d_boundary_conditions

    @property
    def laterals_1d(self):
        if not hasattr(self, "model_1d_laterals") or self.reset:
            self.model_1d_laterals = self["v2_1d_lateral"]
        return self.model_1d_laterals

    @property
    def pumpstations(self):
        if not hasattr(self, "model_pumpstations") or self.reset:
            self.model_pumpstations = self["v2_pumpstation"]
        return self.model_pumpstations

    @property
    def levees(self):
        if not hasattr(self, "model_levees") or self.reset:
            self.model_levees = self["v2_levee"]
        return self.model_levees

    @property
    def weirs(self):
        if not hasattr(self, "model_weirs") or self.reset:
            self.model_weirs = self["v2_weir"]
        return self.model_weirs

    @property
    def orifices(self):
        if not hasattr(self, "model_orifices") or self.reset:
            self.model_orifices = self["v2_orifice"]
        return self.model_orifices

    @property
    def culverts(self):
        if not hasattr(self, "model_culverts") or self.reset:
            self.model_culverts = self["v2_culvert"]
        return self.model_culverts

    @property
    def calculation_point(self):
        if not hasattr(self, "model_calculation_point") or self.reset:
            self.model_calculation_point = self["v2_calculation_point"]
        return self.model_calculation_point

    @property
    def control(self):
        if not hasattr(self, "model_control") or self.reset:
            self.model_control = self["v2_control"]
        return self.model_control

    @property
    def control_group(self):
        if not hasattr(self, "model_control_group") or self.reset:
            self.model_control_group = self["v2_control_group"]
        return self.model_control_group

    @property
    def control_measure_group(self):
        if not hasattr(self, "model_control_measure_group") or self.reset:
            self.model_control_measure_group = self["v2_control_measure_group"]
        return self.model_control_measure_group

    @property
    def control_measure_map(self):
        if not hasattr(self, "model_control_measure_map") or self.reset:
            self.model_control_measure_map = self["v2_control_measure_map"]
        return self.model_control_measure_map

    @property
    def control_table(self):
        if not hasattr(self, "model_control_table") or self.reset:
            self.model_control_table = self["v2_control_table"]
        return self.model_control_table

    @property
    def control_memory(self):
        if not hasattr(self, "model_control_memory") or self.reset:
            self.model_control_memory = self["v2_control_memory"]
        return self.model_control_memory

    @property
    def dem(self):
        if self.has_existing_rasters:
            return self.rasters.dem

    @dem.setter
    def dem(self, raster):
        self.rastergroup["dem"] = raster

    @property
    def friction(self):
        return self.rasters.friction

    @friction.setter
    def friction(self, raster):
        self.rastergroup["friction"] = raster

    @property
    def interception(self):
        return self.rasters.interception

    @interception.setter
    def interception(self, raster):
        self.rastergroup["interception"] = raster

    @property
    def initial_waterlevel(self):
        return self.rasters.initial_waterlevel

    @initial_waterlevel.setter
    def initial_waterlevel(self, raster):
        self.rastergroup["initial_waterlevel"] = raster

    @property
    def infiltration(self):
        return self.rasters.infiltration

    @infiltration.setter
    def infiltration(self, raster):
        self.rastergroup["infiltration"] = raster

    @property
    def max_infiltration_capacity(self):
        return self.rasters.max_infiltration_capacity

    @max_infiltration_capacity.setter
    def max_infiltration_capacity(self, raster):
        self.rastergroup["max_infiltration_capacity"] = raster

    @property
    def node_view(self):
        if not hasattr(self, "node_views") or self.reset:
            self.node_views = create_node_view(self)
        return self.node_views

    def nodes_height(self):
        dem = self.dem
        dem.return_raster = True
        return sample_nodes(self, dem.reproject(4326))

    def nodes_sample(self, raster):
        return sample_nodes(self, raster)

    def filter(self, table, node_fid=None, code=None):
        """searches a certain table"""
        return search_table(table, node_fid, code)

    def spatial_filter(self, geometry):
        """filter the model on connection nodes"""
        nodes = self.nodes.spatial_filter(geometry)
        filtered = {}
        for table in self:
            filtered[table.name] = []
            for node in nodes:
                filtered[table.name].append(self.node_view[node.id])
        return filtered

    def derive_raster_extent(self, raster, threshold=0, idx=1):
        """polygonizes raster based on data/nodata"""
        self.raster_extent = raster.polygonize(quiet=False)
        return self.raster_extent

    def delete_tables(self, deletes=None, quiet=True):
        delete_tables(self, deletes, quiet)

    def delete_node(self, node_id, clear=True):
        """deletes the node and all its associates"""
        delete_node(self, node_id, clear)

    def clip(self, vector, rasters=True):
        """clips a model, including the rasters on a vector"""
        clip(self, vector, rasters)


def sample_nodes(model, raster):
    return {node.fid: raster.read(node.geometry) for node in model.nodes}


def search_table(table, node_fid=None, code=None):
    """should be a general fast search of a random field in a certain table"""
    if code:
        filtering = {"code": code}
    elif node_fid:
        filtering = {"fid": node_fid}

    if table.layer_name in TABLES["single"]:
        return table.filter(return_fid=True, **filtering)

    if table.layer_name in TABLES["start_end"]:
        if node_fid:
            start = table.filter(connection_node_start_id=node_fid, return_fid=True)
            end = table.filter(connection_node_end_id=node_fid, return_fid=True)
            return end + start
        elif code:
            return table.filter(return_fid=True, **filtering)


def create_node_view(model):
    """creates a dictionary based on node ids"""
    nodes = model.nodes
    nodes.set_table()
    node_table = nodes.table
    new_dict = {fid: {} for fid in node_table["fid"]}

    # add connection node info
    for i in range(0, nodes.count):
        new_dict[node_table["fid"][i]]["v2_connection_nodes"] = {
            key: node_table[key][i] for key in node_table
        }

    for table in tqdm(TABLES["single"] + TABLES["start_end"], position=0):
        model_table = model[table]
        model_table.set_table()

        add = model_table.table
        for i in range(len(model[table])):
            if table in TABLES["single"]:
                new_dict[add["connection_node_id"][i]][table] = {
                    key: add[key][i] for key in add
                }
            else:
                if add["connection_node_start_id"][i]:
                    new_dict[add["connection_node_start_id"][i]][table + "_start"] = {
                        key: add[key][i] for key in add
                    }
                if add["connection_node_end_id"][i]:
                    new_dict[add["connection_node_end_id"][i]][table + "_end"] = {
                        key: add[key][i] for key in add
                    }

    return new_dict


def clip(model: ThreediEdits, vector, rasters):
    """
    Clips a model based on the geometry

    Parameters
    ----------
    db : ThreediEdits
    geometry : ogr.Geometry

    Returns
    -------
    None.

    """
    # connection nodes
    for feature in vector:
        geometry = feature.geometry

        # Find connection nodes in the area
        nodes = model.nodes.spatial_filter(geometry, return_fid=True)
        total_nodes = model.nodes.fids
        delete_nodes = list(set(total_nodes) - set(nodes))

        deletes = {k: [] for k in TABLES["order"]}
        for node in delete_nodes:
            for table, values in delete_node(model, node, clear=False).items():
                deletes[table].extend(values)

        unique = {k: list(set(v)) for k, v in deletes.items()}
        model.delete_tables(unique, quiet=False)

        # non existing cross section locations
        for csl_id in model.channels.non_existing_cross_section_locations():
            model.cross_section_locations.delete(csl_id)

        # levees
        levees = model.levees.spatial_filter(geometry, return_fid=True)
        delete_levees = list(set(model.levees.fids) - set(levees))
        for delete_levee in delete_levees:
            model.levees.delete(delete_levee)

        grid_refinements = model.grid_refinements.spatial_filter(
            geometry, return_fid=True
        )
        delete_refinements = list(
            set(model.grid_refinements.fids) - set(grid_refinements)
        )
        for delete_refinement in delete_refinements:
            model.grid_refinements.delete(delete_refinement)

    if rasters:
        for scenario in model.scenarios:
            model.scenario = scenario
            group = model.rasters
            group.clip(vector)
            model.rasters = group


def delete_tables(model: ThreediEdits, deletes: dict = None, quiet=True):
    """
    Deletes features in tabels in the correct order
    Parameters
    ----------
    db : ThreediEdits
    deletes : dict
        dict with the table name and fids to delete e.g., {'v2_pipe': [1,2,3,4]}.
    quiet : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    None.

    """
    for table in TABLES["order"]:
        if deletes:
            if table not in deletes:
                continue

            fids = deletes[table]
        else:
            fids = model[table].fids

        for fid in fids:
            model[table].delete(fid)


def delete_node(db: ThreediEdits, node_id: int, clear=True):
    """
    Deletes a node and all its assciates
    """

    view = db.node_view[node_id]
    deletes = {k: [] for k in TABLES["order"]}
    for delete_table in deletes:
        for x in [
            delete_table,
            delete_table + "_start",
            delete_table + "_end",
        ]:
            if x in view:
                if not view[x]["fid"] in deletes[delete_table]:
                    deletes[delete_table].append(view[x]["fid"])

    # associates = [(i, deletes[i]) for i in deletes if len(deletes[i]) > 0]
    logger.info("Deleting associates f{associates}")

    if clear:
        db.delete_tables(deletes, quiet=True)
    else:
        return deletes
