
"""This is the entry point.

This script parses the input arguments, and depending on the selected
options, calls the relevant entry point function, i.e. scan() or 
assemble() with the parsed arguments. 
For more information on usage, run estare -h, or see the documentation.
"""
import argparse
from estare.src.modes import scan, assemble

       
parser = argparse.ArgumentParser(prog='estare', description='''Program for aligning and stacking 
astronomical photos.''', epilog='''estare is a Persian word for star.''')

sub_parsers = parser.add_subparsers()

# create the parser for the feature detection command
parse_feature = sub_parsers.add_parser('scan', help='''Scan an input image to find suitable features 
such as (a) bright star(s) that can be used for aligning multiple frames.''')

parse_feature.add_argument('--img1', action='store', type=str, required=True, \
                           help='Path and name of the reference image (base layer)')

parse_feature.add_argument('--img2', action='store', type=str, required=True, \
                           help='Path and name of the second image (top layer)')

parse_feature.add_argument('-i', '--info-only', action='store_true', \
                           help='''If specified, the properties of the 
                           input image will be printed to stdout, and the 
                           feature detection step will be skipped.''' )

parse_feature.add_argument('--save-pxs', '-x', action='store_true', help='''If set, the pixel values of the 
                                                                            feature(s) will be saved.''')
parse_feature.add_argument('--save-gif', '-g', action='store_true', help='''If set, the feature(s) will be 
                                                                            saved also in .png format.''')

parse_feature.set_defaults(func=scan)

parse_stack = sub_parsers.add_parser('stack', help='''This mode should normally be used after running 
the scan mode whereby alignment features are extracted. The stack mode uses the coordinates of two 
features, which are common in both frames, to align them. It then adjusts them and stacks them up. Two 
input images along with two identical features for each image are required.''')

parse_stack.add_argument('layer_1', help='Path and name of the reference image (base layer)')
parse_stack.add_argument('layer_2', help='Path and name of the second image (top layer)')
parse_stack.add_argument('feature_1', help='''Path and name of a .npy file containing the coordinates 
of the features in the reference layer''')
parse_stack.add_argument('feature_2', help='''Path and name of a .npy file containing the coordinates 
of the features in the second layer which will be lined up with the reference layer.''')

parse_stack.set_defaults(func=assemble)

args = parser.parse_args()


def main():
    args = parser.parse_args()
    args.func(args)   # call the default function

if __name__ == '__main__':
    main()
