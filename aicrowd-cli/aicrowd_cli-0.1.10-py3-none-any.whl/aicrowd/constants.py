"""
Global constants file
"""

import os

RAILS_HOST = os.getenv("RAILS_HOST", "www.aicrowd.com")
RAILS_API_ENDPOINT = f"https://{RAILS_HOST}/api/v1"
AICROWD_API_ENDPOINT = os.getenv("AICROWD_API_ENDPOINT", "https://api.aicrowd.com")

DATASETS_HOST = os.getenv("DATASETS_HOST", "datasets.aicrowd.com")


class LoginConstants:
    """
    Constants related to the login subcommand
    """

    CONFIG_KEY = "aicrowd_api_key"
    URL_LOGIN_REQUEST_LIFETIME = 120


class ChallengeConstants:
    """
    Constants related to challenge command
    """

    CONFIG_SECTION_NAME = "aicrowd-cli"
    CONFIG_ID_KEY = "challenge-id"
    CONFIG_SLUG_KEY = "challenge-slug"


class JupyterConfigConstants:
    ASSETS_DIR = "ASSETS_DIR"
    AICROWD_CONFIG = "AIcrowdConfig"
