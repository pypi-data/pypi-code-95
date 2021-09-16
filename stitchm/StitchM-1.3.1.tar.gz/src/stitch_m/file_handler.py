import os
from os import path
from pathlib import Path
import re
import logging


marker_regex = re.compile(r'(.*)marker(.*).txt$', flags=re.I)

local_config_file = Path(__file__).resolve().with_name("config.cfg")
dragndrop_bat_file = Path(__file__).resolve().parent / "scripts" / "dragndrop.bat"


def is_marker_file(arg):
    return marker_regex.match(path.basename(arg))


def is_mosaic_file(arg):
    return os.path.splitext(arg)[1].lower() == ".txt" and get_mrc_file(arg)


def argument_organiser(arguments):
    logging.debug("Testing args: %s", arguments)
    args_out = [None, ]
    for arg in arguments:
        if is_marker_file(arg):
            args_out.append(arg)
        elif is_mosaic_file(arg):
            args_out[0] = arg
        else:
            logging.warning("argument %s is invalid", arg)
    logging.debug("Returning args: %s", args_out)
    return args_out


def get_mrc_file(arg, return_data=False):
    logging.debug("Opening file: %s", arg)
    txt_path = Path(arg)
    if txt_path.is_file():
        with txt_path.open('rb') as csvfile:
            mrc_path = csvfile.readline().rstrip().decode('utf-8')
            if return_data:
                from numpy import genfromtxt
                location_array = genfromtxt(csvfile, delimiter=",")
        
        if path.splitext(mrc_path)[1].lower() == ".mrc":
            if not path.exists(mrc_path):
                msg = (
                    "Cannot find %s, so the current directory will be tried",
                    mrc_path)
                if return_data:
                    logging.warning(*msg)
                else:
                    logging.debug(*msg)
                if "\\" in mrc_path:
                    #  Windows file paths
                    mrc_name  = mrc_path.split("\\")[-1]
                elif "/" in mrc_path:
                    # Unix file paths
                    mrc_name = mrc_path.split("/")[-1]
                else:
                    mrc_name =  path.basename(mrc_path)
                mrc_path = txt_path.parent / mrc_name
                if not mrc_path.exists():
                    if return_data:
                        raise IOError(f"Cannot find path {mrc_path}")
                    logging.error("%s cannot be found", mrc_path)
                    return False
            
            if return_data:
                return path.abspath(mrc_path), location_array
            return True
        
        elif return_data:
            raise IOError(f"Expected an mrc file, instead the txt file linked to {mrc_path}")
        logging.error("Mosaic txt file contains invalid mrc path: %s", mrc_path)
    
    elif return_data:
        raise IOError(f"Mosaic txt file {txt_path} does not exist")
    logging.error("Invalid txt file: %s", arg)
    return False


def _get_Windows_home_path():
    home = os.getenv("USERPROFILE")
    if home is None:
        homedrive = os.getenv("HOMEDRIVE")
        homepath = os.getenv("HOMEPATH")
        if homedrive and homepath:
            home = os.path.join(homedrive, homepath)
        else:
            home = os.getenv("HOME")

    if home is not None and "Users" in home:
        try:
            home_path = Path(home).resolve(strict=True)
            return home_path
        except FileNotFoundError:
            pass
    logging.error("Cannot find valid home path. The following path was found: '%s'", home)
    raise FileNotFoundError(f"Cannot find valid home path. The following path was found: '{home}''")


def get_user_log_path():
    try:
        if os.name == "nt":
            user_log_path = _get_Windows_home_path() / "AppData" / "Local" / "Temp" / "stitchm"
            # Windows options are read-only or read and write (default), so no mode set
            user_log_path.mkdir(exist_ok=True)
        elif os.name == "posix":
            from tempfile import mkdtemp
            from getpass import getuser
            # Makes user only access dir:
            user_log_path = Path(mkdtemp(prefix=f"stitchm_log_{getuser()}", dir="/tmp"))
            # User can read/write, group can read, others can't access:
            user_log_path.chmod(mode=0o640)
        else:
            logging.error("Operating system cannot be determined")
        
        logging.info("Creating log files in path %s.", str(user_log_path))
        return user_log_path
    except Exception:
        logging.error(f"Error occurred creating log files", exc_info=True)
        return None
    

def get_user_config_path():
    logging_messages = []
    if os.name == "nt":
        user_config_path = _get_Windows_home_path() / "AppData" / "Local" / "stitchm" / "config.cfg"
    elif os.name == "posix":
        user_config_path = Path.home() / ".config" / "stitchm" / "config.cfg"
    else:
        logging_messages.append("Operating system cannot be determined")
        return None, logging_messages
    return user_config_path, logging_messages


def get_config():
    from configparser import ConfigParser
    config_messages = []
    config = ConfigParser()
    user_config_file, logging_messages = get_user_config_path()
    config_messages.extend(logging_messages)
    if user_config_file is not None and user_config_file.exists():
        try:
            with open(user_config_file) as f:
                config.read_file(f)
            return config, config_messages
        except Exception:
            config_messages.append(f"Opening user config file failed. Please delete your existing file and try again! (Expected path: {user_config_file})")
    with open(local_config_file) as f:
            config.read_file(f)
    return config, config_messages


def create_user_config():
    from shutil import copyfile
    user_config_file, logging_messages = get_user_config_path()
    for message in logging_messages:
        logging.warning(message)
    if user_config_file is not None:
        try:
            Path.mkdir(user_config_file.parent, parents=False, exist_ok=True)
            logging.info("Creating user config file in path %s.", str(user_config_file))
            copyfile(local_config_file, user_config_file)
            logging.info("User config file has been created in %s. This file will override default settings.", str(user_config_file))
        except Exception:
            logging.error("Unable to create user config file due to directory issues", exc_info=True)
    else:
        logging.error("Unable to create user config file")


def boolean_config_handler(config, section, key, default):
    try:
        return config.getboolean(section, key, fallback=default)
    except ValueError:
        logging.error("Invalid '%s' option found, default of '%s' will be used", key, default)
        return default


def _create_lnk_file(shortcut_path):
    try:
        # win23com is from the package pywin32, only available in Windows
        import win32com.client
    except ImportError:
        msg = "win32com of pywin32 cannot be imported! Please run 'pip install pywin32' (with '--user' argument if on a shared python environment) then try again."
        print(msg)
        logging.error(msg)
        raise
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = str(dragndrop_bat_file)
    shortcut.save()
    msg = f"Shortcut created! It can be found here: {shortcut_path}"
    print(msg)
    logging.info(msg)


def create_Windows_shortcut():
    if os.name != "nt":
        logging.error("This command is only valid on Windows installations.")
        return 
    else:
        # Place link on users desktop
        shortcut_path = _get_Windows_home_path() / "Desktop" / "StitchM.lnk"
        msg = f"Creating shortcut on user desktop: {shortcut_path}"
        logging.info(msg)
        if shortcut_path.exists():
            msg = f"StitchM shortcut found:'{shortcut_path}'. Are you sure you want to replace it? (y/N)"
            user_input = str(input(msg))
            logging.debug(msg)
            logging.debug("User input: %s", user_input)
            if user_input.lower() == "y" or user_input.lower() == "yes":
                logging.info("The existing shortcut will be replaced.")
            elif user_input.lower() == "n" or user_input.lower() == "no":
                logging.info("The existing shortcut will not be modified.")
            else:
                logging.info("Invalid input: %s. The existing shortcut will not be modified.", user_input)
                return
        _create_lnk_file(shortcut_path)
