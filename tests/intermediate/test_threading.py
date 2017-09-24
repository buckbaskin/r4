import r4
from r4.intermediate.threadit import sufficiently_advanced_technology
import requests_mock

with requests_mock.mock() as m:
    binGetContent = b'{\n  "args": {}, \n  "headers": {\n    "Accept": "*/*", \n    "Accept-Encoding": "gzip, deflate", \n    "Connection": "close", \n    "Host": "httpbin.org", \n    "User-Agent": "python-requests/2.18.4"\n  }, \n  "origin": "35.0.24.80", \n  "url": "https://httpbin.org/get"\n}\n'
    m.get('https://httpbin.com/get', content=binGetContent)

    def test_threading1():
        assert sufficiently_advanced_technology('GET', '/get', None) == binGetContent
