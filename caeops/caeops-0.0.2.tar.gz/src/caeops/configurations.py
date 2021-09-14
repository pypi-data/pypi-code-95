import configparser
import os
from pathlib import Path
import shutil

default_profile = "default"
config_folder = os.path.join(os.path.expanduser("~"), ".cloudaeye")
configFileName = os.path.join(config_folder, "config.ini")


def check_if_config_file_exists() -> bool:
    """
    Checks if config file exists
    :return: True/False
    """
    return os.path.exists(configFileName)


def read(config_name: str, profile=default_profile) -> str:
    """
    Read the value for the config_name from the config file
    :param config_name: Name of the config
    :return: Value of the config name
    :param profile: The user profile to be used (if none provided uses the default profile)
    """
    # Initialize a config parser
    config_parser = configparser.ConfigParser()
    # Check if file exists
    if os.path.isfile(configFileName):
        # Read the config file
        config_parser.read(configFileName)
        # Check if config name exists and return
        try:
            value = config_parser.get(profile, config_name)
            # Return the value for the given config name
            return value
        except Exception:
            # Return config_name not found
            return config_name + " not found"

    else:
        print("File not found. Please use caeops configure")
        exit(1)


def write(config_name, value, profile=default_profile):
    """
    Saves the given config name and value to the required profile
    :param config_name: Name of the new config
    :param value: Value of the new config
    :param profile: The user profile to be used (if none provided uses the default profile)
    :return: None
    """
    # Initialize a config parser
    config_parser = configparser.ConfigParser()
    # Get the path of the config file
    config_file_path = Path(configFileName)
    # Check if it is a file
    if config_file_path.is_file():
        # TODO learn what this command does and add the comment here
        config_parser.readfp(open(configFileName))
    # Check if the config file has the required profile
    if not config_parser.has_section(profile):
        config_parser.add_section(profile)
    # Open the config file in write mode
    cfg_file = open(configFileName, "w")
    # Set the config name and config value in the config file
    config_parser.set(profile, config_name, value)
    # Write to file and close
    config_parser.write(cfg_file)
    cfg_file.close()
    return


def delete():
    """
    Deletes the configuration folder
    :return: None
    """
    if os.path.exists(config_folder):
        shutil.rmtree(config_folder)
    return
