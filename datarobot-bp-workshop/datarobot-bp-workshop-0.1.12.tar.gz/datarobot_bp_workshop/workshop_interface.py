"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""

from typing import Dict, Optional, List

from .datarobot_client import (
    UserBlueprintAvailableTasks,
    UserBlueprintTaskArgument,
    UserBlueprintTaskDefinition,
    ColnameAndType,
)

from datarobot_bp_workshop.auto_rate_limiter import AutoRateLimiter
from datarobot_bp_workshop.sharing import SharingInterface


class WorkshopInterface(SharingInterface):
    """ Interface to use to allow working with a Workshop in BlueprintGraph and Task. """

    def __init__(self, project_id=None, enforce_rate_limit=True):
        self._task_definitions_by_task_code: Dict[str, UserBlueprintTaskDefinition] = {}
        self._custom_task_definitions_by_task_code: Dict[
            str, List[UserBlueprintTaskDefinition]
        ] = {}
        self._custom_tasks_by_id: Dict[str, UserBlueprintTaskDefinition] = {}
        self._custom_tasks_by_version_id: Dict[str, UserBlueprintTaskDefinition] = {}
        self._task_argument_lookup: Dict[str, Dict[str:UserBlueprintTaskArgument]] = {}
        self._input_name_lookup: Dict[str, str] = {}
        self._available_tasks: Optional[UserBlueprintAvailableTasks] = None
        self._colname_and_type_colname_lookup: Dict[str, ColnameAndType] = {}
        self._colname_and_type_hex_lookup: Dict[str, ColnameAndType] = {}
        self._project_id: Optional[str] = project_id
        self._associated_user_blueprint_id: Optional[str] = None

        self.auto_rate_limiter: AutoRateLimiter = (
            AutoRateLimiter() if enforce_rate_limit else AutoRateLimiter(0)
        )
