import importlib
import inspect
import json
import pathlib
import os

from .settings import Settings
from .models import Manifest, Catalog
from .rules import LintRule


class Linter(object):
    """
    Handler for applying linter rules.
    """

    def __init__(
            self, 
            manifest_path=Settings.default_manifest_path, 
            models_path=Settings.default_models_path, 
            catalog_path=Settings.default_catalog_path,
            lint_rules_module=Settings.default_lint_rules_module
        ):
        self.manifest_path = manifest_path
        self.models_path = models_path
        self.catalog_path = catalog_path
        self.lint_rules_module = lint_rules_module
        self.project = Settings.project
        self.project.manifest = Manifest.from_path(self.manifest_path)
        self.project.catalog = Catalog.from_path(self.catalog_path)

    def config(self):
        return {
            'manifest': {
                'path': self.manifest_path
            },
            'catalog': {
                'path': self.catalog_path
            },
            'rules': {
                'module': self.lint_rules_module,
                'classes': list(str(r) for r in self.load_lint_rules(self.lint_rules_module))
            },
            'models': {
                'path': self.models_path
            }
        }

    def to_json(self):
        return json.dumps(self.config(), indent=2)

    def load_lint_rules(self, lint_rules_module):
        module = importlib.import_module(lint_rules_module)
        for varname, varvalue in vars(module).items():
            if inspect.isclass(varvalue) and issubclass(varvalue, LintRule) and varvalue != LintRule:
                yield varvalue

    def iter_model_paths(self):
        for path in pathlib.Path(self.models_path).glob('**/*.sql'):
            yield path

    def run(self):
        paths = list(self.iter_model_paths())
        if len(paths) == 0:
            warnings.warn("No models selected.")
        else:
            lint_rules = list(self.load_lint_rules(self.lint_rules_module))
            for path in paths:
                model = self.project.manifest.get_model_from_path(path)
                if model is None:
                    warnings.warn(f"Path {path} is not associated with any models in the manifest.json"
                                  f"artifact. This is likely a result of an out of date manifest.")
                else:
                    print(model.name)
                    for Rule in lint_rules:
                        Rule(model).run()
                    print()
