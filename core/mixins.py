from rest_framework import serializers


class SignedFileFieldMixin:

    file = serializers.SerializerMethodField()

    def get_file(self, instance):
        # Get signed url from boto
        if instance.file:
            return instance.file.url(expire=3600)
        return None
