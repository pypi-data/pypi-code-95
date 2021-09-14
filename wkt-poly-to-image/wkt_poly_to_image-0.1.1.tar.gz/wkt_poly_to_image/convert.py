from typing import Union
from shapely.geometry import Polygon, MultiPolygon
import numpy as np
import rasterio
from rasterio import features


def convert_poly_to_image(
    poly: Union[Polygon, MultiPolygon],
    width: Union[int, None] = None,
    height: Union[int, None] = None,
) -> np.ndarray:
    """Turns a vector (Multi)Polygon into raster representation.

    Args:
        poly (Union[Polygon, MultiPolygon]): The input polygon geometry
        width (Union[int, None], optional): Optional width for the returned raster representation. Defaults to None.
        height (Union[int, None], optional): Optional height for the returned raster representation. Defaults to None.

    Returns:
        np.ndarray: A 2-dimensional raster representation of the vector (Multi)Polygon as a numpy array with a dtype of uint8. All points outside the (Multi)Polygon have a value of 0, all points inside the (Multi)Polygon have a value of 255.
    """

    if width is None:
        width = int(poly.bounds[2])
    if height is None:
        height = int(poly.bounds[3])
    if not poly.is_valid:
        poly = repair(poly)
    return features.rasterize((poly, 255), out_shape=(height, width))


# at some point get a better repair process (maybe using my Rust code)
def repair(poly: Union[Polygon, MultiPolygon]) -> Union[Polygon, MultiPolygon]:
    if poly.geom_type.lower() == "multipolygon":
        return repair_multipolygon(poly)
    return repair_polygon(poly)


def repair_multipolygon(poly: MultiPolygon) -> MultiPolygon:
    first_pass = poly.buffer(0)
    if first_pass.is_valid:
        return first_pass

    second_pass = []
    for p in poly:
        if not p.is_valid:
            corrected = repair_polygon(p)
            second_pass.append(corrected)
            continue
        second_pass.append(p)
    return MultiPolygon(second_pass)


def repair_polygon(poly: Polygon) -> Union[Polygon, MultiPolygon]:
    buffered = poly.buffer(0)
    if buffered.is_valid:
        return buffered

    second_pass = []
    corrected = poly.buffer(-1)
    reconstituted = corrected.buffer(1)
    if reconstituted.geom_type.lower() == "polygon":
        reconstituted = [reconstituted]
    for r in reconstituted:
        second_pass.append(r)
    return MultiPolygon(second_pass)
