"""Production settings for notices app"""


def plugin_settings(settings):
    """Settings for the notices app"""
    # Whether to enable the feature or not
    settings.FEATURES["ENABLE_NOTICES"] = settings.ENV_TOKENS.get("ENABLE_NOTICES", settings.FEATURES["ENABLE_NOTICES"])
    settings.FEATURES["NOTICES_REDIRECT_ALLOWLIST"] = settings.ENV_TOKENS.get(
        "NOTICES_REDIRECT_ALLOWLIST", settings.FEATURES["NOTICES_REDIRECT_ALLOWLIST"]
    )
    settings.FEATURES["NOTICES_DEFAULT_REDIRECT_URL"] = settings.ENV_TOKENS.get(
        "NOTICES_DEFAULT_REDIRECT_URL", settings.FEATURES["NOTICES_DEFAULT_REDIRECT_URL"]
    )
