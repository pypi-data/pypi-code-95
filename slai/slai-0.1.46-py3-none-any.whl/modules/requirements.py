import sys
import ast

from collections import namedtuple

Import = namedtuple("Import", ["module", "name", "alias"])
BUILT_INS = [
    "os",
    "sys",
    "collections",
    "inspect",
]  # TODO: figure out the built-ins dynamically

USE_LATEST = ["torch"]

PACKAGE_MAP = {"sklearn": "scikit-learn"}


def get_imports(path):
    with open(path) as fh:
        root = ast.parse(fh.read(), path)

    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.Import):
            module = []
        elif isinstance(node, ast.ImportFrom):
            module = node.module.split(".")
        else:
            continue

        for n in node.names:
            yield Import(module, n.name.split("."), n.asname)


def retrieve_version(*, base_module_name, _import, is_derived=False):
    import_line = None

    try:
        version = f"=={sys.modules[base_module_name].__version__}"
    except AttributeError:
        return None, None

    if base_module_name in USE_LATEST:
        version = ""

    if is_derived:
        base_name = base_module_name
        if len(_import.module) > 1:
            base_name = ".".join(_import.module)

        import_line = f"from {base_name} import {'.'.join(_import.name)}"
    else:
        import_line = f"import {'.'.join(_import.name)}"

    if _import.alias:
        import_line += f" as {_import.alias}"

    return version, import_line


def generate_requirements_from_runtime(*, module_name):
    requirements = {}
    import_lines = []

    imports = get_imports(sys.modules[module_name].__file__)

    for _import in imports:
        derived = False

        if len(_import.module) > 0:
            _base_module_name = _import.module[0]
            derived = True
        else:
            _base_module_name = _import.name[0]

        if _base_module_name in BUILT_INS:
            continue

        version, import_line = retrieve_version(
            base_module_name=_base_module_name, _import=_import, is_derived=derived
        )

        if requirements is not None and import_line is not None:
            dist_name = PACKAGE_MAP.get(_base_module_name)

            if dist_name is not None:
                _base_module_name = dist_name

            requirements[_base_module_name] = version
            import_lines.append(import_line)

    import_lines = set(import_lines)
    return requirements, import_lines
