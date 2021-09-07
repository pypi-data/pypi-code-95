"""pccs.__main__

Main entry point for the package
"""


import argparse

import colour
from colour.notation import munsell_colour_to_xyY, RGB_to_HEX

from pccs import pccs_colour_to_munsell_colour


def main():

    parser = argparse.ArgumentParser(
        description='convert PCCS colour to Munsell colour and sRGB hex')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('colour', help='PCCS colour')
    args = parser.parse_args()

    pccs_colour = args.colour
    munsell_colour = pccs_colour_to_munsell_colour(pccs_colour)
    print(munsell_colour)
    xyy = munsell_colour_to_xyY(munsell_colour)
    if args.verbose:
        print('xyY:', xyy)
    xyz = colour.xyY_to_XYZ(xyy)
    if args.verbose:
        print('XYZ:', xyz)
    srgb = colour.XYZ_to_sRGB(xyz)
    if args.verbose:
        print('sRGB', srgb)
    print(RGB_to_HEX(srgb))


if __name__ == '__main__':
    main()
