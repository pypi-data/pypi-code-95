from typing import List

from annotell.openlabel.models.datamodel import FrameInterval


def get_frame_intervals(all_timestamps: List, object_timestamps: List) -> List[FrameInterval]:
    all_timestamps = sorted(all_timestamps)
    object_timestamps = sorted(object_timestamps)

    missing_timestamps = sorted(list(set(all_timestamps).difference(set(object_timestamps))))
    missing_timestamps = [ts for ts in missing_timestamps if object_timestamps[0] <= ts <= object_timestamps[-1]]

    previous_ts_index = 0
    frame_intervals = []
    for timestamp in missing_timestamps:
        index_missing = all_timestamps.index(timestamp)
        ts_before_missing = all_timestamps[index_missing - 1]
        if ts_before_missing not in object_timestamps:
            continue

        last_interval_index = object_timestamps.index(ts_before_missing) + 1
        interval = object_timestamps[previous_ts_index:last_interval_index]
        frame_intervals.append(FrameInterval(frame_start=interval[0], frame_end=interval[-1]))
        previous_ts_index = last_interval_index

    interval = object_timestamps[previous_ts_index:]
    frame_intervals.append(FrameInterval(frame_start=interval[0], frame_end=interval[-1]))

    return frame_intervals
