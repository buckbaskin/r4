import requests
import boto3
import multithreading

reqf = {
    'get': requests.get,
    'post': requests.post,
    'put': requests.put,
    'delete': requests.delete,
    'head': requests.head,
    'options': requests.options,
}

config = {
    'services': [
        {
            'name': 'S3 US East 1',
            'endpoint': 's3.aws.com', # not real value currently
        }
    ],
    'options': {
         # choose all or first 
         'style': 'all' # choose either all or first
    }
}

def sufficiently_advanced_technology(method, requestUri, data):
    r = {}
    for service_dict in services:
        endpoint = service_dict['endpoint']
        # call the same method that was called
        r[service_dict['endpoint']] = reqf[method](endpoint + requestUri, data=data)
    
    for service_dict in services:
        endpoint = service_dict['endpoint']
        try:
            return r[endpoint].contents
        except NameError:
            continue

    return None
    
