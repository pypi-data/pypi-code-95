from pathlib import Path
from common import change_user_path, get_user

res = get_user(Path("/home/foo/bar"))
assert res == "foo"

res = get_user(Path("hola/adios/home/foo/bar"), Path("hola/adios"))
assert res == "foo"

res = change_user_path(Path("/home/foo/bar"), "baz")
assert res == Path("/home/baz/bar")

res = change_user_path(Path("hola/adios/home/foo/bar"), "baz", Path("hola/adios"))
assert res == Path("hola/adios/home/baz/bar")
