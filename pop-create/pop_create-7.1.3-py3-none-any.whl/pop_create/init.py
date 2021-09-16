import datetime
import pathlib
import subprocess
import tempfile
from typing import List

from cookiecutter.exceptions import FailedHookException
from cookiecutter.generate import generate_files
from dict_tools.data import NamespaceDict


def __init__(hub):
    hub.pop.sub.add(dyne_name="tool")
    hub.pop.sub.load_subdirs(hub.tool, recurse=True)
    hub.pop.sub.load_subdirs(hub.pop_create)


COMPLETION_TEXT = """
Congratulations! You have set up a new project!
This project can be executed by calling the run.py script:
    python3 run.py
This project has been set up with pre-commit hooks for code checks and black.
First set up your source control environment with "git init" or "hg init".
Then enable these checks in your git checkout:
    pip install pre-commit
    pre-commit install
To run pre-commit manually, execute:
    pre-commit run --all-files
Please fork the pop-awesome and open a PR listing your new project \u263A
    https://gitlab.com/saltstack/pop/pop-awesome
"""


def cli(hub):
    hub.pop.config.load(["pop_create"], cli="pop_create")
    if hub.SUBPARSER:
        subparsers = [str(hub.SUBPARSER).replace("-", "_")]
    else:
        # No subparser specified, do all the core creators
        # cicd is last because it will run pre-commit on everything
        subparsers = ["seed", "docs", "tests", "cicd"]

    # Decide which copy function to use in the end
    if hub.OPT.pop_create.overwrite_existing:
        copy_function = hub.tool.path.copy2
    else:
        copy_function = hub.tool.path.copy

    with tempfile.TemporaryDirectory(prefix="pop-create-") as tempdir:
        ctx = hub.pop_create.init.context()
        hub.pop_create.init.run(
            directory=tempdir,
            subparsers=subparsers,
            root_dir=tempdir,
            **ctx,
        )

        hub.tool.path.IGNORE = [
            str(pathlib.Path(ctx.target_directory) / x)
            for x in hub.OPT.pop_create.ignore
        ]

        # Copy from temporary directory to target directory
        hub.tool.path.copytree(
            src=pathlib.Path(tempdir),
            dst=pathlib.Path(str(ctx.target_directory)),
            copy_function=copy_function,
        )

    # All done!
    print(COMPLETION_TEXT)


def context(hub):
    directory = pathlib.Path(hub.OPT.pop_create.directory)
    project_name = hub.OPT.pop_create.project_name or directory.name
    clean_name = project_name.replace("-", "_").replace(" ", "_")
    short_dyne_list = sorted(hub.OPT.pop_create.get("dyne", ()))
    if hub.OPT.pop_create.vertical:
        dyne_list = short_dyne_list
    else:
        dyne_list = [clean_name] + short_dyne_list

    if hub.OPT.pop_create.author:
        author = hub.OPT.pop_create.author
    else:
        author = subprocess.getoutput("git config --global user.name")

    if hub.OPT.pop_create.author_email:
        author_email = hub.OPT.pop_create.author_email
    else:
        author_email = subprocess.getoutput("git config --global user.email")

    ctx = NamespaceDict(
        author=author,
        author_email=author_email,
        clean_name=clean_name,
        dyne_list=dyne_list,
        project_name=project_name,
        short_dyne_list=short_dyne_list,
        this_year=str(datetime.datetime.today().year),
        target_directory=str(directory),
    )

    for key, value in hub.OPT.pop_create.items():
        # Don't overwrite any values we already sanitized
        if key in ("project_name", "directory", "author", "author_email"):
            continue
        ctx[key] = value
    return ctx


def run(
    hub,
    directory: pathlib.Path,
    subparsers: List[str],
    **ctx,
):
    for subparser in subparsers:
        try:
            # Let each subparser create it's own context
            context = NamespaceDict(ctx.copy())
            if "init" in hub.pop_create[subparser]:
                context = hub.pop_create[subparser].init.context(context, directory)

            # Get the input directory
            repo_dir = hub.pop_create[subparser]._dirs[0]

            # Copy the templates from the source to the a temporary directory using the generated context
            try:
                generate_files(
                    repo_dir=repo_dir,
                    context={"cookiecutter": context},
                    output_dir=directory,
                    # We should be dealing with a temporary directory
                    overwrite_if_exists=True,
                    skip_if_file_exists=False,
                )
            except FailedHookException:
                hub.log.error(f"Failed to run hook for subparser: {subparser}")
                raise
        except IndexError:
            hub.log.error(f"No template under sub {subparser}")
