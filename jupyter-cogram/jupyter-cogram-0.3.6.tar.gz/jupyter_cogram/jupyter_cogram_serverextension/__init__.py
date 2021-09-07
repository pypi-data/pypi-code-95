import json
import logging
import os
from pathlib import Path
from typing import List, Text, Optional

import requests
import semantic_version
from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join

from jupyter_cogram import __version__

debug_mode = os.environ.get("DEBUG_MODE", "false") == "true"

if debug_mode:
    logging.basicConfig(level=logging.DEBUG)

logger: logging.Logger = logging.getLogger(__name__)

backend_url = os.environ.get("BACKEND_URL", "https://api.cogram.ai")
completions_enpdoint = os.environ.get("SUGGESTIONS_ENDPOINT", "completions")
package_pypi_url = "https://pypi.org/pypi/jupyter-cogram/json"

check_token_endpoint = "checkToken"

logger.debug(f"Backend URL: {backend_url}")
logger.debug(f"Suggestions endpoint: {completions_enpdoint}")
logger.debug(f"PyPI URL: {package_pypi_url}")

config_location = Path().home() / ".ipython/nbextensions/jupyter-cogram"
token_file_name = "cogram_auth_token"

LATEST_PYPI_VERSION: Optional[Text] = None


def save_token(token: Text, loc: Path = config_location) -> None:
    loc = loc.absolute()

    if not loc.is_dir():
        loc.mkdir(parents=True)

    (loc / token_file_name).write_text(token)


def fetch_token(loc: Path = config_location) -> Optional[Text]:
    loc = loc.absolute()
    fname = loc / token_file_name
    logger.debug(f"Checking for token at {fname}")
    if not fname.is_file():
        return None

    return fname.read_text().strip()


def post_auth_token(token: Text) -> requests.Response:
    url = f"{backend_url}/{check_token_endpoint}"
    logger.debug(f"Posting auth token to {url}. Token: {token}")
    return requests.post(
        url,
        json={"auth_token": token},
    )


def is_installation_up_to_date(
    pypi_url: Text = package_pypi_url,
) -> bool:
    logger.info("Checking if local installation is up to date.")

    try:
        res = requests.get(pypi_url, timeout=0.5)
    except Exception as e:
        logger.exception(e)
        return True

    if res.status_code != 200:
        # we don't know, so let's return `True`
        return True

    global LATEST_PYPI_VERSION
    LATEST_PYPI_VERSION = res.json().get("info", {}).get("version")
    if not LATEST_PYPI_VERSION:
        # no version returned
        logger.debug("Could not find latest pypi version.")
        return True

    try:
        is_up_to_date = semantic_version.Version(
            __version__
        ) >= semantic_version.Version(LATEST_PYPI_VERSION)
        logger.info(
            f"Have package version {__version__}. "
            f"Latest PyPi version is {LATEST_PYPI_VERSION}. Installed version is up to "
            f"date: {is_up_to_date}."
        )
        return is_up_to_date
    except ValueError as e:
        logger.exception(e)
        return False


def fetch_suggestion_codex(
    queries,
    cell_contents: Optional[List[Text]] = None,
    kernel_id: Optional[Text] = None,
    session_id: Optional[Text] = None,
    auth_token: Optional[Text] = None,
):
    url = f"{backend_url}/{completions_enpdoint}"
    res = requests.post(
        url,
        json={
            "queries": queries,
            "cell_contents": cell_contents or [],
            "kernel_id": kernel_id,
            "session_id": session_id,
            "auth_token": auth_token,
        },
    )

    save_token(auth_token)

    if res.status_code >= 400:
        if res.json() and res.json().get("error") is not None:
            msg = res.json()["error"]
        else:
            msg = res.text

        error_dict = {
            "status": "error",
            "error_msg": msg,
            "status_code": res.status_code,
        }

        raise ValueError(json.dumps(error_dict))

    return res.json()


class JupyterCogramHandler(IPythonHandler):
    def __init__(self, application, request, **kwargs):
        super(JupyterCogramHandler, self).__init__(application, request, **kwargs)

    def post(self):
        data = json.loads(self.request.body)
        queries = data.get("queries", "")
        cell_contents = data.get("cell_contents", [])
        kernel_id = data.get("kernel_id", "")
        session_id = data.get("session_id", "")
        auth_token = data.get("auth_token", "'")

        try:
            suggestions = fetch_suggestion_codex(
                queries, cell_contents, kernel_id, session_id, auth_token
            )

            logger.debug(f"Have suggestions\n{json.dumps(suggestions, indent=2)}")
            if "choices" in suggestions and suggestions["choices"]:
                message = [c["text"] for c in suggestions["choices"]]
            else:
                message = None

            # logger.debug(f"Extracted suggestion:\n{suggestion}")
            status = "success"
            status_code = 200

        except Exception as e:
            error_dict = json.loads(str(e))
            status = error_dict["status"]
            message = error_dict["error_msg"]
            status_code = error_dict["status_code"]

        response = {"status": status, "message": message}
        self.set_status(status_code)
        # logger.debug(f"Returning response dict {json.dumps(response, indent=2)}")
        self.finish(json.dumps(response))


class JupyterCogramTokenHandler(IPythonHandler):
    def __init__(self, application, request, **kwargs):
        super(JupyterCogramTokenHandler, self).__init__(application, request, **kwargs)

    def post(self):
        logger.debug(f"Receiving token Post!")
        data = json.loads(self.request.body)
        token = data.get("auth_token", "")

        post_token_response = post_auth_token(token)

        if post_token_response.status_code == 200:
            save_token(token)
            status = 200
            response = {"status": status, "message": "Token saved."}
        else:
            status = post_token_response.status_code
            response = post_token_response.json()

        self.set_status(status)
        logger.debug(f"Returning response dict {json.dumps(response, indent=2)}")
        self.finish(json.dumps(response))

    def get(self):
        logger.debug(f"Receiving token fetch request")
        token = fetch_token()
        logger.debug(f"Have fetched token {token}")
        if token is not None:
            logger.debug(f"Checking if token is valid against API: {token}")
            token_valid = post_auth_token(token)
        else:
            token_valid = False

        if token_valid:
            status = 200
            response = {
                "status": status,
                "message": "Token found.",
                "auth_token": token,
            }
        else:
            status = 404
            response = {
                "status": status,
                "message": "Token not found.",
                "auth_token": None,
            }

        self.set_status(status)
        logger.debug(f"Returning response dict {json.dumps(response, indent=2)}")
        self.finish(json.dumps(response))


class JupyterCogramVersionHandler(IPythonHandler):
    def __init__(self, application, request, **kwargs):
        super(JupyterCogramVersionHandler, self).__init__(
            application, request, **kwargs
        )

    def get(self):
        logger.debug(f"Checking package version")
        is_up_to_date = is_installation_up_to_date()

        if is_up_to_date:
            status = 200
            message = (
                f"Installed version ({__version__}) is up to date with PyPI"
                f" version ({LATEST_PYPI_VERSION})."
            )
        else:
            status = 400
            message = (
                f"Installed version ({__version__}) is **not** up to date with PyPI "
                f"version ({LATEST_PYPI_VERSION})."
            )

        self.set_status(status)
        response = {
            "status": status,
            "message": message,
            "pypi_version": LATEST_PYPI_VERSION,
            "installed_version": __version__,
        }
        logger.debug(f"Returning response dict {json.dumps(response, indent=2)}")
        self.finish(json.dumps(response))


def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication):
        handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    host_pattern = ".*$"
    web_app.add_handlers(
        host_pattern,
        [
            (url_path_join(web_app.settings["base_url"], uri), handler)
            for uri, handler in [
                ("/cogram", JupyterCogramHandler),
                ("/token", JupyterCogramTokenHandler),
                ("/checkVersion", JupyterCogramVersionHandler),
            ]
        ],
    )
    logger.debug("loaded_jupyter_server_extension: jupyter-cogram")
