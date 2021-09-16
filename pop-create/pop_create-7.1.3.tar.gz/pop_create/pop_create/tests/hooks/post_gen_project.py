import pathlib
import shutil

from dict_tools.data import NamespaceDict


def make_module(path: pathlib.Path):
    """
    Recursively add an empty __init__.py file to this dir and subdirs recursively.
    Otherwise pytest will have issues with duplicate names of directories and files.
    """
    if path.is_dir():
        init = path / "__init__.py"
        init.touch()
        for p in path.iterdir():
            make_module(p)


if __name__ == "__main__":
    ctx = NamespaceDict({{cookiecutter}})

    root_directory = pathlib.Path.cwd()
    test_dir = root_directory / "tests"

    if ctx.vertical:
        # Vertically app-merged projects won't have an entrypoint for this test
        for test_type in ("integration", "unit"):
            shutil.rmtree(test_dir / test_type / ctx.clean_name)

    # Add __init__.py files under every directory in the "tests" dir
    make_module(test_dir)
