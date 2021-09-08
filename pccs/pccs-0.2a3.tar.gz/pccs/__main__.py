"""
Main entry point for the package
"""


import argparse

import colour
from colour.models import eotf_inverse_sRGB, eotf_sRGB
from colour.notation import munsell_colour_to_xyY, RGB_to_HEX
from colour.utilities import normalise_maximum
import numpy as np

from pccs import (pccs_colour_to_munsell_colour,
                  pccs_colour_to_pccs_specification,
                  pccs_specification_to_pccs_colour)


def main():

    parser = argparse.ArgumentParser(
        description='convert PCCS colour to Munsell colour and sRGB hex')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('colour', help='PCCS colour')
    args = parser.parse_args()

    pccs_colour = args.colour
    pccs_spec = pccs_colour_to_pccs_specification(pccs_colour)
    pccs_colour_short = pccs_specification_to_pccs_colour(pccs_spec)
    print(pccs_colour_short)
    pccs_colour_long = pccs_specification_to_pccs_colour(pccs_spec, long=True)
    print(pccs_colour_long)
    munsell_colour = pccs_colour_to_munsell_colour(pccs_colour)
    print(munsell_colour)
    xyy = munsell_colour_to_xyY(munsell_colour)
    if args.verbose:
        print(' xyY:', xyy)
    xyz = colour.xyY_to_XYZ(xyy)
    if args.verbose:
        print(' XYZ:', xyz)
    srgb = colour.XYZ_to_sRGB(xyz)
    if args.verbose:
        print('sRGB:', srgb)
    note = ''
    if np.any(srgb < 0):
        srgb = np.clip(srgb, 0, np.inf)
        note = ' (clipped)'
    if np.any(srgb > 1):
        srgb = eotf_inverse_sRGB(normalise_maximum(eotf_sRGB(srgb)))
        note = ' (normalized)'
    print(RGB_to_HEX(srgb) + note)


if __name__ == '__main__':
    main()
