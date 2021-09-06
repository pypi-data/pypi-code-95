# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.
"""
Rextract, the king of extractors.
Extract parts of lizard rasters using geometries from a shapefile.
Please note that any information about the spatial reference system in the
shapefile is ignored.
If something goes wrong due to a problem on one of the lizard servers, it may
be possible to resume the process by keeping the output folder intact and
retrying exactly the same command.

from raster-tools
"""

# from http.client import responses
from time import sleep

import contextlib
import http
import pathlib
import requests
import uuid as uid
import numpy as np
import logging
from osgeo import gdal

from threedi_raster_edits.gis.dataset import Dataset
from threedi_raster_edits.gis.layer import Layer
from threedi_raster_edits.gis.geotransform import GeoTransform
from threedi_raster_edits.utils.project import Progress


MAX_THREADS = 1  # if set to 0 there will be no limit on the amount of threads

# urls and the like
API_URL = "https://%s.lizard.net/api/v4/rasters/"

# gdal drivers and options
MEM_DRIVER = gdal.GetDriverByName("mem")
TIF_DRIVER = gdal.GetDriverByName("gtiff")
TIF_OPTIONS = [
    "TILED=YES",
    "BIGTIFF=YES",
    "SPARSE_OK=TRUE",
    "COMPRESS=DEFLATE",
]

# dtype argument lookups
DTYPES = {
    "u1": gdal.GDT_Byte,
    "u2": gdal.GDT_UInt16,
    "u4": gdal.GDT_UInt32,
    "i2": gdal.GDT_Int16,
    "i4": gdal.GDT_Int32,
    "f4": gdal.GDT_Float32,
}

# argument defaults
TIMESTAMP = "1970-01-01T00:00:00Z"
ATTRIBUTE = "name"
SRS = "EPSG:28992"
CELLSIZE = 0.5
DTYPE = "f4"
SUBDOMAIN = "demo"
FILL_VALUE = -9999

# sleep and retry
STATUS_RETRY_SECONDS = {
    http.HTTPStatus.SERVICE_UNAVAILABLE: 10,
    http.HTTPStatus.GATEWAY_TIMEOUT: 0,
}
RETRY_SLEEP = 10
INTER_REQUEST_SLEEP = 2
AUTH = {}

# logging

logger = logging.getLogger(__name__)


def set_api_key(api_key):
    AUTH["api_key"] = api_key


def get_api_key():
    return AUTH["api_key"]


class Indicator:
    def __init__(self, path):
        self.path = str(path)

    def get(self):
        try:
            with open(self.path) as f:
                return int(f.read())
        except IOError:
            return 0

    def set(self, value):
        with open(self.path, "w") as f:
            f.write("%s\n" % value)


class Index:
    """Iterates the indices into the target dataset."""

    def __init__(self, dataset, geometry):
        """
        Rasterize geometry into target dataset extent to find relevant
        blocks.
        """
        width, height = dataset.GetRasterBand(1).GetBlockSize()
        geo_transform = GeoTransform(dataset.GetGeoTransform())

        # create an array in which each cell represents a dataset block
        shape = (
            (dataset.RasterYSize - 1) // height + 1,
            (dataset.RasterXSize - 1) // width + 1,
        )
        index = np.zeros(shape, dtype="u1")
        kwargs = {
            "geotransform": geo_transform.scaled(width, height),
            "spatial_reference": dataset.GetProjection(),
        }

        # find active blocks by rasterizing geometry
        options = ["all_touched=true"]
        with Layer(geometry) as layer:
            with Dataset(index[np.newaxis], **kwargs) as ds_idx:
                gdal.RasterizeLayer(
                    ds_idx,
                    [1],
                    layer,
                    burn_values=[1],
                    options=options,
                )

        # store as attributes
        self.block_size = width, height
        self.dataset_size = dataset.RasterXSize, dataset.RasterYSize
        self.geo_transform = geo_transform
        self.indices = index.nonzero()

    def _get_indices(self, serial):
        """Return indices into dataset."""
        block_width, block_height = self.block_size
        ds_width, ds_height = self.dataset_size
        y, x = self.indices[0][serial].item(), self.indices[1][serial].item()
        x1 = block_width * x
        y1 = block_height * y
        x2 = min(ds_width, (x + 1) * block_width)
        y2 = min(ds_height, (y + 1) * block_height)
        return x1, y1, x2, y2

    def _get_bbox(self, indices):
        """Return bbox tuple for a rectangle."""
        u1, v1, u2, v2 = indices
        p, a, b, q, c, d = self.geo_transform
        x1 = p + a * u1 + b * v1
        y2 = q + c * u1 + d * v1
        x2 = p + a * u2 + b * v2
        y1 = q + c * u2 + d * v2
        return "%s,%s,%s,%s" % (x1, y1, x2, y2)

    def __len__(self):
        return len(self.indices[0])

    def get_chunks(self, start=1):
        """
        Return chunk generator.
        Note that the serial number starts counting at 1.
        """
        for serial in range(start, len(self) + 1):
            x1, y1, x2, y2 = indices = self._get_indices(serial - 1)
            width, height, origin = x2 - x1, y2 - y1, (x1, y1)
            bbox = self._get_bbox(indices)
            yield Chunk(
                bbox=bbox,
                width=width,
                height=height,
                origin=origin,
                serial=serial,
            )


class Target:
    """
    Wraps the resulting gdal dataset.
    """

    def __init__(self, path, geometry, dtype, fillvalue, **kwargs):
        """Kwargs contain cellsize and uuid."""
        # coordinates
        self.geometry = geometry
        path = pathlib.Path(path)

        # types
        self.dtype = dtype
        if fillvalue is None:
            # pick the largest value possible within the dtype
            info = np.finfo if dtype.startswith("f") else np.iinfo
            self.fillvalue = info(dtype).max.item()
        else:
            # cast the string dtype to the correct python type
            self.fillvalue = np.dtype(self.dtype).type(fillvalue).item()

        # dataset
        if path.exists():
            print("Appending to %s... " % path, end="")
            self.dataset = gdal.Open(str(path), gdal.GA_Update)
        else:
            print("Creating %s" % path)
            self.dataset = self._create_dataset(path=str(path), **kwargs)

        # chunks
        self.index = Index(dataset=self.dataset, geometry=self.geometry)

    def __len__(self):
        return len(self.index)

    @property
    def data_type(self):
        return DTYPES[self.dtype]

    @property
    def no_data_value(self):
        return self.fillvalue

    @property
    def projection(self):
        return self.geometry.GetSpatialReference().ExportToWkt()

    def _create_dataset(self, path, cellsize, subdomain, time, uuid):
        """Create output tif dataset."""
        # calculate
        a, b, c, d = cellsize, 0.0, 0.0, -cellsize
        x1, x2, y1, y2 = self.geometry.GetEnvelope()
        p, q = a * (x1 // a), d * (y2 // d)

        width = -int((p - x2) // a)
        height = -int((q - y1) // d)
        geo_transform = p, a, b, q, c, d

        # create
        dataset = TIF_DRIVER.Create(
            path,
            width,
            height,
            1,
            self.data_type,
            options=TIF_OPTIONS,
        )
        dataset.SetProjection(self.projection)
        dataset.SetGeoTransform(geo_transform)
        dataset.GetRasterBand(1).SetNoDataValue(self.no_data_value)

        # meta
        dataset.SetMetadata(
            {"subdomain": subdomain, "time": time, "uuid": uuid},
        )

        return dataset

    def get_chunks(self, start):
        return self.index.get_chunks(start)

    def save(self, chunk):
        """ """
        # read and convert datatype
        with chunk.as_dataset() as dataset:
            band = dataset.GetRasterBand(1)
            active = band.GetMaskBand().ReadAsArray()[np.newaxis]
            array = band.ReadAsArray().astype(self.dtype)[np.newaxis]
        # determine inside pixels
        inside = np.zeros_like(active)
        kwargs = {
            "geotransform": dataset.GetGeoTransform(),
            "spatial_reference": dataset.GetProjection(),
        }
        with Layer(self.geometry) as layer:
            with Dataset(inside, **kwargs) as dataset:
                gdal.RasterizeLayer(dataset, [1], layer, burn_values=[255])

        # mask outide or inactive
        array[~np.logical_and(active, inside)] = self.no_data_value

        # write to target dataset
        kwargs.update(nodata_value=self.no_data_value)
        with Dataset(array, **kwargs) as dataset:
            data = dataset.ReadRaster(0, 0, chunk.width, chunk.height)
            args = chunk.origin + (chunk.width, chunk.height, data)
        self.dataset.WriteRaster(*args)


class Chunk(object):
    def __init__(self, bbox, width, height, origin, serial):
        # for request
        self.bbox = bbox
        self.width = width
        self.height = height

        # for result
        self.origin = origin
        self.serial = serial

        # the geotiff data
        self.response = None

    def fetch(self, subdomain, uuid, time, srs):
        request = {
            "url": API_URL % subdomain + uuid + "/data/",
            "params": {
                "start": time,
                "bbox": self.bbox,
                "projection": srs,
                "width": self.width,
                "height": self.height,
                "format": "geotiff",
            },
        }
        self.response = requests.get(**request, auth=("__key__", get_api_key()))
        logger.info(self.response.url)

    @contextlib.contextmanager
    def as_dataset(self):
        """Temporily serve data as geotiff file in virtual memory."""
        mem_file = f"/vsimem/{uid.uuid4()}.tif"
        gdal.FileFromMemBuffer(mem_file, self.response.content)
        yield gdal.Open(mem_file)


class RasterExtraction:
    """
    Represent the extraction of a single geometry.
    """

    def __init__(
        self,
        api_key,
        srs="EPSG:28992",
        retries=100,
        subdomain=SUBDOMAIN,
        quiet=False,
        fillvalue=FILL_VALUE,
        dtype=DTYPE,
        inter_request_sleep=INTER_REQUEST_SLEEP,
    ):

        self.srs = srs
        self.subdomain = subdomain
        self.retries = retries
        self.quiet = quiet
        self.fillvalue = fillvalue
        self.dtype = dtype
        self.inter_request_sleep = inter_request_sleep

        set_api_key(api_key)

        self.check_login(subdomain)

    def process(self, path, uuid, time, cellsize, geometry):
        """
        Extract for a single feature.
        :param session: requests.Sesssion object, logged in.
        :param srs: str defining spatial reference system
        :param time: ISO-8601 timestamp
        :param uuid: Lizard raster UUID

        Simple variant, wo threading
        """
        self.geometry = geometry

        kwargs = {
            "uuid": uuid,
            "time": time,
            "cellsize": cellsize,
            "subdomain": self.subdomain,
        }

        self.target = Target(path, self.geometry, self.dtype, self.fillvalue, **kwargs)
        self.indicator = Indicator(path=path.replace(".tif", ".pro"))

        completed = self.indicator.get()

        total = len(self.target)
        if completed == total:
            print("Already complete.")
            return
        if completed > 0:
            print("Resuming from chunk %s." % completed)

        # run a thread that starts putting chunks with threads in a queue
        fetch_kwargs = {
            "subdomain": self.subdomain,
            "uuid": uuid,
            "time": time,
            "srs": self.srs,
        }

        pbar = Progress(total, "Rextract")
        attempts = 0

        for chunk in self.target.get_chunks(start=completed + 1):
            self.indicator.set(completed)

            chunk.fetch(**fetch_kwargs)
            while not chunk.response.status_code == 200:
                sleep(RETRY_SLEEP)
                print(f"Got response... {chunk.response}")
                print(
                    "Retrying...attempt {} of {}".format(
                        int(attempts), int(self.retries)
                    )
                )
                attempts += 1
                chunk.fetch(**fetch_kwargs)

            # when correct
            self.target.save(chunk)
            sleep(self.inter_request_sleep)

            pbar.update(self.quiet)
            completed = chunk.serial

    def run(self, path, uuid, geometry, time=TIMESTAMP, cellsize=CELLSIZE):
        self.process(path, uuid, time, cellsize, geometry)
        self.target = None

    def check_login(self, subdomain):
        session = requests.Session()
        post = session.post(url=API_URL % subdomain, auth=("__key__", get_api_key()))

        if post.text != "login-reg":
            print("Login successful")
        else:
            print(post.text)

    # except Exception as e:
    #     print("Got Rextract exception: ", e)
    # finally:
    #     self.target = None
    #     print(f"Ended, written rextraction file to {path}")
