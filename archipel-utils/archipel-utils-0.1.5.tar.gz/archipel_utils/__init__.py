"""Copyright Alpine Intuition Sàrl team.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import warnings

try:
    from .data import *  # noqa
except ImportError:
    with warnings.catch_warnings():
        warnings.simplefilter("always", ImportWarning)
        warnings.warn(
            "Missing packages, you will not be able to use archipel 'data' "
            + "utils, others remain usable. To fix: pip install opencv numpy",
            ImportWarning,
        )

from .msg import *  # noqa
from .path import *  # noqa
from .process import *  # noqa

__version__ = "0.1.5"
