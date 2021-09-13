import json
from ..client import Boto3Client


class SQSClient(Boto3Client):
    """
    """
    
    def __init__(self):
        """
        """
        super().__init__('sqs')

    def send_preprocess_job(self,
                            bucket: str,
                            document: dict,
                            pages: list):
        """
        """
        msg_body = {
            'bucket': bucket,
            'document': json.dumps(document),
            'pages': json.dumps(pages)
        }
        self.send_message(
            QueueUrl="https://sqs.eu-west-3.amazonaws.com/749868801319/preprocess-queue",
            MessageBody=json.dumps(msg_body)
        )
        
    def send_ocr_job(self,
                     bucket: str,
                     img_uri: str,
                     page_id: int):
        """
        """
        msg_body = {
            'bucket': bucket,
            'imgUri': img_uri,
            'pageId': page_id
        }
        self.send_message(
            QueueUrl="https://sqs.eu-west-3.amazonaws.com/749868801319/ocr-queue",
            MessageBody=json.dumps(msg_body)
        )

    def empty_preprocess(self):
        """
        """
        num_msgs = self.get_queue_attributes(
            QueueUrl="https://sqs.eu-west-3.amazonaws.com/749868801319/preprocess-queue",
            AttributeNames=['ApproximateNumberOfMessages']
        )['Attributes']['ApproximateNumberOfMessages']
        return int(num_msgs) == 0
        
    def empty_ocr(self):
        """
        """
        num_msgs = self.get_queue_attributes(
            QueueUrl="https://sqs.eu-west-3.amazonaws.com/749868801319/ocr-queue",
            AttributeNames=['ApproximateNumberOfMessages']
        )['Attributes']['ApproximateNumberOfMessages']
        return int(num_msgs) == 0
    
    def send_rds_query(self,
                       query: str):
        """
        """
        msg_body = query
        self.send_message(
            QueueUrl="https://sqs.eu-west-3.amazonaws.com/749868801319/rds-queries-queue.fifo",
            MessageBody=msg_body,
            MessageGroupId="1"
        )
        