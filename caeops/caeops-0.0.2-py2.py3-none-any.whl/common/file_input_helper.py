import sys
from caeops.utilities import read_json, read_yaml_as_json, convert_dict_to_yaml
import json
from caeops.common.parser import ArgumentParser


def check_for_generate_cli_skeleton_argument(parser) -> bool:
    """
    Generates the CLI skeleton structure for the given service command
    :param parser: Arguments parser
    """
    # Take system argument from index 3
    args = parser.parse_args(sys.argv[3:])
    if args.generate_cli_skeleton:
        # Parse the arguments in the current parser and convert them to payload in camel case
        payload = ArgumentParser.parse_args_and_convert_to_payload(parser, keep_none=True)
        # Convert the dict to yaml if the required output format is yaml, else dump it into a json
        data = (
            convert_dict_to_yaml(payload)
            if args.yaml
            else json.dumps(payload, indent=2)
        )
        print(data)
        exit()
    return True


def load_input_from_file(parser) -> dict:
    """
    Generates the CLI skeleton structure for the given service command
    :param parser: Arg parser
    """
    args = parser.parse_args(sys.argv[3:])
    data = None
    if args.input_file:
        data = (
            read_yaml_as_json(args.input_file)
            if args.yaml
            else read_json(args.input_file)
        )
        data = json.loads(data)
    return data
