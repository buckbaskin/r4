import boto3
import requests
import multiprocessing
import threading
from multiprocessing.pool import ThreadPool

pool = ThreadPool(5)

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
        # {
        #     'name': 'S3 US East 1',
        #     'endpoint': 's3.aws.com', # not real value currently
        # }
        {
            'name': 'HTTP Bin',
            'endpoint': 'https://httpbin.org/'
        }
    ],
    'options': {
         # choose all or first 
         'style': 'all' # choose either all or first
    }
}

def sufficiently_advanced_technology(method, requestUri, data):
    method = method.lower()
    services = config['services']
    r = {}
    targets = []
    def mapped_f(endpoint):
        r[endpoint] = reqf[method](endpoint + requestUri, data=data),
        
    for service_dict in services:
        endpoint = service_dict['endpoint']
        targets.append(endpoint)

    pool.map(mapped_f, targets)
    
    for service_dict in services:
        endpoint = service_dict['endpoint']
        try:
            return r[endpoint][0].content
        except NameError:
            continue

    return None
    
def can_u_threadit():
    return sufficiently_advanced_technology('GET', '/get', None)

if __name__ == '__main__':
    print(can_u_threadit())

