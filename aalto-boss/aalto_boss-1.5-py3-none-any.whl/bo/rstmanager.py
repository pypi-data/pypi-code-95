import os.path
import numpy as np
import boss.io.ioutils as io
import boss.io.dump as dump


def split_rst_data(rst_data, dim):
    """Split the restart data into acquisitions and model parameters.

    Parameters
    ----------
    rst_data: np.ndarray
        The rst_data containing rows of (X, y, theta),
        e.g., as returned by parse_input_data.
    dim: int
        The dimension of the X-data.

    Returns
    -------
    acqs: np.ndarray
        Array containing the interation number (starting from 1) and the correspoding
        acquisitions found in the restart data.
    mod_par: np.ndarray
        Array containing the interation number (starting from 1) and the correspoding
        model parameters found in the restart data.
    """
    totalpts = rst_data.shape[0]
    # The number of input pts w/o mod param values is the number of rows with at most
    # dim + 1 entries that are not np.nan.
    inputpts = np.sum(np.sum(~np.isnan(rst_data), axis=1) <= dim + 1)
    acqs = np.c_[np.arange(1, totalpts + 1), rst_data[:, : dim + 1]]
    if totalpts > inputpts:
        mod_par = np.c_[
            np.arange(inputpts + 1, totalpts + 1),
            rst_data[inputpts:, dim + 1 :],
        ]
    else:
        mod_par = np.array([])
    return acqs, mod_par


class RstManager:
    """
    A class that handles restart-files (rst-files). These files can be used to
        1) introduce acquisition data from another source as initial values,
        2) continue a run that has been interrupted for some reason,
        3) continue a finished run by acquiring more points or
        4) keep the acquisitions but change the model or settings for a rerun.
    """

    def __init__(self, settings, rst_data=None):
        """
        Initializes the class with an array (settings.rstvals) containing the data
        read from an rst-file.
        """
        if rst_data is None:
            rst_data = np.array([])
        self.data = rst_data
        self.settings = settings
        self.x_dim = settings.dim
        self.use_gradients = settings["ygrads"]
        self.rstfile = settings["rstfile"]

    def new_file(self):
        if os.path.isfile(self.rstfile):
            print("warning: overwriting file '" + self.rstfile + "'")
        dump.dump_input_file(self.rstfile, self.settings, results_header=True)

    def get_x(self, i):
        """
        Returns the i:th acquisition location from the rst-data or None if
        it can't be found.
        """
        if (
            self.data.shape[0] > i
            and self.data.shape[1] >= self.x_dim
            and np.sum(np.isnan(self.data[i, 0 : self.x_dim])) == 0
        ):
            x_new = self.data[i, 0 : self.x_dim]
            return x_new
        else:
            return None

    def get_y(self, i):
        """
        Returns the i:th acquisition evaluation (energy and gradient) from the
        rst-data or None if it can't be found.
        """
        len_x = self.x_dim  # for convenience
        len_y = 1
        if self.use_gradients:
            len_y += len_x
        y_new = None
        yd_new = None
        # Actual functionality:
        if (
            self.data.shape[0] > i
            and self.data.shape[1] >= len_x + len_y
            and sum(np.isnan(self.data[i, len_x : (len_x + len_y)])) == 0
        ):
            y_new = self.data[i, len_x]
            if self.use_gradients:
                yd_new = self.data[i, (len_x + 1) : (len_x + len_y)]
        if not self.use_gradients:
            return y_new
        else:
            return (y_new, yd_new)

    def get_theta(self, i, n):
        """
        Returns the model paramters at iteration i from the rst-data or None
        if they can't be found.
        """
        len_x = self.x_dim  # for convenience
        len_y = 1
        if self.use_gradients:
            len_y += len_x
        a = len_x + len_y

        # Actual functionality:
        if (
            self.data.shape[0] > i
            and self.data.shape[1] == a + n
            and np.sum(np.isnan(self.data[i, a : (a + n)]) == 0)
        ):
            return self.data[i, a : (a + n)]
        else:
            return None

    def new_data(self, x, y):
        """
        Outputs a new data point (x,y) to rst file.
        """
        rst = open(self.rstfile, "a")
        rst.write("\n" + io.data_line(x, y, fstr="%23.15E")[:-1])
        rst.close()

    def new_model_params(self, mod_param):
        """
        Outputs a new set of model parameters to rst file.
        """
        rst = open(self.rstfile, "a")
        rst.write("     " + io.data_line(mod_param, fstr="%23.15E")[:-1])
        rst.close()
