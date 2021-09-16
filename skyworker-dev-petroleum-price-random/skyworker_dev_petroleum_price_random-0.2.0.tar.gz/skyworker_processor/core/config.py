"""
This file is part of the Omedia Skyworker Processor.

(c) 2021 Omedia <welcome@omedia.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

Written by Temuri Takalandze <t.takalandze@omedia.dev>, September 2021
"""

# pylint: disable=R0903


class _Input:
    """
    Configuration class for the AI Processor's input data.
    """

    # DO NOT touch these attributes! They will be initialized later.
    TIME_SERIES = {}


class _Parameters:
    """
    Configuration class for the AI Processor's parameters.
    """

    # DO NOT touch these attributes! They will be initialized later.
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
    PARAMETERS = _Parameters()
