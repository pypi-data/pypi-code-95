"""Common settings for notices app"""


def plugin_settings(settings):
    """Settings for the notices app"""
    # .. toggle_name: ENABLE_NOTICES
    # .. toggle_implementation: DjangoSetting
    # .. toggle_default: False
    # .. toggle_description: If True, users will be prompted to acknowledge the notice in a client
    # .. toggle_use_cases: open_edx
    # .. toggle_creation_date: 2021-08-19
    settings.FEATURES["ENABLE_NOTICES"] = False
    settings.FEATURES["NOTICES_REDIRECT_ALLOWLIST"] = []
    settings.FEATURES["NOTICES_DEFAULT_REDIRECT_URL"] = "http://www.example.com"
