import sys

from .rules import LintRule
from .linter import Linter
from .models import Node
from .version import version as __version__

# Needed for importing the user's lint_rules.py 
sys.path.append('.')
