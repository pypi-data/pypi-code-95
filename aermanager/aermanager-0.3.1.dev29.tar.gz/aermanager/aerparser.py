from typing import Callable
from .parsers import parse_aedat4, parse_dvs_128, parse_dvs_ibm, parse_dvs_red, parse_dvs_346mini


def load_events_from_file(filename, parser: Callable = parse_aedat4):
    """
    Load_events_from_file(filename, dvs_model) - Method, convert .aedat file into Numpy Sturctured array of Class DvsData

    Args:
        filename (str):
            The name of the .aedat, .aedat4, .bin file

        parser (str, Callable):
            Callable: You can also pass a custom callable/method,
            to be used for parsing your custom file.
            This method is expected to return a shape, and a structured-array
            identical to the return type of this method.

            Defaults to parse_aedat4

            Alternatively, you can specity a dvs sensor name from the
            below list to use one of the inbuilt parsers.

            Name of the DVS model. Currently only 3 supported:
            'DVS128': resolution of rows and cols are (128, 128)
            'mini346': resolution of rows and cols are (260, 346)
            'redV3': resolution of rows and cols are (132,104)
    Returns:
        tuple: a tuple containing (shape, xytp)
            shape (Tuple):
                (height, width) or None if it cannot be inferred
            xytp:
                Structured Numpy array of Class DvsData where aer_data.data is:
                ["x"]: int Row ID of a spike
                ["y"]: int Column ID of a spike
                ["p"]: bool 'On' (polarity=0) or 'Off' (polarity=1)
                Channel of a spike
                ["t"]: float Timestamp of a spike in ms
    """
    if callable(parser):
        pass
    elif parser == "aedat4":
        parser = parse_aedat4
    elif parser == "DVS128":
        parser = parse_dvs_128
    elif parser == "mini346":
        parser = parse_dvs_346mini
    elif parser == "redV3":
        parser = parse_dvs_red
    elif parser == "ibm":
        parser = parse_dvs_ibm
    else:
        raise NotImplementedError("DVS model not recognized.")
    shape, aer_data = parser(filename)
    return shape, aer_data

