import os
import boto3

bucket_name = 'nlpa-website-bucket'
keyprefix = 'entries'
s3_client = boto3.client('s3')

objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='%s/'%keyprefix)
for o in objects['Contents'][1:]:
    key = o['Key']
    tags_response = s3_client.get_object_tagging(Bucket=bucket_name,Key=key)
    tagset = tags_response['TagSet']
    tagdict = {}
    for tag in tagset:
        tagdict[tag['Key']] = tag['Value']
    filename = tagdict['filename']
    email = tagdict['user_email']
    category = tagdict['category']
    youth = tagdict['is_young_entrant'] == 'True'
    os.makedirs('%s/%s'%(email,category))
    s3_client.download_file(bucket_name,key,'%s/%s/%s'%(email,category,filename))
