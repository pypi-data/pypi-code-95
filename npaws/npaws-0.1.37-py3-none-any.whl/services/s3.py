import json
import os
from ..client import Boto3Client


class S3Client(Boto3Client):
    """
    """
    
    def __init__(self):
        """
        """
        super().__init__('s3')
        
    def upload_model(self,
                     bucket: str,
                     project_name: str,
                     version_id: int,
                     model_name: str,
                     filepath: str,
                     filename: str = 'model.h5'):
        """
        """
        file_path = f"{project_name}/versions/{version_id}/models/{model_name}/{filename}"
        self.upload_file(filepath, Bucket=bucket, Key=file_path)
        
    def download_model(self,
                       bucket: str,
                       project_name: str,
                       version_id: int,
                       model_name: str,
                       filename: str = 'model.h5') -> str:
        """
        """
        file_path = f"{project_name}/versions/{version_id}/models/{model_name}/{filename}"
        self.download_file(bucket, file_path, filename)
        return filename
    
    def upload_model_parameters(self,
                                bucket: str,
                                project_name: str,
                                version_id: int,
                                model_name: str,
                                parameters: dict = {}):
        """
        """
        file_path = f"{project_name}/versions/{version_id}/models/{model_name}/parameters.json"
        self.put_object(Body=json.dumps(parameters).encode(), Bucket=bucket, Key=file_path)
        
    def get_model_parameters(self,
                             bucket: str,
                             project_name: str,
                             version_id: int,
                             model_name: str) -> dict:
        """
        """
        file_path = f"{project_name}/versions/{version_id}/models/{model_name}/parameters.json"
        self.download_file(bucket, file_path, 'tmp.json')
        parameters = json.load(open('tmp.json', 'r'))
        os.remove('tmp.json')
        return parameters
    
    def upload_model_evaluation(self,
                                bucket: str,
                                project_name: int,
                                version_id: int,
                                model_name: str,
                                evaluation: dict):
        """
        """
        file_path = f"{project_name}/versions/{version_id}/models/{model_name}/evaluation/evaluation.json"
        self.put_object(Body=json.dumps(evaluation).encode(), Bucket=bucket, Key=file_path)
    
    def get_model_evaluation(self,
                             bucket: str,
                             project_name: int,
                             version_id: int,
                             model_name: str):
        """
        """
        file_path = f"{project_name}/versions/{version_id}/models/{model_name}/evaluation/evaluation.json"
        self.download_file(bucket, file_path, 'tmp.json')
        evaluation = json.load(open('tmp.json', 'r'))
        os.remove('tmp.json')
        return evaluation
        
    def get_vocab(self,
                  bucket: str,
                  project_name: str) -> dict:
        """
        """
        vocab = self.get_object(Bucket=bucket, Key=f"{project_name}/config/vocab.json")
        return json.loads(vocab['Body'].read())
    
    def upload_vocab(self,
                     bucket: str,
                     project_name: str,
                     vocab: dict):
        """
        """
        self.put_object(Body=json.dumps(vocab).encode(), Bucket=bucket, Key=f"{project_name}/config/vocab.json")
            
    def get_word2idx(self,
                     bucket: str,
                     project_name: str) -> dict:
        """
        """
        vocab = self.get_object(Bucket=bucket, Key=f"{project_name}/config/word2idx.json")
        return json.loads(vocab['Body'].read())
    
    def upload_word2idx(self,
                        bucket: str,
                        project_name: str,
                        word2idx: dict):
        """
        """
        self.put_object(Body=json.dumps(word2idx).encode(), Bucket=bucket, Key=f"{project_name}/config/word2idx.json")

    def get_version_classes(self,
                            bucket: str,
                            project_name: str,
                            version_id: int) -> dict:
        """
        """
        classes = self.get_object(Bucket=bucket, Key=f"{project_name}/versions/{version_id}/datasets/classes.json")
        return json.loads(classes['Body'].read())
    
    def upload_version_classes(self,
                               bucket: str,
                               project_name: str,
                               version_id: int,
                               classes: list):
        """
        """
        self.put_object(Body=json.dumps(classes).encode(), Bucket=bucket, Key=f"{project_name}/versions/{version_id}/datasets/classes.json")

    def create_account_bucket(self,
                              name: str,
                              region: str = 'eu-west-3') -> str:
        """
        """
        bucket_name = f'np-{name}-bucket'
        location = {'LocationConstraint': region}
        self.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        return bucket_name

