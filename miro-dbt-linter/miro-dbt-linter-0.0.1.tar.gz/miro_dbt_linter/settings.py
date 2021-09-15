import os
from typing import Union

import pydantic


class Project(pydantic.BaseModel):
    manifest: Union[None, 'Manifest'] = None
    catalog: Union[None, 'Catalog'] = None


class Settings:
    project = Project()
    default_catalog_path = os.path.join('.', 'target', 'catalog.json')
    default_manifest_path = os.path.join('.', 'target', 'manifest.json')
    default_models_path = os.path.join('.', 'models')
    default_lint_rules_module = 'lint_rules.py'
