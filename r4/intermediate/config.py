# from r4.intermediate.threadit import sufficiently_advanced_technology as sat
import boto3
import botocore
import hashlib
import json


r4_IP_address = '127.0.0.1'

session = boto3.session.Session()

s3_client = boto3.client(
    's3'
)

def sanitize_username(username):
    h = hashlib.new('sha512')
    h.update(username.encode('utf-8'))
    return h.hexdigest()

def store_config(username, config):
    bucket_name = 'io.r4.config'
    try:
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
    except botocore.exceptions.ClientError:
        pass
    s3_client.put_object(Body=json.dumps(config).encode('utf-8'), Bucket=bucket_name, Key=sanitize_username(username))

def read_config(username):
    bucket_name = 'io.r4.config'
    obj = s3_client.get_object(Bucket=bucket_name, Key=sanitize_username(username))
    config = json.loads(obj['Body'].read().decode('utf-8'))
    return config

if __name__ == '__main__':
    config = {'hello': 'world', 'actual': 'data'}
    username = 'johndoe'
    store_config(username, config)
    loaded_config = read_config(username)
    print('old config', config)
    print('new config', loaded_config)
    
