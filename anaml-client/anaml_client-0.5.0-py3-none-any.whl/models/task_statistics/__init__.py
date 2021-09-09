"""Generated implementation of task_statistics."""

# WARNING DO NOT EDIT
# This code was generated from task-statistics.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import logging  # noqa: F401
import uuid  # noqa: F401
import typing  # noqa: F401
import jsonschema  # noqa: F401


@dataclasses.dataclass(frozen=True)
class TaskStatistics:
    """Execution statistics for a job task.
    
    Args:
        stageId (int): A data field.
        stageAttemptId (int): A data field.
        taskType (str): A data field.
        index (int): A data field.
        taskId (int): A data field.
        attemptNumber (int): A data field.
        launchTime (int): A data field.
        finishTime (int): A data field.
        duration (int): A data field.
        schedulerDelay (int): A data field.
        executorId (str): A data field.
        host (str): A data field.
        taskLocality (str): A data field.
        speculative (bool): A data field.
        gettingResultTime (int): A data field.
        successful (bool): A data field.
        executorRunTime (int): A data field.
        executorCpuTime (int): A data field.
        executorDeserializeTime (int): A data field.
        executorDeserializeCpuTime (int): A data field.
        resultSerializationTime (int): A data field.
        jvmGCTime (int): A data field.
        resultSize (int): A data field.
        numUpdatedBlockStatuses (int): A data field.
        diskBytesSpilled (int): A data field.
        memoryBytesSpilled (int): A data field.
        peakExecutionMemory (int): A data field.
        recordsRead (int): A data field.
        bytesRead (int): A data field.
        recordsWritten (int): A data field.
        bytesWritten (int): A data field.
        shuffleFetchWaitTime (int): A data field.
        shuffleTotalBytesRead (int): A data field.
        shuffleTotalBlocksFetched (int): A data field.
        shuffleLocalBlocksFetched (int): A data field.
        shuffleRemoteBlocksFetched (int): A data field.
        shuffleWriteTime (int): A data field.
        shuffleBytesWritten (int): A data field.
        shuffleRecordsWritten (int): A data field.
        statusMessage (typing.Optional[str]): A data field.
    """
    
    stageId: int
    stageAttemptId: int
    taskType: str
    index: int
    taskId: int
    attemptNumber: int
    launchTime: int
    finishTime: int
    duration: int
    schedulerDelay: int
    executorId: str
    host: str
    taskLocality: str
    speculative: bool
    gettingResultTime: int
    successful: bool
    executorRunTime: int
    executorCpuTime: int
    executorDeserializeTime: int
    executorDeserializeCpuTime: int
    resultSerializationTime: int
    jvmGCTime: int
    resultSize: int
    numUpdatedBlockStatuses: int
    diskBytesSpilled: int
    memoryBytesSpilled: int
    peakExecutionMemory: int
    recordsRead: int
    bytesRead: int
    recordsWritten: int
    bytesWritten: int
    shuffleFetchWaitTime: int
    shuffleTotalBytesRead: int
    shuffleTotalBlocksFetched: int
    shuffleLocalBlocksFetched: int
    shuffleRemoteBlocksFetched: int
    shuffleWriteTime: int
    shuffleBytesWritten: int
    shuffleRecordsWritten: int
    statusMessage: typing.Optional[str]
    
    @classmethod
    def json_schema(cls):
        """Return the JSON schema for TaskStatistics data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "stageId": {
                    "type": "integer"
                },
                "stageAttemptId": {
                    "type": "integer"
                },
                "taskType": {
                    "type": "string"
                },
                "index": {
                    "type": "integer"
                },
                "taskId": {
                    "type": "integer"
                },
                "attemptNumber": {
                    "type": "integer"
                },
                "launchTime": {
                    "type": "integer"
                },
                "finishTime": {
                    "type": "integer"
                },
                "duration": {
                    "type": "integer"
                },
                "schedulerDelay": {
                    "type": "integer"
                },
                "executorId": {
                    "type": "string"
                },
                "host": {
                    "type": "string"
                },
                "taskLocality": {
                    "type": "string"
                },
                "speculative": {
                    "type": "boolean"
                },
                "gettingResultTime": {
                    "type": "integer"
                },
                "successful": {
                    "type": "boolean"
                },
                "executorRunTime": {
                    "type": "integer"
                },
                "executorCpuTime": {
                    "type": "integer"
                },
                "executorDeserializeTime": {
                    "type": "integer"
                },
                "executorDeserializeCpuTime": {
                    "type": "integer"
                },
                "resultSerializationTime": {
                    "type": "integer"
                },
                "jvmGCTime": {
                    "type": "integer"
                },
                "resultSize": {
                    "type": "integer"
                },
                "numUpdatedBlockStatuses": {
                    "type": "integer"
                },
                "diskBytesSpilled": {
                    "type": "integer"
                },
                "memoryBytesSpilled": {
                    "type": "integer"
                },
                "peakExecutionMemory": {
                    "type": "integer"
                },
                "recordsRead": {
                    "type": "integer"
                },
                "bytesRead": {
                    "type": "integer"
                },
                "recordsWritten": {
                    "type": "integer"
                },
                "bytesWritten": {
                    "type": "integer"
                },
                "shuffleFetchWaitTime": {
                    "type": "integer"
                },
                "shuffleTotalBytesRead": {
                    "type": "integer"
                },
                "shuffleTotalBlocksFetched": {
                    "type": "integer"
                },
                "shuffleLocalBlocksFetched": {
                    "type": "integer"
                },
                "shuffleRemoteBlocksFetched": {
                    "type": "integer"
                },
                "shuffleWriteTime": {
                    "type": "integer"
                },
                "shuffleBytesWritten": {
                    "type": "integer"
                },
                "shuffleRecordsWritten": {
                    "type": "integer"
                },
                "statusMessage": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "stageId",
                "stageAttemptId",
                "taskType",
                "index",
                "taskId",
                "attemptNumber",
                "launchTime",
                "finishTime",
                "duration",
                "schedulerDelay",
                "executorId",
                "host",
                "taskLocality",
                "speculative",
                "gettingResultTime",
                "successful",
                "executorRunTime",
                "executorCpuTime",
                "executorDeserializeTime",
                "executorDeserializeCpuTime",
                "resultSerializationTime",
                "jvmGCTime",
                "resultSize",
                "numUpdatedBlockStatuses",
                "diskBytesSpilled",
                "memoryBytesSpilled",
                "peakExecutionMemory",
                "recordsRead",
                "bytesRead",
                "recordsWritten",
                "bytesWritten",
                "shuffleFetchWaitTime",
                "shuffleTotalBytesRead",
                "shuffleTotalBlocksFetched",
                "shuffleLocalBlocksFetched",
                "shuffleRemoteBlocksFetched",
                "shuffleWriteTime",
                "shuffleBytesWritten",
                "shuffleRecordsWritten",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict):
        """Validate and parse JSON data into an instance of TaskStatistics.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TaskStatistics.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TaskStatistics(
                stageId=int(data["stageId"]),
                stageAttemptId=int(data["stageAttemptId"]),
                taskType=str(data["taskType"]),
                index=int(data["index"]),
                taskId=int(data["taskId"]),
                attemptNumber=int(data["attemptNumber"]),
                launchTime=int(data["launchTime"]),
                finishTime=int(data["finishTime"]),
                duration=int(data["duration"]),
                schedulerDelay=int(data["schedulerDelay"]),
                executorId=str(data["executorId"]),
                host=str(data["host"]),
                taskLocality=str(data["taskLocality"]),
                speculative=bool(data["speculative"]),
                gettingResultTime=int(data["gettingResultTime"]),
                successful=bool(data["successful"]),
                executorRunTime=int(data["executorRunTime"]),
                executorCpuTime=int(data["executorCpuTime"]),
                executorDeserializeTime=int(data["executorDeserializeTime"]),
                executorDeserializeCpuTime=int(data["executorDeserializeCpuTime"]),
                resultSerializationTime=int(data["resultSerializationTime"]),
                jvmGCTime=int(data["jvmGCTime"]),
                resultSize=int(data["resultSize"]),
                numUpdatedBlockStatuses=int(data["numUpdatedBlockStatuses"]),
                diskBytesSpilled=int(data["diskBytesSpilled"]),
                memoryBytesSpilled=int(data["memoryBytesSpilled"]),
                peakExecutionMemory=int(data["peakExecutionMemory"]),
                recordsRead=int(data["recordsRead"]),
                bytesRead=int(data["bytesRead"]),
                recordsWritten=int(data["recordsWritten"]),
                bytesWritten=int(data["bytesWritten"]),
                shuffleFetchWaitTime=int(data["shuffleFetchWaitTime"]),
                shuffleTotalBytesRead=int(data["shuffleTotalBytesRead"]),
                shuffleTotalBlocksFetched=int(data["shuffleTotalBlocksFetched"]),
                shuffleLocalBlocksFetched=int(data["shuffleLocalBlocksFetched"]),
                shuffleRemoteBlocksFetched=int(data["shuffleRemoteBlocksFetched"]),
                shuffleWriteTime=int(data["shuffleWriteTime"]),
                shuffleBytesWritten=int(data["shuffleBytesWritten"]),
                shuffleRecordsWritten=int(data["shuffleRecordsWritten"]),
                statusMessage=(lambda v: v and str(v))(data.get("statusMessage", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TaskStatistics",
                exc_info=ex
            )
            raise
    
    def to_json(self):
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "stageId": int(self.stageId),
            "stageAttemptId": int(self.stageAttemptId),
            "taskType": str(self.taskType),
            "index": self.index,
            "taskId": self.taskId,
            "attemptNumber": int(self.attemptNumber),
            "launchTime": self.launchTime,
            "finishTime": self.finishTime,
            "duration": self.duration,
            "schedulerDelay": self.schedulerDelay,
            "executorId": str(self.executorId),
            "host": str(self.host),
            "taskLocality": str(self.taskLocality),
            "speculative": self.speculative,
            "gettingResultTime": self.gettingResultTime,
            "successful": self.successful,
            "executorRunTime": self.executorRunTime,
            "executorCpuTime": self.executorCpuTime,
            "executorDeserializeTime": self.executorDeserializeTime,
            "executorDeserializeCpuTime": self.executorDeserializeCpuTime,
            "resultSerializationTime": self.resultSerializationTime,
            "jvmGCTime": self.jvmGCTime,
            "resultSize": self.resultSize,
            "numUpdatedBlockStatuses": int(self.numUpdatedBlockStatuses),
            "diskBytesSpilled": self.diskBytesSpilled,
            "memoryBytesSpilled": self.memoryBytesSpilled,
            "peakExecutionMemory": self.peakExecutionMemory,
            "recordsRead": self.recordsRead,
            "bytesRead": self.bytesRead,
            "recordsWritten": self.recordsWritten,
            "bytesWritten": self.bytesWritten,
            "shuffleFetchWaitTime": self.shuffleFetchWaitTime,
            "shuffleTotalBytesRead": self.shuffleTotalBytesRead,
            "shuffleTotalBlocksFetched": self.shuffleTotalBlocksFetched,
            "shuffleLocalBlocksFetched": self.shuffleLocalBlocksFetched,
            "shuffleRemoteBlocksFetched": self.shuffleRemoteBlocksFetched,
            "shuffleWriteTime": self.shuffleWriteTime,
            "shuffleBytesWritten": self.shuffleBytesWritten,
            "shuffleRecordsWritten": self.shuffleRecordsWritten,
            "statusMessage": (lambda v: v and str(v))(self.statusMessage)
        }
