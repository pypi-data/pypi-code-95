from ..client import (
    Boto3Client
)



class ECSClient(Boto3Client):
    """
    """
    
    def __init__(self):
        """
        """
        super().__init__('ecs')
