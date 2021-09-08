import json

import pandas as pd
from mitosheet.sheet_functions.types.utils import NUMBER_SERIES, get_mito_type
from mitosheet.utils import df_to_json_dumpsable

def get_unique_value_counts(event, steps_manager):
    """
    Sends back a string that can be parsed to a JSON object that
    contains the normalized value counts for the series at column_id 
    in the df at sheet_index.
    """
    sheet_index = event['sheet_index']
    column_id = event['column_id']

    column_header = steps_manager.curr_step.column_ids.get_column_header_by_id(sheet_index, column_id)
    
    series: pd.Series = steps_manager.dfs[sheet_index][column_header]

    unique_value_counts_percents_series = series.value_counts(normalize=True, dropna=False)
    unique_value_counts_series = series.value_counts(dropna=False)
    
    unique_value_counts_df = pd.DataFrame({
        'values': unique_value_counts_percents_series.index,
        'percents': unique_value_counts_percents_series, 
        'counts': unique_value_counts_series
        })

    unique_value_counts_df = pd.DataFrame(unique_value_counts_df)

    try:
        return json.dumps(df_to_json_dumpsable(
            unique_value_counts_df, 
            {'values': 'values', 'percents': 'percents', 'counts': 'counts'},
            False
        ))

    except:
        # As this is also a non-critical error, we don't want to display an error
        # message in the case of failure, so we just return nothing
        return ''
