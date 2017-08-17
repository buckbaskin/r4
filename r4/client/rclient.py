import boto3

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

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

def s3_bucket_list():
    for bucket in s3_client.list_buckets()['Buckets']:
        yield bucket

def s3_bucket_create(bucket_name, region):
    s3.Bucket(bucket_name).create(
        CreateBucketConfiguration = {
            'LocationConstraint': region,
        })

def s3_bucket_delete(bucket_name):
    # TODO delete everything in the bucket first:
    # All objects (including all object versions and Delete Markers) in the 
    #  bucket must be deleted before the bucket itself can be deleted.
    s3.Bucket(bucket_name).delete()

def s3_delete_all_buckets():
    for bucket in s3_bucket_list():
        s3_bucket_delete(bucket['Name'])

def s3_bucket_upload(bucket_name, file_key, file_obj):
    s3.Bucket(bucket_name).upload_fileobj(Fileobj=file_obj, Key=file_key)

def s3_bucket_download(bucket_name, file_key, file_obj):
    s3.Bucket(bucket_name).download_fileobj(Key=file_key, Fileobj=file_obj)

for bucket in s3_bucket_list():
    print('Bucket %s' % bucket['Name'])
    bucket_found = True

if not bucket_found:
    print('No buckets found')

upload_this = FileObj('Hello AWS World'.encode('utf-8'), 'upload_this')
key = 'test_file'
bucket_name = 'io.r4.username'

s3_bucket_upload(bucket_name, key, upload_this)

print('uploaded file %s to bucket %s' % (key, bucket_name))

download_here = FileObj(None, 'download_here')

s3_bucket_download(bucket_name, key, download_here)

print('downloaded file %s from bucket %s\n%s' % (key, bucket_name, download_here.data))

# s3_delete_all_buckets()