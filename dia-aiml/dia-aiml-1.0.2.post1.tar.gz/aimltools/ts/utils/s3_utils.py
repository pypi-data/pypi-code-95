import boto3
import time
import pandas as pd
import requests
import io

from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)


class Boto3ClientException(Exception):
    """Exception raised for errors in the input to Boto3ClientFactory methods.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class Boto3ClientFactory:
    """
    Create boto S3 client, possibly using Lilly's API gateway that provides temporary credentials
    Full documentation to be written
    """
    __service_account = ""
    __aws_account_id = ""
    __gw_s3_access_role = ""
    __cert_path = ""
    __cert_key_path = ""
    __gw_url = ""
    __proxy_dict = {}
    __role_arn = ""
    
    def set_service_account(self, service_account):
        self.__service_account = service_account
        return self
    
    def set_aws_account_id(self, aws_account_id):
         self.__aws_account_id = aws_account_id
         return self
        
    def set_aws_access_role(self, gw_s3_access_role):
        self.__gw_s3_access_role = gw_s3_access_role
        return self
        
    def set_certificate_path(self, cert_path):
        self.__cert_path = cert_path
        return self
    
    def set_certificate_key_path(self, cert_key_path):
        self.__cert_key_path = cert_key_path
        return self
    
    def set_gw_url(self, gw_url):
        self.__gw_url = gw_url
        return self
        
    def set_proxies(self, http_proxy, https_proxy, ftp_proxy):
        self.__proxy_dict = { 
              "http"  : http_proxy, 
              "https" : https_proxy, 
              "ftp"   : ftp_proxy
            }
        return self
    
    def _validate(self):
        if self.__service_account == "":
            raise Boto3ClientException("service_account", "PLEASE PROVIDE A VALID AWS SERVICE ACCOUNT")
        
        if self.__aws_account_id == "":
            raise Boto3GwBoto3ClientExceptionClientException("aws_account_id", "PLEASE PROVIDE A VALID AWS ACCOUNT ID")
        
        if self.__gw_s3_access_role == "":
            raise Boto3ClientException("gw_s3_access_role", "PLEASE PROVIDE A VALID AWS GATEWAY ACCESS ROLE")
            
        if self.__cert_path == "":
            raise Boto3ClientException("cert_path", "PLEASE PROVIDE A VALID CERTIFICATE PATH")
        
        if self.__cert_key_path == "":
            raise Boto3ClientException("cert_key_path", "PLEASE PROVIDE A VALID CERTIFICATE KEY PATH")
        
        if self.__gw_url == "":
            raise Boto3ClientException("gw_url", "PLEASE PROVIDE A VALID GATEWAY URL")
        
    def create_using_gw(self, service_account_pwd, client_type='s3', **kwargs):
        self._validate()
        self.__role_arn = 'arn:aws:sts::' + self.__aws_account_id + ':assumed-role/' + self.__gw_s3_access_role + '/' + self.__service_account
        
        authorization=HTTPBasicAuth(self.__service_account,service_account_pwd)
        cert = (self.__cert_path, self.__cert_key_path)
        headers = {'USER': 'application/json','content-type': 'application/json'}
        try:
            temporary_credentials_response=requests.get(self.__gw_url, headers=headers, auth=authorization, cert=cert, proxies=self.__proxy_dict)
            for line in temporary_credentials_response.iter_lines():
                logger.debug('>>>Temp credentials: {}'.format(line))
                if line:
                    decoded_line = line.decode('utf-8')
                    resjson = temporary_credentials_response.json()
                    temporary_credentials = temporary_credentials_response.json()
                    credentials = temporary_credentials
            for key, value in credentials.items():
                try:
                    assume_role_with_saml_result = credentials[key]['AssumeRoleWithSAMLResponse']['AssumeRoleWithSAMLResult']
                    if assume_role_with_saml_result['AssumedRoleUser']['Arn']==self.__role_arn:
                        credentials_field = assume_role_with_saml_result['Credentials']
                        session_token = credentials_field['SessionToken']
                        aws_access_key = credentials_field['AccessKeyId']
                        aws_secret_access_key = credentials_field['SecretAccessKey']
                except KeyError:
                    pass  # we only want assumerolewithsamlresponse
            credentials_field = assume_role_with_saml_result['Credentials']
            session_token = credentials_field['SessionToken']
            aws_access_key = credentials_field['AccessKeyId']
            aws_secret_access_key = credentials_field['SecretAccessKey']
            logger.debug("SessionToken {}\nAccessKeyId {}\nSecretAccessKey {}".format(session_token, aws_access_key, aws_secret_access_key))
            s3 = boto3.client(client_type, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key, aws_session_token=session_token, **kwargs)
        except KeyError:
            logger.error("Error Found: " + KeyError)
        return s3

    def create(self, aws_id = "", aws_secret = "", client_type='s3', **kwargs):
        if len(aws_id) > 0:
            s3 = boto3.client(client_type, aws_access_key_id=aws_id, aws_secret_access_key=aws_secret, **kwargs)
        else:
            s3 = boto3.client(client_type, **kwargs)
        return s3

    
class S3SelectHelper():
    def __init__(self, s3_boto_client):
        self.__s3 = s3_boto_client
        self.set_quote_character()
        self.set_separator()
    
    def set_quote_character(self, quote_character = "'"):
        self.__quote_character = quote_character
    
    def set_separator(self, separator = ","):
        self.__separator = separator
        
    def s3_select_to_df(self, bucket, key, expression, headers):
        logger.info('Quote delimiter set to: [{}]'.format(self.__quote_character))
        start = time.time()
        r, cnt = self.__execute_s3_select(bucket, key, expression)
        end = time.time()
        logger.info('Read {0} rows in {1:.2f} seconds'.format(str(cnt), end - start))
        r = headers + "\n" + r
        return pd.read_csv(io.StringIO(r), sep=self.__separator)
    
    def __execute_s3_select(self, bucket, key, expression):
        compression_type = S3SelectHelper.infer_compression_by_filename(key)
        logger.info("Compression: {}".format(compression_type))
        r = self.__s3.select_object_content(
                Bucket=bucket,
                Key=key,
                ExpressionType='SQL',
                Expression=expression,
                InputSerialization = {'CSV': {"FileHeaderInfo": "Use", "AllowQuotedRecordDelimiter": True, "QuoteCharacter": self.__quote_character}, 'CompressionType': compression_type},
                OutputSerialization = {'CSV': {}},
        )
        event_stream = r['Payload']
        end_event_received = False
        records = ""
        logger.info("Appending rows...")
        cnt = 0
        for event in event_stream:
            cnt = cnt + 1
            if 'Records' in event:
                if cnt%1000 == 0:
                    logger.info("...read 1000 blocks...{}".format(cnt))

                records = records + event['Records']['Payload'].decode('utf-8')

            if 'End' in event:
                end_event_received = True

        if not end_event_received:
            raise Exception("End event not received, request incomplete.")

        return records.rstrip(), records.count("\n")
    
    @staticmethod
    def infer_compression_by_filename(filename):
        compression_type = 'NONE'
        if filename.endswith('.gz'):
            compression_type = 'GZIP'
        return compression_type