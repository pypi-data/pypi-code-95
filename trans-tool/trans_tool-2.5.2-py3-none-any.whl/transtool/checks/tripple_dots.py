"""
# trans-tool
# The translation files checker and syncing tool.
#
# Copyright ©2021 Marcin Orlowski <mail [@] MarcinOrlowski.com>
# https://github.com/MarcinOrlowski/trans-tool/
#
"""
import re
from typing import Dict, List, Union

from transtool.decorators.overrides import overrides
from transtool.report.group import ReportGroup
from .base.check import Check


# noinspection PyUnresolvedReferences
class Substitutions(Check):
    """
    Checks if brackets are used in translation and if so, ensures proper nesting and checks if all
    opened brackets are closed.
    """

    def __init__(self, config: Union[Dict, None] = None):
        super().__init__(config)
        self.is_single_file_check = True

    report_title = 'Substitutions'

    @overrides(Check)
    # Do NOT "fix" the PropFile reference and do not import it, or you step on circular dependency!
    def check(self, translation: 'PropFile', reference: 'PropFile' = None) -> ReportGroup:
        self.need_valid_config()

        if not translation.items:
            return report

        report = ReportGroup(self.report_title)

        for idx, item in enumerate(translation.items):
            # Do not try to be clever and filter() data first, because line_number values will no longer be correct.
            if self._shall_skip_item(item):
                continue

            for config in self.config['map']:
                # build search pattern
                pattern = re.compile(config["regexp"])

                for match in re.finditer(config["regexp"], item.value):
                    report.warn(f'{idx + 1}:{match.start()}',
                                f'Found "{match.group(1)}" that can be replaced with "{config["replace"]}".', item.key)

        return report

    @overrides(Check)
    def get_default_config(self) -> Dict:
        return {
            'comments': False,

            # Keep matching elements at the same positions
            'map':      [
                {
                    'regexp':  r'([\.]{3,})',
                    'replace': '…',
                },
                {
                    'regexp':  r'([\s]{2,})',
                    'replace': ' ',
                },
                {
                    'regexp':  r'([\!]{2,})',
                    'replace': '!',
                }
            ]
        }
