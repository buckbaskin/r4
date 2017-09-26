import boto3

from r4.client import AbstractProvider, AbstractRegion
from r4.logging import logger

class S3(AbstractProvider):
    def __init__(self, region):
        if isinstance(region, S3.Region):
            self.region = region
            self.s3 = boto3.resource('s3', region_name=region.region_id)
            self.s3_client = boto3.client('s3', region_name=region.region_id)

    class Region(AbstractRegion):
        def validate_region_id(self, region_id):
            return region_id in {
                'ap-northeast-1',
                'ap-northeast-2',
                'ap-south-1',
                'ap-southeast-1',
                'ap-southeast-2',
                'ca-central-1',
                'eu-central-1',
                'eu-east-1',
                'eu-west-1',
                'eu-west-2',
                'sa-east-1',
                'us-east-1',
                'us-east-2',
                'us-west-1',
                'us-west-2',
            }

    def list(self):
        for bucket in self.s3_client.list_buckets()['Buckets']:
            yield bucket

    def create(self, bucket_name):
        try:
            if self.region.region_id == 'us-east-1':
                self.s3.Bucket(bucket_name).create()
            else:
                self.s3.Bucket(bucket_name).create(
                    CreateBucketConfiguration = {
                        'LocationConstraint': self.region.region_id,
                    })
            return True
        except botocore.exceptions.ClientError as e:
            if '%s' % (type(e),) == 'botocore.errorfactory.BucketAlreadyOwnedByYou':
                print('bucket %s already exists' % (bucket_name,))
            raise
            return False


    def delete(self, bucket_name):
        # All objects (including all object versions and Delete Markers) in the 
        #  bucket must be deleted before the bucket itself can be deleted.
        # print('begin delete %s' % (bucket_name,))
        self.s3.Bucket(bucket_name).objects.all().delete()
        self.s3.Bucket(bucket_name).delete()
        # print('end delete %s' % (bucket_name,))

    def delete_all(self):
        for bucket in self.list():
            self.delete(bucket['Name'])

    def upload(self, bucket_name, file_key, file_obj):
        self.s3.Bucket(bucket_name).upload_fileobj(Fileobj=file_obj, Key=file_key)

    def download(self, bucket_name, file_key, file_obj):
        self.s3.Bucket(bucket_name).download_fileobj(Key=file_key, Fileobj=file_obj)

