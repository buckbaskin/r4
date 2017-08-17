import boto3
import botocore

class FileObj(object):
    def __init__(self, data=None, id_=None):
        if isinstance(data, bytes):
            self.data = data
        else:
            self.data = ''.encode('utf-8')
        self.id_ = id_
        self.index = 0

    def read(self, size=None, *args, **kwargs):
        # returns bytes, reads the data
        if size is None:
            size = len(self.data)
        size = int(size)
        print('read %s from %s' % (self.data, self.id_,))
        print('with size %d and args %s and kwargs %s' % (size, args, kwargs,))
        if self.index + size >= len(self.data):
            old_index = self.index + 0
            self.index = len(self.data)
            return self.data[old_index:]
        else:
            old_index = self.index + 0
            self.index += size
            return self.data[old_index:self.index]

    def write(self, bytes_, *args, **kwargs):
        print('write %s to %s' % (bytes_, self.id_,))
        self.data = bytes_

class S3(object):
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.s3_client = boto3.client('s3')

    class Region(object):
        def __init__(self, region_id):
            self.region_id = region_id

    def bucket_list(self):
        for bucket in self.s3_client.list_buckets()['Buckets']:
            yield bucket

    def bucket_create(self, bucket_name, region):
        try:
            self.s3.Bucket(bucket_name).create(
                CreateBucketConfiguration = {
                    'LocationConstraint': region.region_id,
                })
        except botocore.exceptions.ClientError:
            return None


    def bucket_delete(self, bucket_name):
        # All objects (including all object versions and Delete Markers) in the 
        #  bucket must be deleted before the bucket itself can be deleted.
        print('begin delete %s' % (bucket_name,))
        self.s3.Bucket(bucket_name).objects.all().delete()
        self.s3.Bucket(bucket_name).delete()
        print('end delete %s' % (bucket_name,))

    def delete_all_buckets(self, ):
        for bucket in self.bucket_list():
            self.bucket_delete(bucket['Name'])

    def bucket_upload(self, bucket_name, file_key, file_obj):
        self.s3.Bucket(bucket_name).upload_fileobj(Fileobj=file_obj, Key=file_key)

    def bucket_download(self, bucket_name, file_key, file_obj):
        self.s3.Bucket(bucket_name).download_fileobj(Key=file_key, Fileobj=file_obj)


if __name__ == '__main__':
    s3 = S3()
    bucket_found = False
    for bucket in s3.bucket_list():
        print('Bucket %s' % bucket['Name'])
        bucket_found = True

    if not bucket_found:
        print('No buckets found')

    upload_this = FileObj('Hello AWS World again'.encode('utf-8'), 'upload_this')
    key = 'test_file'
    bucket_name = 'io.r4.username03'

    s3.bucket_create(bucket_name, S3.Region('us-east-2'))

    s3.bucket_upload(bucket_name, key, upload_this)

    print('uploaded file %s to bucket %s' % (key, bucket_name))

    download_here = FileObj(None, 'download_here')

    s3.bucket_download(bucket_name, key, download_here)

    print('downloaded file %s from bucket %s\n%s' % (key, bucket_name, download_here.data))

    # s3.delete_all_buckets()
