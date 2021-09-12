import boto3
from rest_framework.serializers import ValidationError
import json
from .normalize import map_to_slug_keys
from rest_framework import status


class AbstractLambdaClient:

    LIST_SUPPORTED_TRIGGERS = "supported_triggers"

    def __init__(self, region, function_name, has_local=False, has_qa=False):
        from django.conf import settings

        self.function_name = function_name
        self.client = boto3.client(
            'lambda',
            region_name=region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        self.has_local = has_local
        self.has_qa = has_qa

        if hasattr(self, 'valid_triggers'):
            self.valid_triggers.append(self.LIST_SUPPORTED_TRIGGERS)
        else:
            self.valid_triggers = [self.LIST_SUPPORTED_TRIGGERS]

    def invoke(self, trigger, body={}, return_slug_values=True):
        from django.conf import settings

        if trigger not in self.valid_triggers:
            raise ValidationError({
                "trigger_source": [
                    'Trigger {0} not supported, supported triggers: {1}'.format(
                        trigger, ", ".join(self.valid_triggers))
                ]
            }
            )

        function_name = self.function_name
        if not settings.IS_PRODUCTION:
            if settings.IS_QA and self.has_qa:
                function_name = f"{function_name}QA"
            elif not settings.IS_DEVELOPMENT and not settings.IS_QA and self.has_local:
                function_name = f"{function_name}Local"
            else:
                function_name = f"{function_name}Dev"

        body['triggerSource'] = trigger

        response = self.client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            LogType='None',
            Payload=json.dumps(body).encode('utf-8')
        )

        response_payload = json.loads(
            response['Payload'].read().decode("utf-8"))

        if 'statusCode' in response_payload:
            status_code = response_payload['statusCode']
            if return_slug_values:
                response_payload = map_to_slug_keys(response_payload)

            if status.is_success(status_code):
                return response_payload
            elif status.is_client_error(status_code):
                raise ValidationError(response_payload['body'])
            else:
                if 'detail' in response_payload['body']:
                    raise Exception(response_payload['body']['detail'])
                else:
                    raise Exception("Lambda function error occurred")
        elif 'errorMessage' in response_payload:
            raise Exception(response_payload['errorMessage'])
        else:
            raise Exception("Unknown lambda response")

    class Meta:
        abstract = True
