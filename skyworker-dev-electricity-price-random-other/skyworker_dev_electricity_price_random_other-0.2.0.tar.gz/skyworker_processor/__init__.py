"""
Source package for the Skyworker Processor.

This file is part of the Omedia Skyworker Processor.

(c) 2021 Omedia <welcome@omedia.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

Written by Temuri Takalandze <t.takalandze@omedia.dev>, August 2021
"""

from skyworker_processor.core.processor import process
from skyworker_processor.core.config import Config

__project__ = "skyworker_dev_electricity_price_random_other"
__version__ = "0.2.0"
__description__ = 'This processor creates random Time Series of the "Electricity Price" measurement with other random algorithm.'
__measurements__ = ["Electricity Price"]
__time_series__ = {
    "time_series_1": {
        "name": "Time Series 1",
        "description": "Description of time_series_1",
    },
}
__tags__ = {
    "tag_1": {
        "name": "Tag 1",
        "type": "number",
        "description": "Description of tag_1",
    },
    "tag_2": {
        "name": "Tag 2",
        "type": "string",
        "description": "Description of tag_3",
    }
}

__author__ = "Temuri Takalandze"
__copyright__ = "(c) 2021 Omedia"
__email__ = "welcome@omedia.dev"
__credits__ = ["Omedia", "Siemens"]
__license__ = "Other/Proprietary License"
__status__ = "Development"

Config.NAME = __project__[10:]  # Remove the "skyworker_" prefix.
Config.VERSION = __version__
Config.DESCRIPTION = __description__
Config.MEASUREMENTS = __measurements__
Config.INPUT.TIME_SERIES = __time_series__
Config.PARAMETERS.TAGS = __tags__
