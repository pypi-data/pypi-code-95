#    Copyright 2021 Qruise project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from ._client import QOptimizerClient, create_optimizer_client
from ._endpoint import Endpoint, EndpointSecureKey
from ._fom import (EvaluateFigureOfMerit, EvaluateFigureOfMeritFactory,
                  FigureOfMerit, Pulse)
from ._observer import (IterationResult, OptimizationObserver,
                       RunMetaParameters, ParameterMeta, PulseMeta, OptimizationResultCollector)

from ._browser import BrowserPresenter

__all__ = [
    "create_optimizer_client",
    "BrowserPresenter",
    "Endpoint",
    "EndpointSecureKey",
    "EvaluateFigureOfMerit",
    "EvaluateFigureOfMeritFactory",
    "FigureOfMerit",
    "IterationResult",
    "OptimizationObserver", 
    "RunMetaParameters",
    "ParameterMeta",
    "Pulse",
    "PulseMeta",
    "QOptimizerClient",
    "OptimizationResultCollector",
]
