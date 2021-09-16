import pathlib

from dict_tools.data import NamespaceDict

if __name__ == "__main__":
    ctx = NamespaceDict({{cookiecutter}})
    root_directory = pathlib.Path.cwd()

    for dyne in ctx.dyne_list:
        contract = root_directory / ctx.clean_name / dyne / "contracts"
        try:
            contract.mkdir(parents=True)
        except FileExistsError:
            ...
