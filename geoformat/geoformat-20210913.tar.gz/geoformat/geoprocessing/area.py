from geoformat.conversion.geometry_conversion import (
    geometry_to_geometry_collection,
    multi_geometry_to_single_geometry
)
from geoformat.geoprocessing.measure.area import shoelace_formula


def geometry_area(geometry):
    # initialize return
    area = 0

    # transform function to geometry collection
    geometry = geometry_to_geometry_collection(geometry)
    # if geometry is not empty
    if geometry:
        for geometry in geometry['geometries']:
            # if geometry is not a point or multipoint (they are no dimension then no length)
            if 'POLYGON' in geometry['type'].upper():
                # loop over part
                for geometry_part in multi_geometry_to_single_geometry(geometry, bbox=False):
                    coordinates_list = geometry_part['coordinates']
                    # if there is coordinates
                    if coordinates_list:
                        for i_ring, coordinates_ring in enumerate(coordinates_list):
                            ring_area = shoelace_formula(coordinates_ring)
                            if i_ring == 0:
                                area += ring_area
                            else:
                                area -= ring_area
        return area
