import time
import hashlib
import json
import requests

class R4(object):
    '''
    Class representing the generic R4 bucket
    '''
    read_string = 'https://{addr}/{username}/{bucket}/{r4id}'

    class Id(object):
        def __init__(self, sha3_hash):
            self.r4id = str(sha3_hash)

        @staticmethod
        def create(file_contents, time):
            # take the sha3 hash, and return the id
            hash_ = hashlib.sha512()
            hash_.update(file_contents)
            hash_.update(time)
            return R4.Id(hash_.hexdigest())

    class Status(object):
        def __init__(self, R4, r4id):
            self.R4 = R4
            self.r4id = r4id

        def status(self):
            bad_reasons = []
            for server_addr in FILE_SERVER_ADDRESS:
                res = requests.get(
                    (self.R4.read_string+'/status').format({
                        'addr': server_addr,
                        'username': self.R4.username,
                        'bucket': self.R4.bucket_name,
                        'r4id': self.r4id,
                        }))
                if res.ok():
                    return [res.reason]
                else:
                    bad_reasons.append(res.reason)
            return bad_reasons


    def __init__(self, username, secret, bucket_name):
        self.username = username
        self.secret = secret
        self.bucket_name = bucket_name

    def _time(self):
        return int(round(time.time() * 1000))

    def _post_file(self, r4id, operation, time, file_contents):
        form = {
            'username': 'username',
            'secret': 'secret',
            'timestamp': time,
            'operation': operation,
            'r4id': str(int(r4id,16)),
            'file': file_contents,
        }
        res = requests.post(self.read_string, data = form)
        # post the file to a fileserver
        return R4.Status(self, r4id)

    def create(self, file_contents):
        '''
        Create a file for the given id
        '''
        timestamp = self._time()
        r4id = R4.Id.create(file_contents, timestamp)
        return self._post_file(r4id, 'create', timestamp, file_contents)

    def read(self, r4id):
        '''
        Read the file for the given id
        '''
        return requests.get(
            self.read_string.format({
                'addr': server_addr,
                'username': self.R4.username,
                'bucket': self.R4.bucket_name,
                'r4id': self.r4id,
                }))

    def update(self, r4id, new_file_contents):
        '''
        Upload a file to replace the file at the given id
        '''
        timestamp = self._time()
        return self._post_file(r4id, 'update', timestamp, file_contents)

    def delete(self, r4id):
        '''
        Delete the file for the given id
        '''
        return self._post_file(r4id, 'delete', timestamp, '')
