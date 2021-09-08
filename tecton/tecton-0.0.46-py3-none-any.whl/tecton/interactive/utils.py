from tecton._internals import errors


def run_batch(feature_start_time, feature_end_time, mock_inputs, aggregate_tiles) -> tecton.DataFrame:
    raise errors.UNSUPPORTED_OPERATION("run_batch", "Unimplemented.")


def run_stream(output_temp_table):
    raise errors.UNSUPPORTED_OPERATION("run_stream", "Unimplemented.")


def run_ondemand(join_keys, mock_inputs) -> tecton.DataFrame:
    raise errors.UNSUPPORTED_OPERATION("run_ondemand", "Unimplemented.")
