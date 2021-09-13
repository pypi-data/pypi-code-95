from ..client import (
    Boto3Client
)


class BatchClient(Boto3Client):
    """
    """
    
    def __init__(self):
        """
        """
        super().__init__('batch')

    def submit_train_pipeline_job(self,
                                  project_id: int,
                                  version_id: int,
                                  timeout: int = 3600*24*5):
        """
        """
        environment = [
            {"name": "PROJECT_ID", "value": str(project_id)},
            {"name": "VERSION_ID", "value": str(version_id)}
        ]
        job = self.submit_job(
            jobName=f"train-pipeline-project_{project_id}-version_{version_id}",
            jobQueue='train-queue',
            jobDefinition='train-pipeline-job-definition',
            containerOverrides={'environment': environment},
            timeout={'attemptDurationSeconds': timeout}
        )
        return job
