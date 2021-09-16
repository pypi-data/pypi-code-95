import pathlib

import pop.hub
from dict_tools.data import NamespaceDict

if __name__ == "__main__":
    root_directory = pathlib.Path.cwd()
    hub = pop.hub.Hub()
    hub.pop.sub.add(dyne_name="tool")
    hub.pop.sub.load_subdirs(hub.tool, recurse=True)
    ctx = NamespaceDict({{cookiecutter}})

    hub.tool.path.rmtree(
        root_directory
        / ctx.clean_name
        / "exec"
        / ctx.service_name
        / ctx.clean_api_version
        / "recursive_contracts"
    )
    try:
        (
            root_directory / ctx.clean_name / "exec" / ctx.service_name / "sample.py"
        ).unlink()
    except FileNotFoundError:
        ...
