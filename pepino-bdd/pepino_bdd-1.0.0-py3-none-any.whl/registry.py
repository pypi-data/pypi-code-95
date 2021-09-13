import importlib
import threading
import pathlib
import re
import time
from functools import partial
from typing import Callable, Dict, Any

from .enums import Hook


class CucumberRegistry:

    def __init__(self):
        self._step_dict: Dict[str, Callable] = {}
        self._hooks_dicts = {hk: [] for hk in Hook}
        self._types: Dict[Any, Callable] = {}
        self._step_cls_objects: Dict[str, object] = {}
        self._instance_lock = threading.Lock()

    @property
    def step_dict(self) -> Dict[str, Callable]:
        return self._step_dict

    def load_from_path(self, pattern: str):
        for pyfile in pathlib.Path(".").glob("**/*.py"):
            if re.search(pattern, pyfile.as_posix()):
                mod = pyfile.as_posix()[:-3].replace("/", ".")
                importlib.import_module(mod)

    def add_step(self, pattern: str, func: Callable):
        qualname = func.__qualname__
        if len(qualname.split(".")) > 1:
            self._instance_lock.acquire()
            inst_name = f'{func.__module__}.{".".join(qualname.split(".")[:-1])}'
            if inst_name not in self._step_cls_objects:
                qualparts = qualname.split(".")
                clses = qualparts[:-1]
                modname = func.__module__
                mod_obj = importlib.import_module(modname)
                current_cls = mod_obj
                time.sleep(0.01)
                for cls in clses:
                    current_cls = getattr(current_cls, cls)
                self._step_cls_objects[inst_name] = current_cls()  # type: ignore
            func = partial(func, self._step_cls_objects[inst_name])
            self._instance_lock.release()
        self._step_dict[pattern] = func

    def add_type(self, type_var: Any, func: Callable):
        self._types[type_var] = func

    def get_type_func(self, type_var: Any):
        return self._types.get(type_var, type_var)

    def add_hook(self, hook: Hook, func: Callable):
        self._hooks_dicts[hook].append(func)

    def run_hooks(self, hook, obj):
        for func in self._hooks_dicts[hook]:
            nobj = func(obj)
            obj = nobj if nobj else obj
        return obj


registry = CucumberRegistry()
