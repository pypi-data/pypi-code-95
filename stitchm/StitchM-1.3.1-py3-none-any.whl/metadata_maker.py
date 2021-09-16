# -*- coding: utf-8 -*-
import numpy as np
import logging
import datetime

import oxdls

from .edge_definer import marker_edge_definer


class MetadataMaker():

    def __init__(self, image_name, unstitched, datatype):
        # Set up attributes and variables
        self.boundaries = unstitched.boundaries
        self.mosaic_centre = unstitched.mosaic_centre
        self.pix2edge = unstitched.pix2edge
        self.pixelsize = unstitched.pixel_size
        mosaic_dims = self.__get_mosaic_dims()
        x_position, y_position = self.__get_x_y_position(self.boundaries, mosaic_dims, unstitched.pixel_size)
        physical_mosaic_dims = [dim * unstitched.pixel_size for dim in mosaic_dims]
        date_time = datetime.datetime.fromtimestamp(unstitched.modified_timestamp).isoformat()  # formatted as: "yyyy-mm-ddThh:mm:ss"

        logging.info("Creating OME metadata")
        self.ox = oxdls.OMEXML()
        image = self.ox.image()
        image.set_Name(image_name)
        image.set_ID("Image:0")
        image.set_AcquisitionDate(date_time)

        pixels = image.Pixels
        pixels.set_DimensionOrder("XYZCT")
        pixels.set_ID("Pixels:0")
        pixels.set_PixelType(str(datatype))
        pixels.set_SizeX(mosaic_dims[0])
        pixels.set_SizeY(mosaic_dims[1])
        pixels.set_SizeZ(1)
        pixels.set_SizeC(1)
        pixels.set_SizeT(1)
        pixels.set_PhysicalSizeX(physical_mosaic_dims[0] * 1.e3)
        pixels.set_PhysicalSizeXUnit("nm")
        pixels.set_PhysicalSizeY(physical_mosaic_dims[1] * 1.e3)
        pixels.set_PhysicalSizeYUnit("nm")
        pixels.set_PhysicalSizeZ(1)  # Z doesn't have corresponding data
        pixels.set_PhysicalSizeZUnit("reference frame")
        pixels.set_tiffdata_count(1)
        pixels.set_plane_count(1)

        channel = pixels.channel(0)
        channel.set_ID("Channel:0:0")
        channel.set_Name("C:0")

        tiffdata = pixels.tiffdata(0)
        tiffdata.set_FirstC(0)
        tiffdata.set_FirstZ(0)
        tiffdata.set_FirstT(0)
        tiffdata.set_IFD(0)

        # Add plane/tiffdata
        plane = pixels.plane(0)
        plane.set_TheZ(0)
        plane.set_TheC(0)
        plane.set_TheT(0)
        plane.set_PositionXUnit("nm")
        plane.set_PositionYUnit("nm")
        plane.set_PositionZUnit("reference frame")
        plane.set_PositionX(x_position * 1.e3)
        plane.set_PositionY(y_position * 1.e3)
        plane.set_PositionZ(0)


    def add_markers(self, updated_image_name, markerfile):
        logging.info("Creating ROIs")
        markerlist, marker_numbers = self.__extract_markers(markerfile)

        no_of_markers = len(marker_numbers)

        image = self.ox.image(0)
        image.set_Name(updated_image_name)
        image.set_roiref_count(no_of_markers)
        self.ox.set_roi_count(no_of_markers)

        for count in range(0, no_of_markers, 1):
            start, end = marker_edge_definer(
               markerlist[count],
                self.boundaries,
                self.pix2edge
                )
            image.roiref(count).set_ID(marker_numbers[count])
            roi = self.ox.roi(count)
            roi.set_ID(marker_numbers[count])
            roi.set_Name(f"Marker {marker_numbers[count]}")

            rectangle = roi.Union.Rectangle()
            rectangle.set_ID(f"Shape:{count}:0")
            rectangle.set_Text(f"Area {marker_numbers[count]}")
            rectangle.set_TheZ(0)
            rectangle.set_TheC(0)
            rectangle.set_TheT(0)

            # Colour is set using RGBA to int conversion
            # RGB colours: Red=-16776961, Green=16711935, Blue=65535
            # Calculated the following function from https://docs.openmicroscopy.org/omero/5.5.1/developers/Python.html:
            # def rgba_to_int(red, green, blue, alpha=255):
            #     # Return the color as an Integer in RGBA encoding
            #     r = red << 24
            #     g = green << 16
            #     b = blue << 8
            #     a = alpha
            #     rgba_int = r+g+b+a
            #     if (rgba_int > (2**31-1)):       # convert to signed 32-bit int
            #         rgba_int = rgba_int - 2**32
            #     return rgba_int
            rectangle.set_StrokeColor(-16776961)  # Red
            rectangle.set_StrokeWidth(20)
            rectangle.set_X(start[0])
            rectangle.set_Y(start[1])
            rectangle.set_Width(end[0] - start[0])
            rectangle.set_Height(end[1] - start[1])

    def get(self, encoded=False):
        if self.ox is not None:
            if encoded:
                return self.ox.to_xml().encode()
            else:
                return self.ox
        logging.error("Cannot get metadata that has not yet been created.")
        return self.ox

    def __extract_markers(self, markerfile):
        # returns marker coordinates in pixels
        array = np.genfromtxt(markerfile, delimiter=",")
        marker_coordinates = []
        marker_numbers = []
        for count in range(len(array[:, 0])):
            x, y = array[count, 0:2]
            # x is flipped between image and marker coordinates
            x = ((-x - self.mosaic_centre[0]) / self.pixelsize)
            y = ((y - self.mosaic_centre[1]) / self.pixelsize)
            marker_coordinates.append((int(x), int(y)))
            marker_numbers.append(int(array[count, -1]))
        return marker_coordinates, marker_numbers

    @staticmethod
    def __get_x_y_position(boundaries, mosaic_dims, pixelsize):
        # (minimum position in x & y + half the image size) * pixel size to get physical positions
        x_position = (boundaries[0, 0] + (mosaic_dims[0] / 2)) * pixelsize
        y_position = (boundaries[0, 1] + (mosaic_dims[1] / 2)) * pixelsize
        return x_position, y_position

    def __get_mosaic_dims(self):
        # In pixels
        dim_x = (self.boundaries[1, 0] - self.boundaries[0, 0])
        dim_y = (self.boundaries[1, 1] - self.boundaries[0, 1])
        return [dim_x, dim_y]
