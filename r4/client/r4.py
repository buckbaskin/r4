import errno
import os
import shutil

from hashlib import sha512
from pathlib import Path
from tempfile import TemporaryDirectory

from r4.client import AbstractProvider, AbstractRegion
from r4.logging import logger

class R4(AbstractProvider):
    def __init__(self):
        pass

    class Region(AbstractRegion):
        def validate_region_id(self, region_id):
            # accept 'filesystem' and '<portnum>.LocalR4'
            if '.' in region_id:
                splits = region_id.split('.', 2)
                if len(splits) == 2:
                    try:
                        num = int(splits[0])
                    except ValueError:
                        return False
                    return 1024 <= num <= 49151 and splits[1] == 'LocalR4'
                return False

class FileSystem(AbstractProvider):
    def __init__(self, region):
        self.region = region

        self.registry = {} # mapping of bucket names to entries (folder + known files)
        self.in_memory = (region.path == 'memory')
        if self.in_memory:
            self.temporary = True
        else:
            self.temporary = (region.path == 'temp')

        self.fs = None

    class Region(AbstractRegion):
        def __init__(self, region_id):
            super(FileSystem.Region, self).__init__(region_id)
            self.path = Path(region_id)

        def validate_region_id(self, region_id):
            try:
                Path(region_id)
            except OSError:
                return region_id == 'temp' or region_id == 'memory'
            return True

    def _initialize_filesystem(self):
        if self.in_memory:
            raise NotImplementedError()
        elif self.temporary:
            self.fs = Path(TemporaryDirectory())
        else:
            self.fs = self.region.path

    def list(self):
        # return the list of buckets on the local filesystem
        for bucket_name in self.registry:
            yield {'Name': bucket_name}

    def create(self, bucket_name):
        if self.fs is None:
            self._initialize_filesystem()

        if bucket_name in self.registry:
            return True

        folder_name = str(sha512(str(bucket_name).encode('utf-8')).hexdigest())[:32]
        folder_path = self.fs / folder_name
        try:
            os.makedirs(str(folder_path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
                return False

        self.registry[bucket_name] = {
            'folder_name': folder_name,
            'folder_path': folder_path,
            'file_listing': {},
        }
        return True

    def delete(self, bucket_name):
        if bucket_name not in self.registry:
            return True

        folder_path = self.registry[bucket_name]['folder_path']
        shutil.rmtree(folder_path)

        del self.registry[bucket_name]

        return True

    def delete_all(self):
        for bucket in self.list():
            self.delete(bucket['Name'])

    def upload(self, bucket_name, file_key, file_obj):
        logger.info('begin fs upload of in bucket %s for file %s' % (bucket_name, file_key,))
        logger.info(str(self.registry))
        if bucket_name not in self.registry:
            return False
        logger.info('name in registry')

        folder_path = self.registry[bucket_name]['folder_path']
        file_name = str(sha512(str(file_key).encode('utf-8')).hexdigest())[:32]
        file_full_path = str(folder_path / file_name)

        logger.info('ready to write file')

        with open(file_full_path, 'wb') as f:
            f.write(file_obj.read())
            f.write(file_obj.read())

        self.registry[bucket_name]['file_listing'][file_key] = {
            'file_name': file_name,
            'file_full_path': file_full_path,
        }

        logger.info('file written')

        return True

    def download(self, bucket_name, file_key, file_obj):
        if bucket_name not in self.registry:
            return False

        file_full_path = self.registry[bucket_name]['file_listing'][file_key]['file_full_path']

        with open(file_full_path, 'rb') as f:
            file_obj.write(f.read())

        return True
