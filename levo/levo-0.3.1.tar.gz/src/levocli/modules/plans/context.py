import os
import shutil
from typing import Dict, List, Optional

import attr
from levo_commons.models import TestResult

from .models import Plan


@attr.s(slots=True)
class TestSuiteExecutionContext:
    """Contextual information for the test suite that's being executed."""

    test_item_id: str = attr.ib()
    operations_processed: int = attr.ib(default=0)
    test_case_id_to_item_id: Dict = attr.ib(factory=dict)
    results: List[TestResult] = attr.ib(factory=list)


@attr.s(slots=True)
class ExecutionContext:
    """Contextual information for the test plan that's being executed."""

    plan: Plan = attr.ib()
    workers_num: int = attr.ib(default=1)
    show_errors_tracebacks: bool = attr.ib(default=False)
    current_line_length: int = attr.ib(default=0)
    terminal_size: os.terminal_size = attr.ib(factory=shutil.get_terminal_size)
    cassette_file_name: Optional[str] = attr.ib(default=None)
    junit_xml_file: Optional[str] = attr.ib(default=None)
    verbosity: int = attr.ib(default=0)
    test_suite_id_to_context: Dict = attr.ib(factory=dict)
