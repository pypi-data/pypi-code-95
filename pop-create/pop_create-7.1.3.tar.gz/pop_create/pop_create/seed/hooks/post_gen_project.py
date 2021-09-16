import pathlib
import shutil

from dict_tools.data import NamespaceDict

if __name__ == "__main__":
    ctx = NamespaceDict({{cookiecutter}})
    root_directory = pathlib.Path.cwd()

    if ctx.vertical:
        script = root_directory / ctx.clean_name / "scripts.py"
        script.unlink()

        run = root_directory / "run.py"
        run.unlink()

        non_vertical_dyne = root_directory / ctx.clean_name / ctx.clean_name
        shutil.rmtree(non_vertical_dyne)
