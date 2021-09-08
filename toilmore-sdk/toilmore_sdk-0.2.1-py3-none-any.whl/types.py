from enum import Enum


class RecordState(Enum):
    JUST_RECEIVED = 0
    HASH_COMPUTED = 1
    INITIAL_QUERY_FOR_STATE_COMPLETED = 2
    IMAGE_BYTES_POSTED = 3
    OPTIMIZED_IMAGE_PRESIGNED_ACQUIRED = 4
    OPTIMIZATION_COMPLETE = 5
    OPTIMIZATION_FAILED = 6
    TO_DELETE = 7

    def next_state(self):

        if self.is_final():
            raise Exception('It is already on a final state!')

        return self.value + 1

    def is_final(self):

        return (
            self == RecordState.OPTIMIZATION_COMPLETE or
            self == RecordState.OPTIMIZATION_FAILED
        )
