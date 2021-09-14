from pydantic import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = 'dev'

    AWS_REGION: str = 'ap-southeast-1'
    AWS_SNS_KEY: str = None
    AWS_SNS_SECRET: str = None
    AWS_SNS_PATH: str = 'arn:aws:sns:ap-southeast-1:580482583062:'

    class Config:
        case_sensitive = True

        fields = {
            'ENVIRONMENT': {'env': 'ENVIRONMENT'},

            'AWS_REGION': {'env': 'AWS_REGION'},
            'AWS_SNS_KEY': {'env': 'AWS_SNS_KEY'},
            'AWS_SNS_SECRET': {'env': 'AWS_SNS_SECRET'},
            'AWS_SNS_PATH': {'env': 'AWS_SNS_PATH'},
        }


settings = Settings()
