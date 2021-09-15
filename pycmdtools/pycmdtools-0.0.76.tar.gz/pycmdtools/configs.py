"""
All configurations for pycmdtools
"""
import hashlib

from pytconf import Config, ParamCreator


class ConfigFolder(Config):
    """
    Parameters for the symlink install tool
    """
    folder = ParamCreator.create_existing_folder(
        help_string="Which folder to work on?",
    )


class ConfigUseStandardExceptions(Config):
    """
    Should we use standard exceptions
    """
    use_standard_exceptions = ParamCreator.create_bool(
        help_string="should we use standard exceptions?",
        default=True,
    )


class ConfigChangeLine(Config):
    """
    Change a line in fire parameters
    """
    from_line = ParamCreator.create_str_or_none(
        help_string="from what value?",
        default=None,
    )
    to_line = ParamCreator.create_str(
        help_string="to what value?",
    )


class ConfigProgress(Config):
    """
    Configuration options for progress reporting
    """
    progress = ParamCreator.create_bool(
        help_string="show progress report",
        default=True,
    )


class ConfigAlgorithm(Config):
    """
    Configuration options to select the digest algorithm
    """
    algorithm = ParamCreator.create_choice(
        choice_list=list(hashlib.algorithms_available),
        help_string="digest algorithm to use",
        default="md5",
    )


class ConfigDownloadGoogleDrive(Config):
    """
    Parameters for downloading a file from google drive
    """
    file_id = ParamCreator.create_str(
        help_string='id of the google drive document',
    )
    destination = ParamCreator.create_new_file(
        help_string='file name to save',
    )


class ConfigDownloadGdriveURL(Config):
    """
    Parameters to download a share url from google drive
    """
    # we should really have support in pytconf for create_url...:(
    url = ParamCreator.create_str(
        help_string='url of the google drive document',
    )


class ConfigCopy(Config):
    """
    Configure copy stuff
    """
    copy = ParamCreator.create_bool(
        help_string="Do you want to copy a certain version to others?",
        default=False,
    )
