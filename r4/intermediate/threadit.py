import requests

from multiprocessing.pool import ThreadPool

# Magic number 5!
pool = ThreadPool(5)

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
services = config['services']
options = config['options']

def sufficiently_advanced_technology(method, requestUri, data):
    method = method.lower()
    def mapped_f(endpoint):
        return getattr(requests, method)(endpoint + requestUri, data=data),
        
    asyncr = pool.map_async(mapped_f, (service_dict['endpoint'] for service_dict in services))

    # return the fastest result
    for result in asyncr.get(None):
        return result[0].content
 
# example
def can_u_threadit():
    return sufficiently_advanced_technology('GET', '/get', None)

if __name__ == '__main__':
    print(can_u_threadit())

