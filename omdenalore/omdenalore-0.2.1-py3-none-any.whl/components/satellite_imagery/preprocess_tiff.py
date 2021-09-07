import imghdr
from pathlib import Path
import gdal


class SatelliteImage:
    """
    SatelliteImage class is used to preprocess satellite images

    :param path: Path of the input .tif image
    :type path: str
    :param parts: Splits the single image into smaller images with a total of (parts * parts) images returned
    :type parts: int

    :example:

    >>> si = SatelliteImage(
    >>>        path="sample.tif", parts=5
    >>> )
    >>> si.split()
    """

    def __init__(self, path: str, parts: int) -> None:
        self.path = path
        assert self.path != "", "Path cannot be empty"
        assert imghdr.what(self.path) == "tiff", "You need to pass a .tif image"
        self.dem = gdal.Open(self.path)
        self.gt = self.dem.GetGeoTransform()
        self.parts = parts
        assert self.parts != 0, "Parts needs to be greater than 0"
        self.dir = Path(self.path).parent

    def split(self) -> None:
        """Splits a single .tif image into multiple parts in the same directory

        This makes it easier for
        visualising and storing in memory compared to having a single large
        image
        """
        x_min = self.gt[0]
        y_max = self.gt[3]
        res = self.gt[1]
        x_len = res * self.dem.RasterXSize
        y_len = res * self.dem.RasterYSize
        x_div = self.parts
        y_div = self.parts
        x_size = x_len / x_div
        y_size = y_len / y_div
        x_steps = [x_min + x_size * i for i in range(x_div + 1)]
        y_steps = [y_max - y_size * i for i in range(y_div + 1)]

        for i in range(x_div):
            for j in range(y_div):
                xmin = x_steps[i]
                xmax = x_steps[i + 1]
                ymax = y_steps[j]
                ymin = y_steps[j + 1]
                print(f"xmin: {xmin}\nxmax: {xmax}\nymin: {ymin}\nymax: {ymax}")
                gdal.Warp(
                    f"{self.dir}/dem-{i}-{j}.tif",
                    self.dem,
                    outputBounds=(xmin, ymin, xmax, ymax),
                    dstNodata=-9999,
                )
        self.dem = None
