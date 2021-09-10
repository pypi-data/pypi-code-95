# Here there be a package
from waterbear.service.cloudfront import cloudfront

import os

def lambda_handler(event, context):
    cloudfront.respond_to_message(event, context)
