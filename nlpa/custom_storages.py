from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import json
from pprint import pprint
from urllib.parse import quote_plus, urlencode, unquote

def encoded_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.items():
        #print(v)
        out_dict[k] = quote_plus(v,safe='').replace('%','/')
        #print(unquote(out_dict[k].replace('/','%')))
    return out_dict

class CustomS3Boto3Storage(S3Boto3Storage):
    file_overwrite = False

    def get_object_parameters(self, name):
        s3_object_params = {
            "ACL": "public-read",
            "Tagging": urlencode(encoded_dict(self.custom[self.original_filename])),
        }
        return {**s3_object_params, **self.object_parameters.copy()}

    def generate_filename(self, filename):
        """
        Validate the filename by calling get_valid_name() and return a filename
        to be passed to the save() method.
        """
        # `filename` may include a path as returned by FileField.upload_to.
        self.original_filename = filename.split('/',1)[1]
        return super().generate_filename(filename)


def create_custom_storage(myvar):
    storage = CustomS3Boto3Storage
    storage.custom_variable = myvar
    return storage
