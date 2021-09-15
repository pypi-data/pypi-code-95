import os
from argparse import ArgumentParser

from .settings import Settings
from .version import version


parser = ArgumentParser(description='Extensible linter for dbt projects')

parser.add_argument(
    '--debug',
    help='Print configuration information and exit',
    action='store_true'
)

parser.add_argument(
    '--version',
    help="Print version information and exit",
    action="version",
    version=version
)

parser.add_argument(
    'models',
    help="Path to a set of dbt models to lint",
    nargs=1
)

parser.add_argument(
    '--manifest', 
    help="Path to dbt's manifest.json artifact. Defaults to ./target/manifest.json",
    default=Settings.default_manifest_path,
    dest='manifest_path'
)

parser.add_argument(
    '--catalog',
    help="Path to dbt's catalog.json artifact. Defaults to ./target/catalog.json",
    default=Settings.default_catalog_path,
    dest='catalog_path'
)

# Quick and dirty way to enable importing the lint rules.
parser.add_argument(
    '--lint-rules',
    help="Name of an importable python module with linting rules. Defaults to "
         "{Settings.default_lint_rules_model}. Must be importable.",
    default=Settings.default_lint_rules_module,
    dest='lint_rules_module'
)