import logging


def image_edge_definer(pixel_positions, boundaries, pixels_to_edge):
    # Mosaic image position coordinates are from the centre of each
    # image, according to Cockpit's absolute position
    position_on_mosaic = [pixel_positions[0] - boundaries[0, 0],
                          pixel_positions[1] - boundaries[0, 1]]
    start = (position_on_mosaic[0] - pixels_to_edge[0],
             position_on_mosaic[1] - pixels_to_edge[1])
    end = (position_on_mosaic[0] + pixels_to_edge[0],
           position_on_mosaic[1] + pixels_to_edge[1])
    logging.debug("Image edges defined as (%i, %i), (%i, %i)", *start, *end)
    return start, end


def marker_edge_definer(pixel_positions, boundaries, pixels_to_edge):
    # Markers position coordinates are from the top right corner
    # of each image, according to Cockpit's absolute position
    # NOTE: "top right" is according to the final display
    # directions NOT the pre-processed coordinates
    im_y_size = boundaries[1, 1] - boundaries[0, 1]
    position_on_mosaic = [pixel_positions[0] - boundaries[0, 0],
                          pixel_positions[1] - boundaries[0, 1]]
    start = (position_on_mosaic[0] - pixels_to_edge[0] * 2,
             im_y_size - (position_on_mosaic[1]))
    end = (position_on_mosaic[0],
           im_y_size - (position_on_mosaic[1] - pixels_to_edge[1] * 2))
    logging.debug("Marker edges defined as (%i, %i), (%i, %i)", *start, *end)
    return start, end
