import numpy as np
import xarray as xr
from tsdat.config import Config

from .file_handlers import AbstractFileHandler


class ZarrHandler(AbstractFileHandler):
    """FileHandler to read from and write to zarr files. Takes a number of
    parameters that are passed in from the storage config file. Parameters
    specified in the config file should follow the following example:

    .. code-block:: yaml

        parameters:
          write:
            to_zarr:
              # Parameters here will be passed to xr.Dataset.to_zarr()
          read:
            open_zarr:
              # Parameters here will be passed to xr.open_zarr()

    :param parameters:
        Parameters that were passed to the FileHandler when it was registered
        in the storage config file, defaults to {}.
    :type parameters: Dict, optional
    """

    def write(self, ds: xr.Dataset, filename: str, config: Config = None, **kwargs) -> None:
        """Saves the given dataset to a zarr file.

        :param ds: The dataset to save.
        :type ds: xr.Dataset
        :param filename: The path to where the file should be written to.
        :type filename: str
        :param config: Optional Config object, defaults to None
        :type config: Config, optional
        """
        write_params = self.parameters.get('write', {})
        to_zarr_kwargs = dict(format='NETCDF4')
        to_zarr_kwargs.update(write_params.get('to_zarr', {}))

        # We have to make sure that time variables do not have units set as attrs,
        # and instead have units set on the encoding or else xarray will crash
        # when trying to save:
        # https://github.com/pydata/xarray/issues/3739
        for variable_name in ds.variables:
            variable = ds[variable_name]
            if variable.values.dtype.type == np.datetime64:
                units = variable.attrs['units']
                del(variable.attrs['units'])
                variable.encoding['units'] = units

        ds.to_zarr(filename, **to_zarr_kwargs)

    def read(self, filename: str, **kwargs) -> xr.Dataset:
        """Reads in the given file and converts it into an Xarray dataset for
        use in the pipeline. 

        :param filename: The path to the file to read in.
        :type filename: str
        :return: A xr.Dataset object.
        :rtype: xr.Dataset
        """
        read_params = self.parameters.get('read', {})
        open_zarr_kwargs = read_params.get('open_zarr', {})
        return xr.open_zarr(filename, **open_zarr_kwargs)
