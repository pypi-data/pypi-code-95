"""#
Created on Fri Apr 26 16:39:50 2019

@author: chris.kerklaan

Vector wrapper used for GIS programming

Goals:
    1. Provide a better interface for ogr
    2. Provides a table and spatial index which grows and deletes with adding
    and deleting features
    3. Provides basic geoprocessing options: Clipping, dissolving etc.

TODO:
    1. Fids should be derived easier/faster
    2. Work on layer_name logics
Bugs:
    1. Multipart2singlepart does not write as single part file shape
    2. Coyp zorgt voor problemen met originele bestand

Important Notes on pointers:
    Datasource is your pointer, pointer always needs to be present when
    data is edited in layer
    When a feature is created the feature is the pointer.

    Due to this pointers, gdal ds, layers and features are kept in place,
    hence the classs are not an extension of the object but built on top of them.
    If working with pure ogr, make sure that pointer are available:

        lines = Vector(TEST_DIRECTORY+"lines.shp")
        works:
            layer = lines.layer
            feature=layer[0]
            feature.geometry().Clone()
        does not work:
            layer = lines.layer
            feature.geometry().Clone()

    Also:
        works:
            for geometry in multipartgeometry:
                geometry.GetArea()
        does not work:
            for geometry in multipartgeometry:
                function(geometry)

            def function(geometry):
                geometry.GetArea()

    Functions outside the class can only use ogr-functions

"""
# First-party imports
import os
import logging
import pathlib
import bisect
import operator

# Third party imports
from osgeo import osr, ogr, gdal

# Third party imports - not obligatory
try:
    import rtree

    HAS_RTREE = True
except ImportError:
    HAS_RTREE = False

# Local imports
from .geometry import (
    POLYGON,
    SINGLE_TYPES,
    SINGLE_TO_MULTIPLE,
    MULTI_TYPES,
    TRANSLATION as GEOMETRY_TRANSLATE,
    fix as fix_geometry,
    clip as clip_geometry,
    difference as difference_geometry,
    dissolve as dissolve_geometry,
)
from .geometries import Polygon
from .fields import Fields
from .spatial_reference import SpatialReference
from .feature import Feature
from threedi_raster_edits.utils.project import Progress

# Global DRIVERS
DRIVER_GDAL_MEM = gdal.GetDriverByName("MEM")
DRIVER_OGR_MEM = ogr.GetDriverByName("Memory")
DRIVERS_SQL = ["PostgreSQL", "GPKG"]
# options
gdal.SetConfigOption("SQLITE_LIST_ALL_TABLES", "YES")
gdal.SetConfigOption("PG_LIST_ALL_TABLES", "YES")

# Exceptions
gdal.SetConfigOption("CPL_LOG", "NUl")
ogr.UseExceptions()
gdal.UseExceptions()

# Memory counter
_mem_num = 0

# Logger
logger = logging.getLogger(__name__)


class Vector:
    """wrapper of ogr layer, input is ogr datasource, only one layer
    is expected
    """

    def __init__(
        self,
        path: str = None,
        layer_name=None,
        write=1,
        view=False,
        create_index=False,
        create_table=False,
        name=None,
        epsg=28992,
        ds=False,
    ):
        self.create_index = create_index
        self.create_table = create_table
        self.layer_name = layer_name
        self.view = view
        self.standard_epsg = epsg

        if ds:
            self.ds = path
        else:
            if not os.path.exists(path) and not "vsimem" in path:
                raise FileNotFoundError("Vector not found")

            pl = pathlib.Path(path)
            self.path = path
            self.ext = pl.suffix
            if self.ext == ".shp":
                layer_name = pl.stem
            self.ds = ogr.Open(path, write)

        # Check for layer name
        if not layer_name:
            try:
                self.layer = self.ds[0]
            except TypeError:
                raise FileNotFoundError("No layer name, please define")
            logger.debug("setting temp as layer name")
            self.layer_name = self.layer.GetName()
        else:
            self.layer_name = layer_name
            self.layer = self.ds.GetLayer(layer_name)

        # vector settings
        if not name:
            name = self.layer_name
        self.name = name

        self.has_rtree = HAS_RTREE
        self.info(self.layer)

        if "vsimem" in path:
            logger.debug("loading vector in memory")

    @classmethod
    def from_pg(cls, host, port, user, password, dbname, layer_name, **kwargs):
        """
        returns a class from a postgres database
        takes a {"host":"x", "port":"x", "password":"x",
                 "user":"x", "host":"x"}
        """
        ogr_pg = ("PG:host={} port={} user='{}'" "password='{}' dbname='{}'").format(
            host, port, user, password, dbname
        )

        return cls(ogr.Open(ogr_pg), layer_name, ds=True, **kwargs)

    @classmethod
    def from_ds(cls, ogr_ds: ogr.DataSource = None, **kwargs):
        """returns a class from datasource input"""
        return cls(ogr_ds, ds=True, **kwargs)

    @classmethod
    def from_mem_path(cls, path: str = None, **kwargs):
        """returns a class from a memory path"""
        return cls(ogr.Open(path), ds=True, **kwargs)

    @classmethod
    def from_scratch(cls, layer_name, geometry_type, epsg, **kwargs):
        """creates a layer from scratch"""
        ds, _ = mem_layer(layer_name, geometry_type=geometry_type, epsg=epsg)
        return cls(ds, layer_name, ds=True, **kwargs)

    def info(self, layer, **kwargs):
        """Returns info of an ogr layer(s)"""

        if layer:
            self.layer = layer
            self.original_count = self.count
        else:
            raise ValueError("Layer is None, check filename?")

        if len(kwargs) > 0:
            for key, value in kwargs.items():
                setattr(self, key, value)

        self.quiet = False
        settings = self.settings
        if not settings["view"]:
            if settings["create_index"]:
                self.set_index()

            if settings["create_table"]:
                self.set_table()

    def get_feature(self, fid):
        """helper for retrieving features"""
        return Feature(self.layer.GetFeature(fid), self.layer)

    def __iter__(self):
        self.reset()
        for i in self.layer:
            yield self.get_feature(i.GetFID())

    def __getitem__(self, i):
        return self.get_feature(i)

    def __len__(self):
        return self.layer.GetFeatureCount()

    def __setitem__(self, key, value):
        if key == "feature":
            self.set_feature(value)

    @property
    def layers(self):
        return [layer.GetName() for layer in self.ds]

    @property
    def extent(self):
        return self.layer.GetExtent()

    @property
    def count(self):
        self.reset()
        return self.layer.GetFeatureCount()

    @property
    def fields(self):
        return Fields(self.layer)

    @property
    def layer_defn(self):
        return self.layer.GetLayerDefn()

    @property
    def geometry_type(self):
        return self.layer.GetGeomType()

    @property
    def fids(self):
        return [x.fid for x in self]

    @property
    def fid_column(self):
        column = self.layer.GetFIDColumn()
        if column == "":
            return "id"
        return self.layer.GetFIDColumn()

    @property
    def driver(self):
        return self.ds.GetDriver().name

    @property
    def spatial_reference(self):
        sr = self.layer.GetSpatialRef()
        if not sr:
            return SpatialReference.from_epsg(self.standard_epsg)
        else:
            return SpatialReference.from_sr(sr)

    @property
    def epsg(self):
        return self.spatial_reference.epsg

    @property
    def extent_geometry(self):
        x1, x2, y1, y2 = self.layer.GetExtent()
        wkt = POLYGON.format(x1=x1, x2=x2, y1=y1, y2=y2)
        return Polygon(ogr.CreateGeometryFromWkt(wkt))

    @property
    def extent_area(self):
        return self.extent_geometry.GetArea()

    @property
    def settings(self):
        return {
            "create_index": self.create_index,
            "create_table": self.create_table,
            "view": self.view,
            "layer_name": self.layer_name,
            "epsg": self.epsg,
            "name": self.name,
        }

    @property
    def as_gdal_dataset(self):
        """gdal and ogr not always compatible, we have to use openex"""
        mem_ds = mem_path() + ".shp"
        self.write(mem_ds)
        return gdal.OpenEx(mem_ds)

    def reset(self):
        self.layer.ResetReading()

    def add_field(self, name, ogr_type, update_table=False):
        self.fields.add(name, ogr_type)

        if update_table or hasattr(self, "update_table"):
            self.table[name] = [None for table in self.table["fid"]]

    def delete_field(self, *field_names):
        for field_name in field_names:
            self.fields.delete(field_name)

    def add(
        self,
        feature=None,
        geometry=None,
        items={},
        fid=-1,
        update_index=False,
        update_table=False,
        skip=True,
    ):
        # unpack feature
        if isinstance(feature, Feature):
            geometry = feature.geometry
            items = feature.items

        # account for none attributes
        if len(items) != 0:
            keys = list(items.keys())
            for key in keys:
                if key not in self.fields.names:
                    if skip:
                        del items[key]
        if geometry:
            geometry = ogr_geometry(geometry)

        self.layer, fid = add_feature(self.layer, self.layer_defn, geometry, items, fid)

        if update_index or hasattr(self, "update_index"):
            self.add_index_feature(self.layer.GetFeature(fid))

        if update_table or hasattr(self, "update_table"):
            self.add_table_feature(self.layer.GetFeature(fid))

        return fid

    def delete(self, feature, update_table=False, update_index=False):
        """deletes by using feature ids
        Input can be a single feature id or of type Feature class
        """

        if type(feature) == int:
            feature = self[feature]

        feature = ogr_feature(feature)

        if self.driver == "PostgreSQL":
            self.layer.ResetReading()
            self.ds.StartTransaction()

        if update_index or hasattr(self, "update_index"):
            self.delete_index_feature(feature)

        if update_table or hasattr(self, "update_table"):
            self.delete_table_feature(feature)

        self.layer.DeleteFeature(feature.GetFID())

        if self.driver == "PostgreSQL":
            self.ds.CommitTransaction()

    def delete_all(self, update_index=False, update_table=False):
        self.reset()
        for feature in self:
            self.delete(feature, update_table, update_index)

        # actually deletes the features
        self.layer.SyncToDisk()
        self.ds.FlushCache()

        self.layer = None
        self.layer = self.ds.GetLayer(self.layer_name)

    def set_feature(self, feature):
        self.layer.SetFeature(ogr_feature(feature))

    def copy(
        self,
        geometry_type=None,
        shell=False,
        fields=True,
        index=True,
        table=True,
    ):
        """In memory ogr object, with features
        params:
            geometry_type: change the geometry type
            shell: Does not add the features
            fields: Set to True is fields have to be included
        """

        if type(geometry_type) == str:
            geometry_type = GEOMETRY_TRANSLATE[geometry_type]

        if not geometry_type:
            geometry_type = self.geometry_type

        ds, layer, path = mem_layer(
            self.layer_name,
            self.layer,
            geometry_type=geometry_type,
            shell=shell,
            fields=fields,
            sr=self.spatial_reference,
            return_path=True,
        )

        self.path = path
        settings = self.settings
        if index == False:
            settings["create_index"] = False

        if table == False:
            settings["create_table"] = False

        return Vector.from_ds(ds, **settings)

    def write(self, path, overwrite=False):
        """write is done by createing a new file and copying features"""

        driver_name = self.drivers()[pathlib.Path(path).suffix]
        driver = ogr.GetDriverByName(driver_name)

        if overwrite:
            if os.path.exists(path):
                driver.DeleteDataSource(path)

        # create output file
        out_ds = driver.CreateDataSource(path)
        out_layer = out_ds.CreateLayer(
            self.layer_name, self.spatial_reference, self.geometry_type
        )

        for i in range(self.layer_defn.GetFieldCount()):
            out_layer.CreateField(self.layer_defn.GetFieldDefn(i))

        for feature in self:
            if driver_name in DRIVERS_SQL:
                add_sql_feature(
                    out_ds,
                    feature.geometry,
                    feature.items,
                    self.layer_name,
                    self.geometry_type,
                    self.spatial_reference.epsg,
                    geometry_name="geom",
                )
            else:
                add_feature(
                    out_layer,
                    self.layer_defn,
                    ogr_geometry(feature.geometry),
                    feature.items,
                )

        out_layer = None
        out_ds.Destroy()

    def drivers(self):
        return driver_extension_mapping()

    def close(self):
        self.layer = None
        self.ds.Destroy()

    """tables and index"""

    def set_index(self):
        """sets the index if not exist"""
        if not hasattr(self, "idx") and self.has_rtree:
            self.create_index = True
            self.update_index = True
            self.idx = create_index(self.layer, self.quiet)

    def add_index_feature(self, feature):
        """adds a feature to the index"""
        ogr_feat = ogr_feature(feature)

        # if multiple geometry fields are present
        geometry = ogr_feat.geometry()
        if geometry == None:
            geometry = ogr_feat.GetGeomFieldRef(1)

        self.idx.insert(ogr_feat.GetFID(), geometry.GetEnvelope())

    def delete_index_feature(self, feature):
        """deletes a feature in the index the index"""

        ogr_feat = ogr_feature(feature)

        # if multiple geometry fields are present
        geometry = ogr_feat.geometry()
        if geometry == None:
            geometry = ogr_feat.GetGeomFieldRef(1)

        self.idx.delete(ogr_feat.GetFID(), geometry.GetEnvelope())

    def set_table(self):
        """sets the table if not exists"""
        if not hasattr(self, "table"):
            self.create_table = True
            self.update_table = True
            self.table_fields = self.fields.names + ["fid"]
            self.table = {field: [] for field in self.table_fields}

            p = Progress(self.count, "Table")
            for feature in self:
                self.add_table_feature(feature)
                p.update(self.quiet)

    def add_table_feature(self, feature: ogr.Feature):
        """updates the table using an ogr feature"""
        feature = ogr_feature(feature)
        feature_items = feature.items()
        for key, value in feature_items.items():
            self.table[key].append(value)
        self.table["fid"].append(feature.GetFID())

    def delete_table_feature(self, feature: ogr.Feature):
        """delete a feature in the table"""
        feature = ogr_feature(feature)
        idx = self.table["fid"].index(feature.GetFID())
        for key in self.table.keys():
            del self.table[key][idx]

    """spatial and table filters"""

    def spatial_filter(
        self,
        geometry,
        method="intersect",
        filter=False,
        return_fid=False,
        quiet=True,
    ):
        """Takes a geometry and returns fids based on method
        params:
            method: 'intersect' or 'within'
            filter: Setting a spatial filter on the layer
        """
        self.set_index()

        if filter:
            self.set_spatial_filter(geometry)

        fids = self.extent_intersects(geometry)

        if method == "extent":
            return fids

        fids = self.intersects(geometry, fids, method, quiet)

        if filter:
            self.set_spatial_filter(None)

        if return_fid:
            return list(fids)
        else:
            return [self.get_feature(i) for i in fids]

    def extent_intersects(self, geometry):
        """returns intersecting ids"""
        self.set_index()

        if self.has_rtree:
            return [i for i in self.idx.intersection(geometry.GetEnvelope())]
        else:
            return self.fids

    def intersects(self, geometry, fids, method="intersect", quiet=True):
        """returns intersecting of within fids
        params:
            method: 'intersect' or 'within'
        """
        output = []

        pbar = Progress(len(fids), method)
        for fid in fids:
            feature = self[fid]
            if method == "intersect":
                add = feature.geometry.Intersects(geometry)
            else:
                add = feature.geometry.Within(geometry)

            if add:
                output.append(feature.fid)

            pbar.update(quiet)
        return output

    def set_spatial_filter(self, geometry):
        self.layer.SetSpatialFilter(geometry)
        self.info(self.layer)

    def set_attribute_filter(self, key, value=None):
        if key is None:
            self.layer.SetAttributeFilter(None)
            return
        self.layer.SetAttributeFilter(f"{key} = {value}")

    def filter(self, return_fid=False, **filtering):
        """Params:
            fid_only: returns the fid only
            filtering: Can be a dictionary e.g.,:**{
                                        field1:field_value1
                                            }
                       Or filled in as argument e.g.,:
                           percentile=1,
                           klasse=100
        returns a list
        """
        self.set_table()

        # get first field
        for field_key, field_value in filtering.items():
            break

        if len(self.table) == 0:
            return []

        table_fids = self.table["fid"]
        loop_fids = table_fids
        for i, (field_key, field_value) in enumerate(filtering.items()):

            if i == 0:
                loop_table_values = self.table[field_key]
            else:
                table_values = self.table[field_key]
                loop_table_values = [
                    lookup_ordered(fid, table_fids, table_values) for fid in loop_fids
                ]

            loop_fids = lookup_unordered(field_value, loop_table_values, loop_fids)
        fids = set(loop_fids)

        if return_fid:
            return list(fids)
        else:
            return [self.get_feature(i) for i in fids]

    def rasterize(
        self,
        rows=None,
        columns=None,
        geotransform=None,
        resolution=None,
        nodata=-9999,
        field=None,
        all_touches=False,
        options=None,
        return_ds=False,
        data_type=gdal.GDT_Float32,
    ):
        """Rasterizes the vector as a boolean,
        If field or all touches is given that is used
        """

        if not columns and not rows:
            if not resolution:
                logger.error("please provide resolution")
                return
            x1, x2, y1, y2 = self.extent
            columns = int((x2 - x1) / resolution)
            rows = int((y2 - y1) / resolution)
            geotransform = (x1, resolution, 0, y2, 0, -resolution)

        return rasterize(
            self.layer,
            rows,
            columns,
            geotransform,
            self.spatial_reference.wkt,
            nodata,
            field,
            all_touches,
            options,
            return_ds,
            data_type,
        )

    def interpolate(
        self,
        field,
        resolution,
        algorithm="invdist",
        argument="power=2.0",
        nodata_value=-9999,
    ):
        """interpolates vector points using gdal grid
        https://gdal.org/programs/gdal_grid.html#interpolation-algorithms
        """
        logger.debug("vector - interpolate - Start")
        extent = self.extent
        width_pixels = int((extent[1] - extent[0]) / resolution)
        height_pixels = int((extent[3] - extent[2]) / resolution)
        grid_options = gdal.GridOptions(
            zfield=field,
            algorithm=f"{algorithm}:{argument}",
            width=width_pixels,
            height=height_pixels,
        )

        path = mem_path()
        ds = gdal.Grid(destName=path, srcDS=self.as_gdal_dataset, options=grid_options)

        band = ds.GetRasterBand(1)

        # set nodata value
        band.SetNoDataValue(-9999)
        band = None
        ds = None

        return gdal.Open(path)

    def pgupload(
        self,
        host,
        port,
        user,
        password,
        dbname,
        layer_name,
        schema="public",
        overwrite="yes",
        spatial_index="GIST",
        fid_column="ogc_fid",
        geometry_name="the_geom",
        force_multi=True,
        quiet=True,
    ):
        ogr_pg = ("PG:host={} port={} user='{}'" "password='{}' dbname='{}'").format(
            host, port, user, password, dbname
        )
        upload(
            ogr.Open(ogr_pg),
            self.layer,
            layer_name,
            schema,
            overwrite,
            spatial_index,
            fid_column,
            geometry_name,
            force_multi,
            quiet,
        )

    def fix(self, geometry_type=ogr.wkbMultiPolygon, quiet=True):
        """geometries are autmatically fixed when looping over features"""
        target = self.copy(shell=True, geometry_type=geometry_type)
        pbar = Progress(self.count, "Geometries fixes")
        for feature in self:
            target.add(feature)
            pbar.update(quiet)
        return target

    def clip(self, vector, quiet=True):
        return Vector.from_ds(clip(self.layer, vector.layer, quiet, self.has_rtree))

    def buffer(self, buffer_size, layer=None, quiet=True):
        return Vector.from_ds(buffer(self.layer, buffer_size, quiet))

    def dissolve(self, field=None, quiet=True):
        return Vector.from_ds(dissolve(self.layer, field, quiet))

    def difference(self, vector, quiet=True):
        return Vector.from_ds(
            difference(self.layer, vector.layer, quiet, self.has_rtree)
        )

    def to_single(self, quiet=True):
        return Vector.from_ds(multiparts_to_singleparts(self.layer, quiet))

    def centroid(self, layer=None, quiet=True):
        return Vector.from_ds(centroid(self.layer, quiet))

    def reproject(self, epsg, quiet=True):
        return Vector.from_ds(reproject(self.layer, epsg, quiet))

    def polygon_to_lines(self, quiet=True):
        return Vector.from_ds(polygon_to_lines(self.layer, quiet))

    def simplify(self, factor, quiet=True):
        return Vector.from_ds(simplify(self.layer, factor, quiet))


def ogr_feature(feature):
    """Translates a Feature to an ogr_feature"""
    try:
        feature = feature.ptr
    except Exception:
        pass
    return feature


def ogr_geometry(geometry):
    if hasattr(geometry, "ogr"):
        geometry = geometry.ogr
    return geometry


def lookup_unordered(value, table, lookup_table):
    """fastest way to lookup a value by using an index in a unordered list
    Looping over a list only once
    returns a list of matching values
    """

    values = []

    if value not in table:
        return values

    index = 0

    # last index of value in table
    end = len(table) - operator.indexOf(reversed(table), value) - 1

    # when the first value is the only one
    if end == 0:
        return [lookup_table[0]]

    while index <= end:
        index = table.index(value, index)
        values.append(lookup_table[index])
        index += 1

    return values


def lookup_ordered(value, table, lookup_table):
    """fastest way to returns a lookup table value for an ordered list given,
    using bisect
    table must be ordered
    if not unique only the first index is returned
    """
    return lookup_table[bisect.bisect_left(table, value)]


def mem_path():
    global _mem_num
    location = f"/vsimem/mem{_mem_num}"
    _mem_num += 1
    return location


def mem_ds():
    location = mem_path()
    mem_datasource = DRIVER_OGR_MEM.CreateDataSource(location)
    return mem_datasource, location


def mem_layer(
    layer_name: str,
    layer: ogr.Layer = None,
    geometry_type: int = None,
    epsg: int = None,
    sr: osr.SpatialReference = None,
    shell: bool = True,
    fields: bool = True,
    options: list = ["SPATIAL_INDEX=YES"],
    return_path: bool = False,
):
    """
    Standard creates a 'shell' of another layer,
    To create a new memory layer,
    or to creat a memory copy of a layer
    params:
        epsg/sr: one can choose between epsg/sr
        shell: if True, returns a shell with no  feature
        field: if False, returns a shell without the fields
    returns:
        ds : ogr.Datasource
    """
    ds, path = mem_ds()

    if not shell and layer is not None:
        ds.CopyLayer(layer, layer_name)
        if return_path:
            return ds, ds.GetLayerByName(layer_name), path
        else:
            return ds, ds.GetLayerByName(layer_name)

    if epsg:
        sr = SpatialReference.from_epsg(epsg)
    elif sr == None:
        sr = layer.GetSpatialRef()

    if not geometry_type and layer:
        geometry_type = layer.GetGeomType()

    new_layer = ds.CreateLayer(layer_name, sr, geometry_type, options)

    if fields and layer:
        layer_defn = layer.GetLayerDefn()
        for i in range(layer_defn.GetFieldCount()):
            new_layer.CreateField(layer_defn.GetFieldDefn(i))

    if return_path:
        return ds, new_layer, path
    else:
        return ds, new_layer


def create_index(layer, quiet=True):
    index = rtree.index.Index(interleaved=False)
    pbar = Progress(layer.GetFeatureCount(), "Rtree Index")
    layer.ResetReading()
    for feature in layer:
        if feature:
            geometry = feature.GetGeometryRef()
            if not geometry:
                geometry = feature.GetGeomFieldRef(1)
            if not geometry:
                continue
            xmin, xmax, ymin, ymax = geometry.GetEnvelope()
            index.insert(feature.GetFID(), (xmin, xmax, ymin, ymax))
        else:
            logger.debug(f"Skipping feature with id {feature.GetFID()}")
        pbar.update(quiet)
    return index


def add_feature(layer, layer_defn, geometry, attributes, fid=-1):
    """Append geometry and attributes as new feature"""
    feature = ogr.Feature(layer_defn)
    feature_count = layer.GetFeatureCount()

    if fid == -1:
        if feature_count == 0:
            fid = 0
        else:
            feature.SetFID(layer.GetFeatureCount() + 1)
    else:
        feature.SetFID(fid)

    if geometry != None:
        feature.SetGeometry(geometry)

    for key, value in attributes.items():
        try:
            feature[str(key)] = value
        except Exception as e:
            raise ValueError("error:", e, "key", key, "value", value)

    try:
        layer.CreateFeature(feature)
    except RuntimeError as e:
        raise RuntimeError("error:", e, "geom:", geometry, "attributes:", attributes)
    finally:
        fid = feature.GetFID()
        feature = None

    return layer, fid


def add_sql_feature(
    ds,
    geometry,
    attributes,
    layer_name,
    geometry_type,
    epsg,
    geometry_name="geom",
):
    """ugly method of creating an sql-insert statement, but it works"""

    # lower items
    pgitems = {}
    for key, value in attributes.items():
        new_key = str(key).lower().replace("-", "_")
        pgitems[new_key] = value

    # postgis keys
    pgkeys = tuple(list(pgitems.keys()) + [geometry_name])
    keysql = f"{pgkeys}".replace("'", "")

    # postgis geometry
    geometry = ogr.ForceTo(geometry, geometry_type)
    wkt = geometry.ExportToWkt()

    # account for null and postgis values
    pgvalues = []
    for value in pgitems.values():
        if value == None:
            pgvalues.append("NULL")
        else:
            pgvalues.append(str(value))

    # create sql
    insert_sql = f"INSERT INTO {layer_name}{keysql}"
    sqlvalues = f" VALUES ({pgvalues}".replace("[", "").replace("]", "")
    sqlvalues = sqlvalues + f", ST_GeomFromText('{wkt}', {epsg}));"
    sql = insert_sql + sqlvalues
    try:
        ds.ExecuteSQL(sql)
    except RuntimeError as e:
        raise ValueError(f"Error {e} with statement {sql}")


def rasterize(
    layer,
    rows,
    columns,
    geotransform,
    spatial_reference_wkt,
    nodata=-9999,
    field=None,
    all_touches=False,
    options=None,
    return_ds=False,
    data_type=gdal.GDT_Float32,
):
    target_ds = DRIVER_GDAL_MEM.Create("", columns, rows, 1, data_type)

    # set nodata
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(nodata)
    band.Fill(nodata)
    band.FlushCache()

    # set metadata
    target_ds.SetProjection(spatial_reference_wkt)
    target_ds.SetGeoTransform(geotransform)

    # set options
    gdal_options = []

    if field:
        print(field)
        gdal_options.append(f"ATTRIBUTE={field}")

    if all_touches:
        gdal_options.append("ALL_TOUCHES=TRUE")

    if options:
        gdal_options.extend(options)

    if len(gdal_options) == 0:
        gdal.RasterizeLayer(target_ds, (1,), layer, burn_values=(1,))
    else:
        gdal.RasterizeLayer(target_ds, [1], layer, options=gdal_options)

    if return_ds:
        return target_ds
    else:
        array = target_ds.ReadAsArray()
        target_ds = None
        return array


def buffer(in_layer: ogr.Layer, buffer_size: float, quiet: bool = True):
    """Buffers a layer, output is always a polygon"""
    out_datasource, out_layer = mem_layer("buffer", in_layer, ogr.wkbPolygon)
    out_layer_defn = out_layer.GetLayerDefn()

    pbar = Progress(in_layer.GetFeatureCount(), "Buffer")
    in_layer.ResetReading()
    for out_feature in in_layer:
        pbar.update(quiet)
        geometry = out_feature.GetGeometryRef()
        geometry, valid = fix_geometry(geometry)
        if not valid:
            continue
        buffered_geometry = geometry.Buffer(buffer_size)
        items = out_feature.items()
        add_feature(out_layer, out_layer_defn, buffered_geometry, items)

    out_layer = None
    return out_datasource


def centroid(in_layer: ogr.Layer, quiet: bool = True):
    """Takes a ogr layer and returns a centroid ogr layer"""
    out_datasource, out_layer = mem_layer("centroid", in_layer, ogr.wkbPoint)
    out_layer_defn = out_layer.GetLayerDefn()

    pbar = Progress(in_layer.GetFeatureCount(), "Centroid")

    in_layer.ResetReading()
    for out_feat in in_layer:
        out_geom = out_feat.GetGeometryRef().Centroid()
        add_feature(out_layer, out_layer_defn, out_geom, out_feat.items())
        pbar.update(quiet)

    out_layer = None
    return out_datasource


def simplify(in_layer: ogr.Layer, simple_factor: float, quiet: bool = True):
    """Takes a layer and simplifies all geometryies, return ogr ds"""
    out_datasource, out_layer = mem_layer("simplify", in_layer)
    out_layer_defn = out_layer.GetLayerDefn()

    pbar = Progress(in_layer.GetFeatureCount(), "Simplify")
    in_layer.ResetReading()
    for out_feature in in_layer:
        items = out_feature.items()
        out_geometry = out_feature.GetGeometryRef().Simplify(simple_factor)
        add_feature(out_layer, out_layer_defn, out_geometry, items)
        pbar.update(quiet)

    out_layer = None
    return out_datasource


def multiparts_to_singleparts(in_layer: ogr.Layer, quiet=True):
    """converts multiparts to single parts"""
    geom_type = SINGLE_TYPES[in_layer.GetGeomType()]
    out_datasource, out_layer = mem_layer("multi2single", in_layer, geom_type)
    out_layer_defn = out_layer.GetLayerDefn()
    pbar = Progress(in_layer.GetFeatureCount(), "Multi2single")

    in_layer.ResetReading()
    for count, feature in enumerate(in_layer):
        items = feature.items()
        geometry = feature.GetGeometryRef()
        geometry, valid = fix_geometry(geometry)
        if not valid:
            continue
        if "MULTI" in geometry.GetGeometryName():
            for geometry_part in geometry:
                add_feature(out_layer, out_layer_defn, geometry_part, items)
        else:
            add_feature(out_layer, out_layer_defn, geometry, items)
        pbar.update(quiet)
    out_layer = None
    return out_datasource


def reproject(in_layer: ogr.Layer, epsg: int, quiet=True):
    """Takes an ogr layer, reprojects and returns an ogr datasource"""
    in_spatial_ref = in_layer.GetSpatialRef()
    spatial_ref_out = osr.SpatialReference()
    spatial_ref_out.ImportFromEPSG(int(epsg))

    out_datasource, out_layer = mem_layer("reproject", in_layer, epsg=epsg)
    out_layer_defn = out_layer.GetLayerDefn()
    reproject = osr.CoordinateTransformation(in_spatial_ref, spatial_ref_out)

    pbar = Progress(in_layer.GetFeatureCount(), "Reproject")
    for feature in in_layer:
        pbar.update(quiet)
        geometry = feature.GetGeometryRef()
        geometry.Transform(reproject)
        add_feature(out_layer, out_layer_defn, geometry, feature.items())
    out_layer = None
    return out_datasource


def polygon_to_lines(in_layer: ogr.Layer, quiet=True):
    """Takes a polygon in layer and returns a linestring ogr datsource"""
    out_datasource, out_layer = mem_layer("poly2lines", in_layer, ogr.wkbLineString)
    out_layer_defn = out_layer.GetLayerDefn()

    pbar = Progress(in_layer.GetFeatureCount(), "Poly2lines")
    in_layer.ResetReading()
    for feature in in_layer:
        boundary = feature.geometry().Boundary()
        add_feature(out_layer, out_layer_defn, boundary, feature.items())
        pbar.update(quiet)

    out_layer = None
    return out_datasource


def dissolve(in_layer: ogr.Layer, field=None, quiet=True):
    """
    Dissolved the vector layer into a single multipolygon feature.
    Value can be filled to used certain field.
    """

    out_datasource, out_layer = mem_layer("dissolve", in_layer)
    out_layer_defn = out_layer.GetLayerDefn()
    geom_type = in_layer.GetGeomType()
    multi_type = MULTI_TYPES[geom_type]
    in_layer.ResetReading()
    if field:
        unique = {feature[field]: [] for feature in in_layer}
        in_layer.ResetReading()
        for feature in in_layer:
            unique[feature[field]].append(feature.GetFID())

        pbar = Progress(len(unique), f"Dissolve field {field}")
        for field_value, fid_list in unique.items():
            multi = ogr.Geometry(multi_type)
            for fid in fid_list:
                feature = in_layer[fid]
                geometry, valid = fix_geometry(feature.GetGeometryRef())
                if not valid:
                    continue
                multi.AddGeometry(geometry)

            dissolved = dissolve_geometry(multi)
            add_feature(out_layer, out_layer_defn, dissolved, {})
            pbar.update(quiet)

    else:
        pbar = Progress(in_layer.GetFeatureCount(), "Dissolve")
        multi = ogr.Geometry(multi_type)
        in_layer.ResetReading()
        for feature in in_layer:
            geometry, valid = fix_geometry(feature.GetGeometryRef())
            if not valid:
                continue

            if geometry.GetGeometryType() > 3:  # multi
                for single_geom in geometry:
                    multi.AddGeometry(single_geom)
            else:
                multi.AddGeometry(geometry)
            pbar.update(quiet)

        add_feature(out_layer, out_layer_defn, dissolve_geometry(multi), {})

    out_layer = None
    return out_datasource


def difference(
    in_layer: ogr.Layer,
    mask_layer: ogr.Layer,
    quiet=True,
    use_rtree=True,
):
    """
    This function takes a difference between vector layer and difference layer.
    - Takes into account multiparts and single parts.
    - It also leaves geometries which are not valid.

    """
    in_layer_geom_type = in_layer.GetGeomType()

    if use_rtree:
        idx = create_index(mask_layer)

    geometry_types = SINGLE_TO_MULTIPLE[in_layer_geom_type]
    out_datasource, out_layer = mem_layer("difference", in_layer)
    in_layer_defn = in_layer.GetLayerDefn()
    pbar = Progress(in_layer.GetFeatureCount(), "Difference")

    in_layer.ResetReading()
    for in_feature in in_layer:
        pbar.update(quiet)

        if in_feature:
            in_items = in_feature.items()
            in_geom = in_feature.GetGeometryRef()

            if use_rtree:
                mask_ids = idx.intersection(in_geom.GetEnvelope())
                mask_features = [mask_layer.GetFeature(i) for i in mask_ids]
            else:
                mask_layer.SetSpatialFilter(in_geom)
                mask_features = [i for i in mask_layer]
                mask_layer.SetSpatialFilter(None)

            difference = None
            for loop, mask_feature in enumerate(mask_features):
                mask_geometry = mask_feature.GetGeometryRef()
                if loop == 0:
                    out = difference_geometry(in_geom, mask_geometry)
                else:
                    out = difference_geometry(difference, mask_geometry)

                if out:
                    difference = out

        if difference:
            diff_part_type = difference.GetGeometryType()
            if diff_part_type not in geometry_types:
                # Check if geometry collection
                if diff_part_type == ogr.wkbGeometryCollection:
                    for part in difference:
                        if part.GetGeometryType() == in_layer_geom_type:
                            add_feature(out_layer, in_layer_defn, part, in_items)
            else:  # geometry intersects, differenced and has correct geom type
                add_feature(out_layer, in_layer_defn, difference, in_items)

        else:  # geometry outside difference area
            add_feature(out_layer, in_layer_defn, in_geom, in_items)

    out_layer = None
    return out_datasource


def clip(
    in_layer: ogr.Layer,
    mask_layer: ogr.Layer,
    quiet: bool = True,
    use_rtree: bool = True,
):
    """Takes two ogr layer and returns a clipped layer"""
    out_datasource, out_layer = mem_layer("clip", in_layer)
    out_layer_defn = out_layer.GetLayerDefn()
    geom_type = in_layer.GetGeomType()

    if use_rtree:
        idx = create_index(mask_layer)

    pbar = Progress(in_layer.GetFeatureCount(), "Clip")
    in_layer.ResetReading()
    for in_feature in in_layer:
        pbar.update(quiet)
        in_geometry = in_feature.GetGeometryRef()

        if use_rtree:
            mask_ids = idx.intersection(in_geometry.GetEnvelope())
            mask_features = [mask_layer.GetFeature(i) for i in mask_ids]
        else:
            mask_layer.SetSpatialFilter(in_geometry)
            mask_features = [i for i in mask_layer]
            mask_layer.SetSpatialFilter(None)

        for mask_feature in mask_features:
            clipped_geometries = clip_geometry(
                in_geometry,
                mask_feature.GetGeometryRef(),
                output_type=geom_type,
            )

            if clipped_geometries:
                items = in_feature.items()
                for geometry in clipped_geometries:
                    add_feature(out_layer, out_layer_defn, geometry, items)

    return out_datasource


def merge(vector_path_list: list, simplify: float = 0, quiet=True):
    """merges list of vector paths and return as ogr datasource"""
    if type(vector_path_list[0]) == str:
        ds = ogr.Open(vector_path_list[0])
        layer = ds[0]
    else:
        ds = vector_path_list[0]
        layer = ds.layer

    geom_type = layer.GetGeomType()
    out_datasource, out_layer = mem_layer("merge", layer, geom_type)
    pbar = Progress(len(vector_path_list), "Poly2lines")
    for file in vector_path_list:
        pbar.update(quiet)
        if type(file) == str:
            ds = ogr.Open(file)
        else:
            ds = file.ds

        if ds is None:
            logger.error("dataset is None")
            continue

        layer = ds[0]
        layer_defn = layer.GetLayerDefn()

        layer.ResetReading()
        for feat in layer:
            if feat:
                geometry = feat.GetGeometryRef().Clone()
                geometry = geometry.Simplify(simplify)
                attributes = feat.items()
                add_feature(out_layer, layer_defn, geometry, attributes)
    return out_datasource


def upload(
    pgds: ogr.DataSource,
    layer: ogr.Layer,
    layer_name: str,
    schema="public",
    overwrite="YES",
    spatial_index="GIST",
    fid_column="ogc_fid",
    geometry_name="the_geom",
    force_multi=True,
    quiet=False,
):
    """Takes uploading the data to a postgres database with different features
    writing with sql-statements so that we can understand what is happening
    params:
        layer: input layer
        layer_name: writes to this name

    """

    options = [
        f"OVERWRITE={overwrite}",
        f"SCHEMA={schema}",
        f"SPATIAL_INDEX={spatial_index}",
        f"FID={fid_column}",
        f"GEOMETRY_NAME={geometry_name}",
    ]

    sr = layer.GetSpatialRef()
    sr.AutoIdentifyEPSG()
    epsg = int(sr.GetAttrValue("AUTHORITY", 1))

    geometry_type = MULTI_TYPES[layer.GetGeomType()]
    new_layer = pgds.CreateLayer(layer_name, sr, geometry_type, options)
    for x in range(layer.GetLayerDefn().GetFieldCount()):
        new_layer.CreateField(layer.GetLayerDefn().GetFieldDefn(x))
    new_layer = None

    layer.ResetReading()
    pbar = Progress(layer.GetFeatureCount(), "Upload")
    for loop, feature in enumerate(layer):
        add_sql_feature(
            pgds,
            feature.geometry(),
            feature.items(),
            layer_name,
            geometry_type,
            epsg,
            geometry_name,
        )
        pbar.update(quiet)


def driver_extension_mapping():
    """return driver extensions for ogr based on small name"""
    ext = {}
    for i in range(ogr.GetDriverCount()):
        drv = ogr.GetDriver(i)
        if (
            drv.GetMetadataItem("DCAP_VECTOR") == "YES"
            and drv.GetMetadataItem("DCAP_CREATE") == "YES"
        ):
            driver = drv.GetMetadataItem("DMD_EXTENSION")
            if driver:
                ext["." + driver] = drv.GetName()
    return ext
