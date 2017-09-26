import r4
from r4.intermediate.threadit import sufficiently_advanced_technology

# import mock
# import pytest
import requests
from pytest_mock import mocker

binGetContent1 = b'{\n  "args": {}, \n  "headers": {\n    "Accept": "*/*", \n    "Accept-Encoding": "gzip, deflate", \n    "Connection": "close", \n    "Host": "httpbin.org", \n    "User-Agent": "python-requests/2.18.4"\n  }, \n  "origin": "129.22.124.131", \n  "url": "https://httpbin.org/get"\n}\n'


def test_threading1(mocker):
    url = "https://httpbin.org/get"
    mocker.patch.object(requests, 'get')
    r = requests.Response()
    r._content = binGetContent1
    r.url = url
    requests.get.return_value = r
    # requests.method_under_test()
    assert sufficiently_advanced_technology('GET', '/get', None) == binGetContent1
    requests.get.assert_called_with(url, data=None)
