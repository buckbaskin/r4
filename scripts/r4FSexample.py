import logging

from r4.client import Client
from r4.client.r4 import FileSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print = logger.info

if __name__ == '__main__':

    client = Client(regions=[
        FileSystem.Region('temp'),
        ])
    
    bucket_name = 'helloWorld'

    print('Client.create("%s")' % (bucket_name,))
    client.create(bucket_name)

    print('done creating bucket')

    for bucket in client.list():
        print('Bucket? %s' % bucket['Name'])

    print('done listing buckets')

    upload_this = 'Hello AWS World. 4 Threads!'.encode('utf-8')
    key = 'test_file'

    client.upload(bucket_name, key, upload_this, fractional_upload=1)
    print('uploaded file %s to bucket %s' % (key, bucket_name))

    data = client.download(bucket_name, key, fractional_download=1)
    print('downloaded file %s from bucket %s\n%s' % (key, bucket_name, data))

    # client.delete_all_buckets()
