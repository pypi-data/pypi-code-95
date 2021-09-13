from typing import Tuple
from pathlib import Path


def CheckArgs(args:dict, amc) -> bool:
    # check output filename != input filename
    if args["input"] == args["output"]: raise ValueError("Output filename same as input. Cannot override original file.")
    # check output file dose not exist
    filePath = Path(f"{args['output']}.amc")
    if not filePath.is_file():
        # check fps greater than 0
        if args["framerate"] <= 0: raise ValueError("FPS needs to be greater than 0.")
        # check start point is greater than 0 and less than total
        if args["start"] < 0 or args["start"] > (amc.count/30):  raise ValueError("Start seconds out of range.")
        # check end point is greater than start point and less than total
        if args["end"] <= args["start"] or args["end"] > (amc.count/30):  raise ValueError("End seconds out of range.")
        return True
    raise FileExistsError("Output file exists. Cannot override existing files.")

def parseToAmc(frames:Tuple[dict,...]) -> str:
    amc = ":FULLY-SPECIFIED\n:DEGREES\n"
    frameCount = 1
    for frame in frames:
        amc += f"{frameCount}\n"
        for key, value in frame.items():
            amc += f"{key}"
            for float in value:
                amc += f"\t{str(float)}"
            amc += "\n"
        frameCount += 1
    return amc

def SaveAmc(filename:str, file:str):
    with open(f"{filename}.amc","w") as f:
        f.write(file)


