from __future__ import unicode_literals

import base64
import hmac
import json
import time
import uuid

import logging
try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    # Don't error out if boto3 isn't available. This is only required
    # when the 'private' flag is True.
    pass

try:
    from urllib.parse import quote, quote_plus
except ImportError:
    # python 2
    from urllib import quote, quote_plus

from datetime import datetime
from hashlib import sha1

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django.utils.encoding import smart_bytes


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
    amz_headers = "x-amz-acl:public-read"

    # The private flag specifies whether we need to return a signed
    # GET url when the upload succeeds.
    private = False

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

    def get_amz_headers(self):
        return self.amz_headers

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
        s3_client = boto3.client(
            's3',
            aws_access_key_id=self.get_aws_access_key(),
            aws_secret_access_key=self.get_aws_secret_key()
        )

        try:
            response = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name,
                        'Key': object_name},
                ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None

        # The response contains the presigned URL
        return response

    def get(self, request):
        AWS_ACCESS_KEY = self.get_aws_access_key()
        AWS_SECRET_KEY = self.get_aws_secret_key()
        S3_BUCKET = self.get_bucket()
        mime_type = self.get_mimetype(request)
        object_name = self.get_object_name(request)

        expires = int(self.now_time() + self.get_expiration_time())

        if self.get_amz_headers():
            put_request = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (
                mime_type, expires, self.get_amz_headers(),
                S3_BUCKET, object_name)
        else:
            put_request = "PUT\n\n%s\n%d\n/%s/%s" % (
                mime_type, expires, S3_BUCKET, object_name)

        # Calculate the signature for a PUT request.
        signature = base64.encodebytes(
            hmac.new(
                smart_bytes(AWS_SECRET_KEY),
                put_request.encode('utf-8'),
                sha1
            ).digest())
        signature = quote_plus(signature.strip())

        # Encode the plus symbols
        # https://pmt.ccnmtl.columbia.edu/item/95796/
        signature = quote(signature)

        url = 'https://{}.s3.amazonaws.com/{}'.format(
            S3_BUCKET, object_name)
        signed_request = \
            '{}?AWSAccessKeyId={}&Expires={:d}&Signature={}'.format(
                url, AWS_ACCESS_KEY, expires, signature)

        data = {
            'signed_request': signed_request,
            'url': url
        }

        if self.private:
            data['signed_get_url'] = quote(
                self.create_presigned_url(
                    S3_BUCKET, object_name, self.get_expiration_time()))

        return HttpResponse(
            json.dumps(data), content_type='application/json')
