from r4.client import Client
from r4.client.s3 import S3

if __name__ == '__main__':

    client = Client(regions=[
        S3.Region('us-east-1'),
        S3.Region('us-east-2'),
        S3.Region('us-west-1'),
        S3.Region('us-west-2'),
        ])
    
    bucket_name = 'io.r4.username03'

    # print('Client.create("%s")' % (bucket_name,))
    # client.create(bucket_name)

    # for bucket in client.list():
    #     print('Bucket? %s' % bucket['Name'])

    upload_this = 'Hello AWS World. 4 Threads!'.encode('utf-8')
    key = 'test_file'

    client.upload(bucket_name, key, upload_this, fractional_upload=1)
    print('uploaded file %s to bucket %s' % (key, bucket_name))

    data = client.download(bucket_name, key, fractional_download=1)
    print('downloaded file %s from bucket %s\n%s' % (key, bucket_name, data))

    # client.delete_all_buckets()
