#!/usr/bin/env python
# coding: utf8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from copy import deepcopy
from typing import Any, Dict, List, Optional

from mitosheet.errors import make_column_exists_error
from mitosheet.parser import safe_replace
from mitosheet.state import State
from mitosheet.step_performers.column_steps.set_column_formula import \
    _update_column_formula_in_step
from mitosheet.step_performers.step_performer import StepPerformer


class RenameColumnStepPerformer(StepPerformer):
    """"
    A rename_column step, which allows you to rename a column
    in a dataframe.
    """

    @classmethod
    def step_version(cls) -> int:
        return 2

    @classmethod
    def step_type(cls) -> str:
        return 'rename_column' 

    @classmethod
    def step_display_name(cls) -> str:
        return 'Renamed a Column'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'rename_column_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        column_id: str,
        new_column_header: str,
        **params
    ) -> State:
        if new_column_header in prev_state.dfs[sheet_index].keys():
            raise make_column_exists_error(new_column_header)

        # Create a new post state for this step
        post_state = deepcopy(prev_state)

        rename_column_headers_in_state(
            post_state,
            sheet_index,
            column_id,
            new_column_header
        )

        return post_state, None

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        column_id: str,
        new_column_header: str
    ) -> List[str]:
        df_name = post_state.df_names[sheet_index]
        old_column_header = prev_state.column_ids.get_column_header_by_id(sheet_index, column_id)
        rename_dict = "{\"" + old_column_header + "\": \"" + new_column_header + "\"}"
        return [f'{df_name}.rename(columns={rename_dict}, inplace=True)']

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        column_id: str,
        new_column_header: str,
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            df_name = df_names[sheet_index]
            return f'Renamed {column_id} to {new_column_header} in {df_name}'
        return f'Renamed {column_id} to {new_column_header}'


def rename_column_headers_in_state(
        post_state: State,
        sheet_index: int,
        column_id: str,
        new_column_header: Any
    ):
    """
    A helper function for updating a column header in the state, which is useful
    for both this rename step and for the bulk rename step.
    """
    old_column_header = post_state.column_ids.get_column_header_by_id(sheet_index, column_id)

    # Save original column headers, so we can use them below
    original_column_headers = list(post_state.dfs[sheet_index].keys())

    # Execute the rename
    post_state.dfs[sheet_index].rename(columns={old_column_header: new_column_header}, inplace=True)

    # Fix the column Python code, for this column
    post_state.column_python_code[sheet_index][column_id] = post_state.column_python_code[sheet_index][column_id].replace(
        f'df[\'{old_column_header}\']',
        f'df[\'{new_column_header}\']'
    )

    # We also have to go over _all_ the formulas in the sheet that reference this column, and update
    # their references to the new column. 
    for other_column_id in post_state.column_evaluation_graph[sheet_index][column_id]:
        old_formula = post_state.column_spreadsheet_code[sheet_index][other_column_id]
        new_formula = safe_replace(
            old_formula,
            old_column_header,
            new_column_header,
            original_column_headers
        )
        _update_column_formula_in_step(
            post_state, 
            sheet_index, 
            other_column_id, 
            old_formula, 
            new_formula,
            update_from_rename=True
        )

    # Update the column header
    post_state.column_ids.set_column_header(sheet_index, column_id, new_column_header)
    
    return post_state