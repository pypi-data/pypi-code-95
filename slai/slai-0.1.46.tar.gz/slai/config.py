from slai.modules.parameters import from_config


def get_api_base_url():
    stage = from_config(
        key="STAGE",
        default="staging",
    )

    if stage == "local":
        base_url = from_config(
            key="BASE_URL",
            default="http://localhost:5000",
        )
    elif stage == "docker":
        base_url = "http://host.docker.internal:5000"
    else:
        base_url = from_config(
            key="BASE_URL",
            default=f"https://api.slai.io/{stage}",
        )

    return base_url
