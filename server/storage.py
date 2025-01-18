from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class LocalStackS3Storage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):

        if settings.DEBUG:
            # LocalStack endpoint
            kwargs['endpoint_url'] = settings.AWS_S3_ENDPOINT_URL

        super().__init__(*args, **kwargs)
