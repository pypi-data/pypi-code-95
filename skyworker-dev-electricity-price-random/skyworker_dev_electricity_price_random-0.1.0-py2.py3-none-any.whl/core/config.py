"""
This file is part of the Omedia Skyworker Processor.

(c) 2021 Omedia <welcome@omedia.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

Written by Temuri Takalandze <t.takalandze@omedia.dev>, September 2021
"""


class _Input:
    # DO NOT touch these attributes! They will be initialized later.
    TIME_SERIES = {}
    TAGS = {}


class Config:
    """
    Configuration class for the AI Processor.
    """

    # DO NOT touch these attributes! They will be initialized later.
    NAME = None
    VERSION = None
    DESCRIPTION = None
    MEASUREMENTS = []
    INPUT = _Input()
