"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""
# flake8: noqa
# Unused imports on purpose

# Try to import what we need from DataRobot Python Client, backwards-compatible.
try:
    from datarobot._experimental.models.user_blueprints.models import *
    from datarobot._experimental import UserBlueprint
except (ImportError, ModuleNotFoundError):
    pass

try:
    from datarobot._experimental import CustomTrainingModel as CustomTask
except (ImportError, ModuleNotFoundError):
    pass

try:
    from datarobot.models.user_blueprints.models import *
    from datarobot import UserBlueprint
    from datarobot import CustomTask
except (ImportError, ModuleNotFoundError):
    pass
