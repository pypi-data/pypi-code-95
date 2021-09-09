# -- coding: utf-8 --
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pathlib import Path

import requests
import typer
import yaml

app = typer.Typer()

query_app = typer.Typer()
app.add_typer(query_app, name="query", help="Execute queries, list databases, tables")
storage_app = typer.Typer()
app.add_typer(storage_app, name="storage", help="Manipulate data files")
connector_app = typer.Typer()
app.add_typer(
    connector_app, name="connector", help="Manipulate DB/storage connector instances"
)


APP_NAME = "compose"

"""
Wrapper around https://docs.gethue.com/developer/api/rest/
"""


@app.callback()
def callback():
    """
    Query your Data Easily
    """


@app.command()
def auth(
    api_url: str = typer.Option("https://demo.gethue.com", prompt=True),
    username: str = typer.Option("demo", prompt=True),
    password: str = typer.Option("demo", prompt=True, hide_input=True),
):
    """
    Authenticate with the API server
    """
    session = requests.Session()

    data = {
        "username": username,
        "password": password,
    }

    response = session.post("%s/api/token/auth" % api_url, data=data)
    print(
        "Auth: %s %s"
        % ("success" if response.status_code == 200 else "error", response.status_code)
    )

    token = json.loads(response.content)["access"]
    print("Token: %s" % token)

    save_api_creds(api_url, username, token)


@query_app.command("autocomplete")
def query_autocomplete(database: str = None, table: str = None):
    """
    Autocomplete SQL
    """
    creds = get_config()["auth"]

    response = requests.post(
        "%(url)s/api/query/autocomplete" % creds,
        headers={
            "Authorization": "Bearer %(token)s" % creds,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"snippet": json.dumps({"type": "6"})},
    )
    print(response.status_code)
    print(json.dumps(json.loads(response.text), indent=2, sort_keys=True))


@storage_app.command("list")
def storage_list(path: str = typer.Argument("s3a://demo-gethue")):
    """
    List the content of a directory
    """

    creds = get_config()["auth"]

    response = requests.get(
        "%(url)s/api/storage/view=%(path)s" % {"url": creds["url"], "path": path},
        headers={
            "Authorization": "Bearer %(token)s" % creds,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    data = json.loads(response.text)

    for f in data["files"][1:]:
        print(
            "%(path)s\t(%(host)s/hue%(url)s)"
            % {"url": f["url"], "host": creds["url"], "path": f["path"]}
        )


@connector_app.command("list")
def connector_list():
    """
    List the installed connectors
    """

    creds = get_config()["auth"]

    response = requests.get(
        "%(url)s/api/connector/instances/" % {"url": creds["url"]},
        headers={
            "Authorization": "Bearer %(token)s" % creds,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    print(response.status_code)
    print(json.dumps(json.loads(response.text), indent=2, sort_keys=True))


def save_api_creds(api_url: str, username: str, token: str):
    app_dir = typer.get_app_dir(APP_NAME)
    config_dir = Path(app_dir)
    config_dir.mkdir(exist_ok=True)
    config_path: Path = config_dir / "config.yml"

    yaml.dump(
        {"auth": {"url": api_url, "username": username, "token": token}},
        open(config_path, "w"),
    )


def get_config():
    app_dir = typer.get_app_dir(APP_NAME)
    config_path: Path = Path(app_dir) / "config.yml"

    if not config_path.is_file():
        typer.echo(
            "Config file doesn't exist yet. Please run again the `auth` command."
        )
        raise typer.Exit()

    config = yaml.safe_load(open(config_path))

    return config


if __name__ == "__main__":
    app()
