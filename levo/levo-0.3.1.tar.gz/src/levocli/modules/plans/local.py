import pathlib
from typing import Optional

from .models import Plan


def get_plan(plan_lrn: str, catalog: str, workspace_id: str) -> Optional[Plan]:
    """Method to read the local test plans from LOCAL_TEST_PLANS_CATALOG and return the list of them."""
    _catalog = pathlib.Path(catalog)
    plan_dir = _catalog / plan_lrn
    if plan_dir.is_dir():
        return Plan(lrn=plan_lrn, catalog=_catalog, workspace_id=workspace_id)
    return None
