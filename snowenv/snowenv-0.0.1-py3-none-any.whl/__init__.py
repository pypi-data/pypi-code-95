import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from snowflake.connector import SnowflakeConnection

from .connector import connect


def connect_env(path: Optional[str] = None) -> SnowflakeConnection:
    """Connect to Snowflake using environment variables SNOWFLAKE_*.

    Args:
        path (str): Path to .env file to load. Defaults to None.

    Returns:
        SnowflakeConnection: Opened Snowflake connection.
    """

    if path:
        load_dotenv(path, override=True)

    return connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        private_key_path=os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH"),
        private_key_passphrase=os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )


def connect_dbt(
    profile: Optional[str] = None,
    target: Optional[str] = None,
    path: Optional[str] = str(Path.home() / ".dbt" / "profiles.yml"),
) -> SnowflakeConnection:
    """Connect to Snowflake using dbt profiles.

    Args:
        profile (str, optional): Profile name, optional if there's only one. Defaults to None.
        target (str, optional): Target name, optional if target field specified. Defaults to None.
        path (str, optional): Path to profiles.yml file. Defaults to ~/.dbt/profiles.yml.

    Returns:
        SnowflakeConnection: Opened Snowflake connection.
    """

    raise ValueError(f"Not implemented: {profile}, {target}, {path}")
