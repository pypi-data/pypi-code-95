from asfamcparser import ParseAMC
import argparse
from amccrop.amccrop import CheckArgs, parseToAmc, SaveAmc 
import sys

def main():
    """ The main routine"""

    parser = argparse.ArgumentParser(description='Crop AMC files using whole seconds intervals.')

    parser.add_argument("-i","--input",help="The selected amc file to crop.", required=True)
    parser.add_argument("-o","--output",help="The output amc file name.", required=True)
    parser.add_argument("-fps","--framerate",help="The frame rate of the amc file in seconds.", required=True, type=int)
    parser.add_argument("-s","--start",help="The start point in whole seconds", required=True, type=int)
    parser.add_argument("-e","--end",help="The end point in whole seconds", required=True, type=int)

    args = vars(parser.parse_args())

    amc = ParseAMC(f"{args['input']}.amc")

    if CheckArgs(args, amc.amc):
        # start frame
        startFrame = args["start"] * args["framerate"]
        # end frame
        endFrame = args["end"] * args["framerate"]
        # crop frame
        croppedFrames = amc.amc.frames[startFrame:endFrame]
        # parse cropped frames to amc format
        amcFile = parseToAmc(croppedFrames)
        # save new amc file
        SaveAmc(args["output"],amcFile)

if __name__ == "__main__":
    sys.exit(main())