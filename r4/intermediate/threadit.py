import boto3
import requests
import multiprocessing
import threading
from multiprocessing.pool import ThreadPool

# Magic number 5!
pool = ThreadPool(5)

reqf = {
    'get': requests.get,
    'post': requests.post,
    'put': requests.put,
    'delete': requests.delete,
    'head': requests.head,
    'options': requests.options,
}

# Magic config
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
    def mapped_f(endpoint):
        r[endpoint] = reqf[method](endpoint + requestUri, data=data),
        return r[endpoint]
        
    asyncr = pool.map_async(mapped_f, (service_dict['endpoint'] for service_dict in services))

    for result in asyncr.get(None):
        return result[0].content

    return None
    
def can_u_threadit():
    return sufficiently_advanced_technology('GET', '/get', None)

if __name__ == '__main__':
    print(can_u_threadit())

