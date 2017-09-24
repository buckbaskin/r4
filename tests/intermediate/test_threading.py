import requests_mock

with requests_mock.mock() as m:
    m.get('https://httpbin.com/get', text=b'{\n  "args": {}, \n  "headers": {\n    "Accept": "*/*", \n    "Accept-Encoding": "gzip, deflate", \n    "Connection": "close", \n    "Host": "httpbin.org", \n    "User-Agent": "python-requests/2.18.4"\n  }, \n  "origin": "35.0.24.80", \n  "url": "https://httpbin.org/get"\n}\n')

    def test_threading1():
        return False
