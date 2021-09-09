from __future__ import unicode_literals

import json
import time
import uuid

import logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View


s3_config = Config(
    signature_version='s3v4',
    s3={'addressing_style': 'path'},
)


class SignS3View(View):
    name_field = 's3_object_name'
    type_field = 's3_object_type'
    expiration_time = 10
    mime_type_extensions = [
        ('jpeg', '.jpg'),
        ('png', '.png'),
        ('gif', '.gif'),
        ('pdf', '.pdf'),
        ('svg', '.svg'),
        ('webp', '.webp'),
    ]
    default_extension = '.obj'
    root = ''
    path_string = (
        "{root}{now.year:04d}/{now.month:02d}/"
        "{now.day:02d}/{basename}{extension}")
    acl = 'public-read'

    # The private flag specifies whether we need to return a signed
    # GET url when the upload succeeds.
    private = False

    def dispatch(self, request, *args, **kwargs):
        self.s3_client = boto3.client(
            's3', config=s3_config,
            aws_access_key_id=self.get_aws_access_key(),
            aws_secret_access_key=self.get_aws_secret_key()
        )
        return super().dispatch(request, *args, **kwargs)

    def get_name_field(self):
        return self.name_field

    def get_type_field(self):
        return self.type_field

    def get_expiration_time(self):
        return self.expiration_time

    def get_mime_type_extensions(self):
        return self.mime_type_extensions

    def get_default_extension(self):
        return self.default_extension

    def get_root(self):
        return self.root

    def get_path_string(self):
        return self.path_string

    def get_aws_access_key(self):
        return settings.AWS_ACCESS_KEY

    def get_aws_secret_key(self):
        return settings.AWS_SECRET_KEY

    def get_bucket(self):
        return settings.AWS_UPLOAD_BUCKET

    def get_mimetype(self, request):
        return request.GET.get(self.get_type_field())

    def extension_from_mimetype(self, mime_type):
        for m, ext in self.get_mime_type_extensions():
            if m in mime_type:
                return ext
        return self.get_default_extension()

    def now(self):
        return datetime.now()

    def now_time(self):
        return time.time()

    def basename(self, request):
        return str(uuid.uuid4())

    def extension(self, request):
        return self.extension_from_mimetype(self.get_mimetype(request))

    def get_object_name(self, request):
        now = self.now()
        basename = self.basename(request)
        extension = self.extension(request)
        return self.get_path_string().format(
            now=now, basename=basename, extension=extension,
            root=self.get_root())

    def create_presigned_url(self, bucket_name, object_name,
                             expiration=3600):
        """Generate a presigned URL to share an S3 object

        From: https://boto3.amazonaws.com/v1/documentation/api/latest/
                                 guide/s3-presigned-urls.html

        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to
          remain valid
        :return: Presigned URL as string. If error, returns None.
        """

        # Generate a presigned URL for the S3 object
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name,
                        'Key': object_name},
                ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None

        # The response contains the presigned URL
        return response

    def create_presigned_url_expanded(
            self, client_method_name, method_parameters=None,
            expiration=3600, http_method=None):
        """Generate a presigned URL to invoke an S3.Client method

        Not all the client methods provided in the AWS Python SDK are
        supported.

        :param client_method_name: Name of the S3.Client method, e.g.,
        'list_buckets'

        :param method_parameters: Dictionary of parameters to send to
        the method

        :param expiration: Time in seconds for the presigned URL to
        remain valid

        :param http_method: HTTP method to use (GET, etc.)
        :return: Presigned URL as string. If error, returns None.
        """

        # Generate a presigned URL for the S3 client method

        try:
            response = self.s3_client.generate_presigned_url(
                ClientMethod=client_method_name,
                Params=method_parameters,
                ExpiresIn=expiration,
                HttpMethod=http_method)
        except ClientError as e:
            logging.error(e)
            return None

        # The response contains the presigned URL
        return response

    def get(self, request):
        S3_BUCKET = self.get_bucket()
        mime_type = self.get_mimetype(request)
        object_name = self.get_object_name(request)

        if not getattr(self, 's3_client', None):
            self.s3_client = boto3.client(
                's3', config=s3_config,
                aws_access_key_id=self.get_aws_access_key(),
                aws_secret_access_key=self.get_aws_secret_key()
            )

        url = 'https://{}.s3.amazonaws.com/{}'.format(
            S3_BUCKET, object_name)

        put_data = {
            'Bucket': S3_BUCKET,
            'ContentType': mime_type.replace(' ', '+'),
            'Key': object_name,
        }

        if self.acl:
            put_data['ACL'] = self.acl

        signed_request = self.create_presigned_url_expanded(
            'put_object', put_data, self.get_expiration_time(), 'PUT')

        data = {
            'signed_request': signed_request,
            'url': url,
        }

        if self.private:
            data['signed_get_url'] = self.create_presigned_url(
                S3_BUCKET, object_name, self.get_expiration_time())

        return HttpResponse(
            json.dumps(data), content_type='application/json')
