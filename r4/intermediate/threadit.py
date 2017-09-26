import airbrake
import logging
import requests

from multiprocessing.pool import ThreadPool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
airbrake_logger = airbrake.getLogger(api_key="1001b69b71a13ef204b4a8ac1e38d9ad", project_id=157356)
logger.exception = airbrake_logger.exception

# logger.exception("Bad math.")

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
            'endpoint': 'https://httpbin.org'
        }
    ],
    'options': {
         # choose all or first 
         'style': 'all' # choose either all or first
    }
}
services = config['services']
options = config['options']

def sufficiently_advanced_technology(method: str, requestUri: str, data: str) -> bytes:
    method = method.lower()
    def mapped_f(endpoint: str) -> requests.models.Response:
        return getattr(requests, method)(endpoint + requestUri, data=data)
        
    asyncr = pool.map_async(mapped_f, (service_dict['endpoint'] for service_dict in services))

    # return the fastest result
    for result in asyncr.get(None):
        return result.content
    return None
 
# example
def can_u_threadit() -> None:
    print(sufficiently_advanced_technology('GET', '/get', None))

if __name__ == '__main__':
    can_u_threadit()

