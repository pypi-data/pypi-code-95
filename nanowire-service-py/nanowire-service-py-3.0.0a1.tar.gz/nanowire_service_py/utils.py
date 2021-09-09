from typing import Dict, List
import json
from datetime import datetime, timezone

from .types import MultiInput, GroupedInput

from typing import Any, Dict, List
import json

from pydantic import BaseModel, ValidationError
from dapr.clients import DaprClient

from .types import ChildAction, Environment, Task, TaskOutput, PluginOutput
from .logger import Logger


def find(xs, f):
    for x in xs:
        if f(x):
            return x
    return None


def path(path, obj):
    value = obj
    for part in path:
        if part in value:
            value = value[part]
        else:
            return None
    return value


# Handles datetime better
def safe_json(o):
    if isinstance(o, datetime):
        return o.__str__()


def safe_dump(d):
    return json.dumps(d, default=safe_json)


def now():
    return datetime.now(timezone.utc).isoformat()


def group_input(
    args: Dict[str, MultiInput], meta: Dict[str, MultiInput]
) -> List[GroupedInput]:
    output = []
    for key, entry in args.items():
        output.append(
            GroupedInput(
                plugin=entry.plugin, args=entry.value, meta=meta[key].value
            )
        )
    return output


def children_actions(
    task: Task, args: Dict[str, Any], meta: Dict[str, Any] = {}
) -> List[ChildAction]:
    if task.children is None:
        return []
    return [
        ChildAction(
            parent=task.current.id,
            child=c.id,
            plugin=c.plugin,
            args=args,
            meta=meta,
        )
        for c in task.children
    ]
