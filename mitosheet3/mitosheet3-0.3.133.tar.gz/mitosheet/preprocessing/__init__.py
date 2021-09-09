#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Preprocessing occurs to data that is imported into the sheet, and occurs
to _any_ data that is input into the mitosheet - they always occur, and
require no user input. 

Which pre-process step, and the version of it that is used 
"""

from typing import List

from mitosheet.preprocessing.preprocess_step_performer import PreprocessStepPerformer
from mitosheet.preprocessing.preprocess_read_file_paths import ReadFilePathsPreprocessStepPerformer
from mitosheet.preprocessing.preprocess_check_args_type import CheckArgsTypePreprocessStepPerformer
from mitosheet.preprocessing.preprocess_copy import CopyPreprocessStepPerformer


# NOTE: these should be in the order you want to apply them to the arguments,
# as they are run in a linear order
PREPROCESS_STEP_PERFORMERS: List[PreprocessStepPerformer] = [
   # First, we make sure all the args are the right type
   CheckArgsTypePreprocessStepPerformer,
   # Then, we copy the args to make sure we don't change them accidently
   CopyPreprocessStepPerformer,
   # Then, we read in the files
   ReadFilePathsPreprocessStepPerformer,
]

