import os
from importlib import import_module
from typing import List


def path_head(path: str) -> str:
    """
    Get the head of a path string.

    >>> path_head('/dir1/dir2/path.ext')
    'path.ext'

    >>> path_head('path.ext')
    'path.ext'

    Args:
        path (str): Path string.

    Returns:
        str: Path string's head.
    """
    return os.path.split(path)[1]


def path_tail(path: str) -> str:
    """
    Get the tail of a path string.

    >>> path_tail('/dir1/dir2/path.ext')
    '/dir1/dir2'

    Args:
        path (str): Path string.

    Returns:
        str: Path string's tail.
    """
    return os.path.split(path)[0]


def path_base(path: str) -> str:
    """
    Get the base of a path string.

    >>> path_base('/dir1/dir2/path.ext')
    ''

    >>> path_base('dir1/dir2/path.ext')
    'dir1'

    Args:
        path (str): Path string.

    Returns:
        str: Path string's base.
    """

    return os.path.normpath(path).split(os.sep)[0]


def path_ext(path: str) -> str:
    """
    Get the extension of a path string.

    >>> path_ext('/dir1/dir2/path.ext')
    '.ext'

    >>> path_ext('/dir1/dir2/path.ext.j2')
    '.j2'

    Args:
        path (str): Path string.

    Returns:
        str: Path string's extension.
    """
    return os.path.splitext(path)[1]


def path_name(path: str) -> str:
    """
    Get the name without an extension of a path string.

    >>> path_name('/dir1/dir2/path.ext')
    'path'

    Args:
        path (str): Path string.

    Returns:
        str: Path string's extension.
    """
    return path_head(os.path.splitext(path)[0])


def drop_extension(path: str) -> str:
    """
    Get the full name without the final extension of a path string.

    >>> drop_extension('/dir1/dir2/path.ext')
    '/dir1/dir2/path'

    >>> drop_extension('/dir1/dir2/path.ext1.ext2')
    '/dir1/dir2/path.ext1'

    Args:
        path (str): Path string.

    Returns:
        str: Path string without its final extension.
    """
    return os.path.splitext(path)[0]


def is_path_head(path: str) -> bool:
    """
    Determin if a path string is a path head.

    >>> is_path_head('path.ext')
    True

    >>> is_path_head('/dir/path.ext')
    False

    Args:
        path (str): Path string.

    Returns:
        bool: If the path string is a path head.
    """
    return path_head(path) == path


def replace_head(path: str, head: str) -> str:
    """
    >>> replace_head('original', 'replacement')
    'replacement'

    >>> replace_head('folder/original', 'replacement')
    'folder/replacement'
    """
    return os.path.join(path_tail(path), head)


def replace_tail(path: str, search: str, replace: str) -> str:
    """
    >>> replace_tail('/dir1/dir2/path.ext', '/dir1', '/dir2')
    'dir2/dir2/path.ext'

    >>> replace_tail('/dir1/dir2/path.ext', '/dir1/', '/dir2/')
    'dir2/dir2/path.ext'

    >>> replace_tail('/dir1/dir2/path.ext', '/dir3', '/dir2')
    '/dir1/dir2/path.ext'
    """
    # Ensure the search path has a trailing slash
    search = os.path.join(search, "")

    # Ensure the search path has a trailing slash and no leading slash
    replace = os.path.join(replace, "")
    replace = replace[1:] if replace.startswith(os.path.sep) else replace

    return path.replace(search, replace, 1) if path.startswith(search) else path


def trim_tail(path: str, search: str) -> str:
    """
    >>> trim_tail('/dir1/dir2/path.ext', '/dir1')
    'dir2/path.ext'

    >>> trim_tail('/dir1/dir2/path.ext', '/dir1/')
    'dir2/path.ext'

    >>> trim_tail('/dir1/dir2/path.ext', '/dir3')
    '/dir1/dir2/path.ext'
    """
    return replace_tail(path, search, "")


def replace_ext(path: str, ext: str) -> str:
    """
    Replace a path's extension with another.

    >>> replace_ext('/dir1/dir2/path.ext', '.ext2')
    '/dir1/dir2/path.ext2'

    Args:
        path (str): Path string.
        ext (str): New extension.

    Returns:
        str: Path string with new extension.
    """
    return path.replace(os.path.splitext(path)[1], ext)


def remove_ext(path: str) -> str:
    """
    >>> remove_ext('/dir1/dir2/path.ext')
    '/dir1/dir2/path'

    >>> remove_ext('/dir1/dir2/path.ext1.ext2')
    '/dir1/dir2/path.ext1'
    """
    return replace_ext(path, "")


def reverse_to_root(project_root: str, output_dir: str) -> str:
    """
    Get the relative path required to move to a project's root
    from some output directory.

    >>> reverse_to_root('/dir1/dir2', '/dir1/dir3')
    '../dir2'

    Args:
        project_root (str): Root path string.
        output_dir (str): Directory path string.

    Returns:
        str: Path string.
    """
    return os.path.relpath(
        project_root,
        os.path.realpath(output_dir),
    )


def abs_from_root(root: str, rel: str) -> str:
    """
    Get the absolute path relative to a root path.

    >>> abs_from_root('dir1/dir2/path1.ext', 'path2.ext')
    'dir1/dir2/path2.ext'

    Args:
        path (str): Path string.
    """
    return os.path.normpath(os.path.join(os.path.dirname(root), rel))


def get_module_path(path: str) -> str:
    """
    Get the directory of a module's path.

    Args:
        path (str): Module name.

    Raises:
        ModuleNotFoundError: Module not found.

    Returns:
        str: Directory of the module's path.
    """
    return path_tail(import_module(path).__file__)


def full_listdir(path: str) -> List[str]:
    return [os.path.normpath(os.path.join(path, i)) for i in os.listdir(path)]


def rebase(path: str, src: str, dest: str) -> str:
    """
    >>> rebase('dir1/path.ext', 'dir1', 'dir2')
    'dir2/path.ext'

    >>> rebase('dir1/dir2/path.ext', 'dir1/dir2', 'dir2')
    'dir2/path.ext'
    """
    return os.path.join(dest, os.path.relpath(path, src))


def leads_path(segment: str, path: str) -> bool:
    """
    >>> leads_path('dir', 'dir/path.ext')
    True

    >>> leads_path('dir', 'dir')
    True

    >>> leads_path('dir2/dir1', 'dir1')
    False
    """
    return (
        segment == path
        or path.startswith(segment)
        and path[len(segment)] == os.path.sep
    )
