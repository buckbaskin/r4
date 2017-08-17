import boto3

s3 = boto3.client('s3')

# s3.create_bucket(Bucket='io.r4.username')

bucket_found = False
for bucket in s3.list_buckets()['Buckets']:
    print('Bucket %s' % bucket['Name'])
    bucket_found = True

if not bucket_found:
    print('No buckets found')
