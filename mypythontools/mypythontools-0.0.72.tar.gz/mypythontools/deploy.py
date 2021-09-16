"""
Allow to deploy project.
Possible destinations: PYPI.

Check `deploy_to_pypi` function docs for how to use it.

Usually this function is not called manually, but it's a part of `push_pipeline` from utils.

Check utils docs where is described, how to use VS Code Task to be able to optionally test, push and deploy
with tasks (one button click).
"""
import subprocess
import os
import shutil
from pathlib import Path
from typing import Union
import platform

import mylogging

from . import paths


def deploy_to_pypi(setup_path: Union[str, Path] = "infer") -> None:
    """Publish python library to Pypi. Username and password are set
    with env vars `TWINE_USERNAME` and `TWINE_PASSWORD`.

    Note:
        You need working `setup.py` file. If you want to see example, try the one from project-statrer on

        https://github.com/Malachov/mypythontools/blob/master/content/project-starter/setup.py

    Args:
        setup_path((str, pathlib.Path), optional): Function suppose, that there is a setup.py somewhere in cwd.
            If not, pass path to setup.py. Build and dist folders will be created in same directory. Defaults to "infer".
    """

    usr = os.environ.get("TWINE_USERNAME")
    pas = os.environ.get("TWINE_PASSWORD")

    if not usr or not pas:
        raise KeyError(
            mylogging.return_str("Setup env vars TWINE_USERNAME and TWINE_PASSWORD to use deploy.")
        )

    setup_path = (
        paths.PROJECT_PATHS.ROOT_PATH / "setup.py"
        if setup_path == "infer"
        else paths.validate_path(setup_path)
    )

    setup_dir_path = setup_path.parent

    dist_path = setup_dir_path / "dist"
    build_path = setup_dir_path / "build"

    if dist_path.exists():
        shutil.rmtree(dist_path)

    if build_path.exists():
        shutil.rmtree(build_path)

    if platform.system() == "Windows":
        python_command = "python"
    else:
        python_command = "python3"

    build_command = f"{python_command} setup.py sdist bdist_wheel"

    subprocess.run(
        build_command.split(),
        cwd=setup_dir_path.as_posix(),
        check=True,
    )

    subprocess.run(
        [
            "twine",
            "upload",
            "-u",
            os.environ["TWINE_USERNAME"],
            "-p",
            os.environ["TWINE_PASSWORD"],
            "dist/*",
        ],
        cwd=setup_dir_path.as_posix(),
        check=True,
    )

    shutil.rmtree(dist_path)
    shutil.rmtree(build_path)
