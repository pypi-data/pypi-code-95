#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from copy import deepcopy
from typing import Any, Dict, List, Optional

from mitosheet.errors import make_invalid_column_delete_error
from mitosheet.state import State
from mitosheet.step_performers.step_performer import StepPerformer


class DeleteColumnStepPerformer(StepPerformer):
    """"
    A delete_column step, which allows you to delete a column
    from a dataframe.
    """
    @classmethod
    def step_version(cls) -> int:
        return 2

    @classmethod
    def step_type(cls) -> str:
        return 'delete_column'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Deleted a Column'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'delete_column_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        column_id: str,
        **params
    ) -> State:
        
        column_header = prev_state.column_ids.get_column_header_by_id(sheet_index, column_id)
        
        # Error if there are any columns that currently rely on this column
        if len(prev_state.column_evaluation_graph[sheet_index][column_id]) > 0:
            raise make_invalid_column_delete_error(
                column_header,
                list(prev_state.column_evaluation_graph[sheet_index][column_id])
            )

        # Make a post state, that is a deep copy
        post_state = deepcopy(prev_state)
        
        # Actually drop the column
        df = post_state.dfs[sheet_index]
        df.drop(column_header, axis=1, inplace=True)

        # And then update all the state variables removing this column from the state
        del post_state.column_metatype[sheet_index][column_id]
        del post_state.column_type[sheet_index][column_id]
        del post_state.column_spreadsheet_code[sheet_index][column_id]
        del post_state.column_python_code[sheet_index][column_id]
        del post_state.column_evaluation_graph[sheet_index][column_id]
        # We also have to delete the places in the graph where this node is 
        for dependents in post_state.column_evaluation_graph[sheet_index].values():
            if column_id in dependents:
                dependents.remove(column_id)
        # Clean up the IDs
        post_state.column_ids.delete_column_id(sheet_index, column_id)
        
        return post_state, None

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        column_id: str
    ) -> List[str]:
        df_name = post_state.df_names[sheet_index]
        column_header = prev_state.column_ids.get_column_header_by_id(sheet_index, column_id)

        return [f'{df_name}.drop(\'{column_header}\', axis=1, inplace=True)']

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        column_id: str,
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            df_name = df_names[sheet_index]
            return f'Deleted column {column_id} from {df_name}'
        return f'Deleted column {column_id}'
