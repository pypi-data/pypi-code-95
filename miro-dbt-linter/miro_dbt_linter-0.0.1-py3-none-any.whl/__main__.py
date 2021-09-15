from argparse import ArgumentParser
import os
import sys

from .cli import parser
from .linter import Linter


def main():
    namespace = parser.parse_args()

    if len(sys.argv) == 1:
        namespace.print_help()
    else:
        linter = Linter(
            manifest_path=namespace.manifest_path,
            catalog_path=namespace.catalog_path,
            lint_rules_module=namespace.lint_rules_module.replace('.py', '')
        )

        if namespace.debug:
            print(linter.to_json())
        else:
            linter.run()



if __name__ == "__main__":
    main()