import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional

import toolz
from appdirs import user_data_dir


@contextmanager
def db_cursor(db_path):
    """
    Wrap sqlite's cursor for use as a context manager

    Commits all changes if no exception is raised.
    Always closes the cursor/connection after the context manager exits.
    """
    connection = sqlite3.connect(str(db_path))
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_db_path() -> str:
    data_directory = user_data_dir(appname="kolo", appauthor="kolo")

    storage_path = os.path.join(data_directory, "storage")
    Path(storage_path).mkdir(parents=True, exist_ok=True)

    custom_database_name = os.environ.get("KOLO_PROJECT_NAME")

    if custom_database_name is not None:
        database_name = custom_database_name.lower()
    else:
        current_folder_name = os.path.basename(os.getcwd()).lower()
        database_name = current_folder_name

    return os.path.join(storage_path, f"{database_name}.sqlite3")


def create_invocations_table(cursor) -> None:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS invocations (
        id text PRIMARY KEY NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        data text NOT NULL
    );
    """
    create_timestamp_index_query = """
        CREATE INDEX IF NOT EXISTS
        idx_invocations_created_at
        ON invocations (created_at);
        """

    cursor.execute(create_table_query)
    cursor.execute(create_timestamp_index_query)


def create_config_table(cursor) -> None:
    create_config_query = """
    CREATE TABLE IF NOT EXISTS config (
        id INTEGER PRIMARY KEY,
        source text NOT NULL UNIQUE,
        last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        data text NOT NULL
    );
    """
    cursor.execute(create_config_query)


def save_config_to_db(cursor, config) -> None:
    save_config_query = "INSERT OR REPLACE INTO config(source, data) VALUES(?,?);"
    cursor.execute(save_config_query, ("python", json.dumps(config)))


def load_config_from_db(db_path: str) -> Dict[str, Any]:
    """
    Load the kolo config from sqlite

    We return the config defined by VSCode, if available, and fallback
    to the config we saved to the db from `.kolo/conf.toml`.
    """
    load_config_query = "SELECT source, data from config;"
    with db_cursor(db_path) as cursor:
        cursor.execute(load_config_query)
        rows = cursor.fetchall()

    data = {key: json.loads(value) for key, value in rows}
    python_config = data["python"]
    vscode_config = data.get("vscode", {})
    return toolz.merge_with(toolz.merge, python_config, vscode_config)


def setup_db(config: Optional[MutableMapping[str, Any]] = None) -> str:
    if config is None:
        config = {}
    db_path = get_db_path()

    with db_cursor(db_path) as cursor:
        create_invocations_table(cursor)
        create_config_table(cursor)
        save_config_to_db(cursor, config)

    return db_path


def save_invocation_in_sqlite(
    db_path: str, invocation_id: str, json_string: str
) -> None:
    insert_sql = """
        INSERT OR IGNORE INTO invocations(id, data)
        VALUES(?,?)
        """

    # We can't reuse a connection
    # because we're in a new thread
    with db_cursor(db_path) as cursor:
        cursor.execute(insert_sql, (invocation_id, json_string))
