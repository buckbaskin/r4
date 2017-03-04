from r4.client import R4

bucket = R4(username='buck', secret='oldman', bucket_name='bucket')

status = bucket.create(open('simple_client.py'))

print('uploaded id: %s' % (status.r4id,))

get_file = bucket.read(status.r4id)

print('got file: %s' % (get_file,))
