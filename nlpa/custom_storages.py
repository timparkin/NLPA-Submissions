from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import json
from urllib.parse import urlencode

def encoded_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.items():
        if isinstance(v, str):
            v = v.encode('utf8')
        elif isinstance(v, bytes):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict

class CustomS3Boto3Storage(S3Boto3Storage):
    file_overwrite = False

    def get_object_parameters(self, name):



        s3_object_params = {
            "ACL": "public-read",
            "Tagging": urlencode(encoded_dict(self.custom)),


        }
        return {**s3_object_params, **self.object_parameters.copy()}


def create_custom_storage(myvar):
    storage = CustomS3Boto3Storage
    storage.custom_variable = myvar
    return storage
