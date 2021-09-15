"""Common for database tools"""
import os


def build_database_url(protocol: str) -> str:
    """Builds a database url from environment variables

    Environment variable used: *DATABASE_USER*, *DATABASE_PASSWORD*, *DATABASE_HOST*, \
        *DATABASE_PORT*, *DATABASE_DATABASE*

    :raises NotImplementedError: Raised if using an unsupported protocol

    :param protocol: The database protocol to use.
        Currently *mysql* and *postgres* are supported
    :type protocol: str
    :return: Database URL
    :rtype: str
    """
    if os.environ.get("DATABASE_URL"):
        return os.environ.get("DATABASE_URL")
    defaults = {
        "postgres": {
            "DATABASE_USER": "postgres",
            "DATABASE_PASSWORD": "",
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": 5432,
            "DATABASE_DATABASE": "postgres",
        },
        "mysql": {
            "DATABASE_USER": "root",
            "DATABASE_PASSWORD": "",
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": 3306,
            "DATABASE_DATABASE": "",
        },
    }
    if protocol not in defaults:
        raise NotImplementedError(f"Protocol {protocol} is not supported")
    required_options = [
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_DATABASE",
    ]

    results_dict = {}
    for option in required_options:
        results_dict[option] = os.environ.get(option, defaults[protocol][option])

    return (
        f"{protocol}://{results_dict['DATABASE_USER']}:"
        f"{results_dict['DATABASE_PASSWORD']}@{results_dict['DATABASE_HOST']}:"
        f"{results_dict['DATABASE_PORT']}/{results_dict['DATABASE_DATABASE']}"
    )
