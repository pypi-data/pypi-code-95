#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  7 09:29:29 2021

@author: mike
"""
import os
import types
import numpy as np
import xarray as xr
import pandas as pd
from tethys_utils.titan import Titan
from tethys_utils.misc import parse_data_paths
# from shapely.geometry import shape, mapping, Point, box
import copy
# import rasterio
# import concurrent.futures
# from uuid import uuid4
# from dask.diagnostics import ProgressBar
import tethys_utils as tu
# from pathlib import Path
from glob import glob


###########################################
### Parameters

base_encoding = {'lon': {'dtype': 'int32', '_FillValue': -999999, 'scale_factor': 1e-07},
'lat': {'dtype': 'int32', '_FillValue': -999999, 'scale_factor': 1e-07},
'altitude': {'dtype': 'int32', '_FillValue': -9999, 'scale_factor': 0.001},
'time': {'_FillValue': -99999999, 'units': 'days since 1970-01-01 00:00:00'},
'height': {'dtype': 'int16', '_FillValue': -9999}}

############################################
### Functions


def split_grid(ds, x_size=None, y_size=None, n_intervals=None, x_name='lon', y_name='lat', mbytes_size=2000):
    """
    Function to split an n-dimensional dataset along the x and y dimensions. Optionally, add time and height dimensions if the array does not aready contain them.

    Parameters
    ----------
    ds : DataSet
        An xarray DataSet with at least x and y dimensions. It can have any number of dimensions, though it probably does not make much sense to have greater than 4 dimensions.
    x_size : int
        The size or length of the smaller grids in the x dimension.
    y_size : int
        The size or length of the smaller grids in the y dimension.
    x_name : str
        The x dimension name.
    y_name : str
        The y dimension name.

    Returns
    -------
    List of DataArrays
        The result contains none of the original attributes.
    """
    ## Get the dimension data
    # dims = ds.dims

    # Get other array info
    # x_index = dims[x_name]
    # y_index = dims[y_name]

    x_min = ds[x_name][0].values
    x_max = ds[x_name][-1].values
    y_min = ds[y_name][0].values
    y_max = ds[y_name][-1].values

    y_diff = ds[y_name].diff(y_name, 1).mean().round(5).values
    x_diff = ds[x_name].diff(x_name, 1).mean().round(5).values

    # Get the aranges of the dimensions
    if isinstance(x_size, int) and isinstance(y_size, int):
        x_range = np.arange(x_min, x_max+x_diff*x_size, x_diff*x_size) - x_diff/2
        y_range = np.arange(y_min, y_max+y_diff*y_size, y_diff*y_size) - y_diff/2

    else:
        if not isinstance(n_intervals, int):
            print('n_intervals will be calculated.')
            n_intervals = round(np.sqrt(ds.nbytes/(mbytes_size*1000000)))
        x_range = np.linspace(x_min, x_max, n_intervals+1, endpoint=True) - (x_diff/2)
        x_range[-1] = x_range[-1] + x_diff
        y_range = np.linspace(y_min, y_max, n_intervals+1, endpoint=True) - (y_diff/2)
        y_range[-1] = y_range[-1] + y_diff

    block_list = []
    for iy, y in enumerate(y_range[1:]):
        ds2 = ds.sel({y_name: slice(y_range[iy], y_range[iy+1])})
        for ix, x in enumerate(x_range[1:]):
            ds3 = ds2.sel({x_name: slice(x_range[ix], x_range[ix+1])})
            if not 0 in list(ds3.dims.values()):
                block_list.append(ds3)

    return block_list


def select_sample_points(grid, block_size=10):
    """

    """
    g1 = grid.isel(time=0, height=0, drop=True).copy().load()
    var1 = [v for v in list(g1.variables) if not v in ['lat', 'lon']][0]

    blocks = split_grid(g1, block_size, block_size)
    blocks1 = [b for b in blocks if int(b[var1].isnull().sum()) == 0]

    r1 = np.random.choice(range(len(blocks1)), 1)[0]

    block = blocks1[r1]

    lons = block['lon'].values
    lats = block['lat'].values

    # df1 = g1.to_dataframe().dropna().reset_index()
    # r1 = np.random.choice(range(len(df1)), samples, False)
    # df2 = df1.iloc[r1][['lon', 'lat']].reset_index(drop=True).copy()

    return lons, lats


def grid_checks(dims):
    """

    """
    if not 'lon' in dims:
        raise ValueError('lon must be a dimension.')
    if not 'lat' in dims:
        raise ValueError('lat must be a dimension.')
    if not 'time' in dims:
        raise ValueError("time must be a dimension.")
    if not 'height' in dims:
        raise ValueError("height must be a dimension.")


def iter_obj_sizes(lons_lats, grid, encoding):
    """

    """
    lons, lats = lons_lats

    block_size = len(lons)

    val1 = grid.sel(lon=lons, lat=lats).copy().load()

    for k, v in encoding.items():
            if k in val1:
                val1[k].encoding = v

    obj_sizes = {}
    for l in range(block_size):
        # print(l)
        lons1 = lons[:(l+1)]
        lats1 = lats[:(l+1)]

        val2 = val1.sel(lon=lons1, lat=lats1)
        obj_size1 = len(tu.processing.write_pkl_zstd(val2.to_netcdf()))

        obj_sizes.update({l+1: obj_size1})

    return obj_sizes




############################################
### Classes


class Processor(object):
    """

    """
    def __init__(self):
        """

        """
        # if isinstance(preprocessor, types.FunctionType):
        # self.preprocessor = preprocessor
        # if isinstance(postprocessor, types.FunctionType):
        # self.postprocessor = postprocessor
        # self.time = time
        # self.height = height

        pass


    def load_dataset_metadata(self, datasets):
        """

        """
        dataset_list = tu.processing.process_datasets(datasets)

        ds_dict = {ds['dataset_id']: ds for ds in dataset_list}

        setattr(self, 'dataset_list', dataset_list)
        setattr(self, 'datasets', ds_dict)

        ## Checks
        grid_bool = all([d['spatial_distribution'] == 'grid' for d in dataset_list])
        if not grid_bool:
            raise ValueError('All values of spatial_distribution in the datasets should be grid.')

        grouping_len = len(np.unique([d['grouping'] for d in dataset_list]))
        if grouping_len > 1:
            raise ValueError('All values of grouping in the datasets must be the same.')

        grouping = dataset_list[0]['grouping']

        # param_len = len(np.unique([d['parameter'] for d in dataset_list]))
        # if param_len > 1:
        #     raise ValueError('All values of parameter in the datasets must be the same.')

        setattr(self, 'grouping', grouping)

        return dataset_list


    def parse_paths(self, glob_obj, date_format=None, from_date=None, to_date=None):
        """

        """
        paths = parse_data_paths(glob_obj, date_format, from_date, to_date)

        self.source_data_paths = paths

        return paths


    def load_raw_grid(self, lon_dim_name, lat_dim_name, time_dim_name=None, chunks=None, parallel=True, preprocessor=None, postprocessor=None, **kwargs):
        """
        The processor takes a str path to one or many files that xr.open_mfdataset can open (e.g. netcdf) and runs a preprocessor and postprocessor (optionally) to provide the proper dimensions and names for the dataset. A Dataset can also be passed to data_path and this will skip the preprocessing step.
        """
        ## initial loading and processing
        # if isinstance(data_path, str):
        #     grid1 = xr.open_mfdataset(data_path, chunks=chunks, parallel=parallel, preprocess=preprocessor)

        # elif isinstance(data_path, list):
        #     if isinstance(data_path[0], str):
        #         paths = []
        #         [paths.extend(glob(p)) for p in data_path]
        #         paths.sort()
        #         grid1 = xr.open_mfdataset(paths, chunks=chunks, parallel=parallel, preprocess=preprocessor)
        #         data_path = paths.copy()
        #     else:
        #         raise TypeError('If data_path is a list, then it must be a list of str paths.')

        # elif isinstance(data_path, xr.Dataset):
        #     grid1 = data_path
        # else:
        #     raise TypeError('data_path must be a str path that xr.open_mfdataset can open or an xr.Dataset.')

        grid1 = xr.open_mfdataset(self.source_data_paths, chunks=chunks, parallel=parallel, preprocess=preprocessor)

        if isinstance(postprocessor, types.FunctionType):
            grid1 = postprocessor(grid1, **kwargs)

        ## add attributes
        self._dims = grid1.dims
        self._lon_dim_name = lon_dim_name
        self._lat_dim_name = lat_dim_name
        self._time_dim_name = time_dim_name
        self._preprocessor = preprocessor
        self._postprocessor = postprocessor
        self._kwargs = kwargs

        return grid1


    # def assess_input_grid(self, dataset_id, samples=900):
    #     """

    #     """
    #     ## checks
    #     if not dataset_id in self.datasets:
    #         raise ValueError('dataset_id not in datasets.')

    #     grid_checks(self._dims)

    #     ## some nice processing
    #     self._extract_results_distribution()


    def save_grid_chunks(self, output_path, block_size=None, block_size_multiplier=10):
        """

        """
        ## Checks
        grid_checks(self._dims)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        ## some nice processing
        if not hasattr(self, '_null_grid'):
            self._extract_null_grid()

        ## Parameters
        if block_size is None:
            obj_dict = self._obj_dict.copy()

            xy_chunk_size = int(obj_dict['block_size'] * block_size_multiplier)
        elif isinstance(block_size, int):
            xy_chunk_size = int(block_size * block_size_multiplier)

        chunks = {self._time_dim_name: self._dims['time'], self._lon_dim_name: xy_chunk_size, self._lat_dim_name: xy_chunk_size}

        ## Open grid
        grid1 = self.load_raw_grid(self._lon_dim_name, self._lat_dim_name, self._time_dim_name, chunks=chunks, parallel=True, preprocessor=self._preprocessor, postprocessor=self._postprocessor, **self._kwargs)

        ## Create the blocks
        block_list = split_grid(grid1, x_size=xy_chunk_size, y_size=xy_chunk_size, n_intervals=None, x_name='lon', y_name='lat', mbytes_size=1600)

        ## get null grid
        null_grid = self._null_grid

        ## Determine blocks that are not all null values
        null_list = split_grid(null_grid.to_dataset(), x_size=xy_chunk_size, y_size=xy_chunk_size, n_intervals=None, x_name='lon', y_name='lat', mbytes_size=1600)

        null_list1 = [bool(n1.null_grid.sum() != 0) for n1 in null_list]

        len1 = sum(null_list1)

        file_name_str = '{}_part_{:>0' + str(len(str(len1))) + 'd}.nc'

        print(str(len1) + ' grid block files will be saved.')

        block_list = [b for i, b in enumerate(block_list) if null_list1[i]]

        ## Determine which datasets are associated with the grid
        vars1 = [v for v in list(grid1.variables) if (not v in ('lon', 'lat')) and (len(grid1[v].dims) == 4)]
        dss = {ds['dataset_id']: list(ds['properties']['encoding'].keys())  for ds in self.dataset_list if ds['parameter'] in vars1}

        if len(dss) == 0:
            raise ValueError('No dataset metadata fit the dataset results.')

        for i, b in enumerate(block_list):
            c = b.copy()
            c.load()
            for ds_id, v in dss.items():
                file_name = file_name_str.format(ds_id, i+1)
                file_path = os.path.join(output_path, file_name)
                print(file_name)
                c[v].to_netcdf(file_path)
            c.close()
            c = None
            b.close()
            b = None

        grid1.close()
        grid1 = None


    def _select_sample_points(self, ds_vars, block_size=10):
        """

        """
        if isinstance(self._time_dim_name, str):
            chunks = {self._time_dim_name: 1}
        else:
            chunks = None

        grid1 = self.load_raw_grid(self._lon_dim_name, self._lat_dim_name, self._time_dim_name, chunks=chunks, parallel=True, preprocessor=self._preprocessor, postprocessor=self._postprocessor, **self._kwargs)
        grid1 = grid1[ds_vars]
        lons_lats = select_sample_points(grid1, block_size=block_size)

        self.sample_lons_lats = lons_lats

        grid1.close()
        grid1 = None

        return lons_lats


    def _extract_null_grid(self):
        """

        """
        if isinstance(self._time_dim_name, str):
            chunks = {self._time_dim_name: 1}
        else:
            chunks = None

        grid1 = self.load_raw_grid(self._lon_dim_name, self._lat_dim_name, self._time_dim_name, chunks=chunks, parallel=True, preprocessor=self._preprocessor, postprocessor=self._postprocessor, **self._kwargs)

        grid2 = grid1.isel(time=0, height=0, drop=True).copy()

        vars1 = [v for v in list(grid2.variables) if (not v in ('lon', 'lat')) and (len(grid2[v].dims) == 2)]
        grid3 = grid2[vars1[0]].load().notnull()
        grid3.name = 'null_grid'

        self._null_grid = grid3


    def determine_grid_block_size(self, min_size=1000, max_size=2000, block_size=10):
        """

        """
        ## checks
        # if not dataset_id in self.datasets:
        #     raise ValueError('dataset_id not in datasets.')

        grid_checks(self._dims)

        ## some nice processing
        self._extract_null_grid()

        ## iterate datasets
        ds_obj_sizes = {}

        dataset_list = copy.deepcopy(self.dataset_list)
        for dataset in dataset_list:
            dataset_id = dataset['dataset_id']
            print(dataset_id)

            dataset = self.datasets[dataset_id]
            dataset_enc = dataset['properties']['encoding']
            encoding = copy.deepcopy(base_encoding)
            encoding.update(dataset_enc)

            ds_vars = [list(ds['properties']['encoding'].keys())  for ds in self.dataset_list if ds['dataset_id'] == dataset_id][0]

            ## get sample points
            lons_lats = self._select_sample_points(ds_vars, block_size)

            # calc obj sizes
            grid1 = self.load_raw_grid(self._lon_dim_name, self._lat_dim_name, self._time_dim_name, chunks={self._time_dim_name: self._dims['time'], self._lon_dim_name: 1, self._lat_dim_name: 1}, parallel=True, preprocessor=self._preprocessor, postprocessor=self._postprocessor, **self._kwargs)

            grid2 = grid1[ds_vars]

            # Do a round of 4 for initial assessment
            obj_sizes = iter_obj_sizes(lons_lats, grid2, encoding)

            null_grid = self._null_grid
            n_stns = int(null_grid.sum())

            if (obj_sizes[1] > max_size*1000):
                block_size = 1
                mean_size = obj_sizes[1]
                obj_size = obj_sizes[1]

                [ds.update({'grouping': 'none'}) for ds in dataset_list]

                print('The results for this dataset should not be grouped and has been changed internally.')

            elif (obj_sizes[10] < min_size*1000):
                mean_size = obj_sizes[10]/100
                block_size = int(((max_size*1000)//mean_size)**0.5)
                obj_size = mean_size * block_size**2

            else:

                obj_sizes1 = {i: o for i, o in obj_sizes.items() if (o >  min_size*1000) and (o <  max_size*1000)}
                if len(obj_sizes1) == 0:
                    raise ValueError('No results for the block size. Widen the range of the min and max sizes.')

                block_size = max(obj_sizes1.keys())
                mean_size = obj_sizes[block_size]/(block_size**2)
                obj_size = obj_sizes[block_size]

                [ds.update({'grouping': 'blocks'}) for ds in dataset_list]

            print('block size estimate is ' + str(block_size))

            obj_dict = {'block_size': block_size, 'obj_size': obj_size, 'sum_obj_sizes': int(mean_size * n_stns), 'n_stations': n_stns}
            self._obj_dict = obj_dict

            _ = self.load_dataset_metadata(dataset_list)

            grid1.close()
            grid1 = None
            grid2.close()
            grid2 = None

            ds_obj_sizes.update({dataset_id: obj_dict})

        return ds_obj_sizes


class Grid(Titan):
    """

    """

    ## Initial import and assignment function
    # def __init__(self):
    #     """

    #     """
    #     # self._load_dataset_metadata = self.load_dataset_metadata
    #     # self._load_results = self.load_results

    #     # del self.load_dataset_metadata
    #     # delattr(Titan, 'load_dataset_metadata')
    #     # delattr(Titan, 'load_results')
    #     # if isinstance(preprocessor, types.FunctionType):
    #     # self.preprocessor = preprocessor
    #     # if isinstance(postprocessor, types.FunctionType):
    #     # self.postprocessor = postprocessor
    #     # self.time = time
    #     # self.height = height

    #     ## Assign grid resolution
    #     # y_diff = np.abs(null_grid['lat'].diff('lat', 1).mean().round(5).values)
    #     # x_diff = np.abs(null_grid['lon'].diff('lon', 1).mean().round(5).values)

    #     # grid_res = np.round(np.mean([y_diff, x_diff]), 5)

    #     pass


    def load_dataset_metadata(self, datasets):
        """

        """
        super().load_dataset_metadata(datasets)

        dataset_list = self.dataset_list

        ## Checks
        grid_bool = all([d['spatial_distribution'] == 'grid' for d in dataset_list])
        if not grid_bool:
            raise ValueError('All values of spatial_distribution in the datasets should be grid.')

        grouping_len = len(np.unique([d['grouping'] for d in dataset_list]))
        if grouping_len > 1:
            raise ValueError('All values of grouping in the datasets must be the same.')

        grouping = dataset_list[0]['grouping']

        # param_len = len(np.unique([d['parameter'] for d in dataset_list]))
        # if param_len > 1:
        #     raise ValueError('All values of parameter in the datasets must be the same.')

        setattr(self, 'grouping', grouping)

        return dataset_list


    def parse_paths(self, glob_obj, date_format=None, from_date=None, to_date=None):
        """

        """
        paths = parse_data_paths(glob_obj, date_format, from_date, to_date)

        self.source_data_paths = paths

        return paths


    def load_results(self, block_size, results=None, dataset_id=None, sum_closed='right', other_closed='left', discrete=True, other_attrs=None, other_encoding=None, run_date=None, skip_resampling=True):
        """

        """
        ## Open datasets
        if isinstance(results, list):
            # if isinstance(results[0], str):
            #     paths = []
            #     [paths.extend(glob(p)) for p in results]
            #     paths.sort()
            #     data_list = [xr.open_dataset(p) for p in paths if isinstance(p, str)]
            if isinstance(results[0], xr.Dataset):
                data_list = [xr.open_dataset(p) for p in results if isinstance(p, xr.Dataset)]
            else:
                raise TypeError('If results is a list, then it must be xr.Datasets.')
        # elif isinstance(results, str):
        #     paths = sorted(glob(results))
        #     data_list = [xr.open_dataset(p) for p in paths]
        elif isinstance(results, xr.Dataset):
            data_list = [results]
        else:
            try:
                data_list = [xr.open_dataset(p) for p in self.source_data_paths]
            except:
                raise TypeError('results must be a list of str/xr.Dataset, a xr.Dataset, or use the method parse_paths.')

        ## Determine dataset_ids
        if isinstance(dataset_id, str):
            data_dict = {dataset_id: data_list}
        else:
            if hasattr(self, 'source_data_paths'):
                ds_ids = set([os.path.split(p)[1].split('_part_')[0] for p in self.source_data_paths])
                data_dict = {ds: [] for ds in ds_ids}
                for i, p in enumerate(self.source_data_paths):
                    ds_id = os.path.split(p)[1].split('_part_')[0]
                    data_dict[ds_id].append(data_list[i])
            else:
                raise TypeError('If paths are not contained in results, then a dataset_id of a str must be passed.')

        ## Iterate through the datasets
        load_results = super().load_results

        for ds_id, data_list in data_dict.items():
            print(ds_id)

            n_files = len(data_list)

            for i, data in enumerate(data_list):
                print(str(i+1) + ' of ' + str(n_files) + ' chunks')
                data1 = data.copy()
                data1.load()
                data.close()
                data = None

                blocks = split_grid(data1, block_size, block_size)
                data1.close()
                data1 = None

                for block in blocks:
                    # Determine if all values are null
                    total_n_values = np.prod(list(block.dims.values()))
                    t1 = block.isnull().sum()
                    n_null = max([int(t1[t].values) for t in t1])

                    if n_null < total_n_values:
                        load_results(block, ds_id, sum_closed=sum_closed, other_closed=other_closed, discrete=discrete, other_attrs=other_attrs, other_encoding=other_encoding, run_date=run_date, skip_resampling=skip_resampling)


















