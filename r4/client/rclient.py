import boto3
import botocore
import copy
import logging
import threading

from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print = logger.info

class AbstractFileManager(object):
    def read(self, size):
        raise NotYetImplemented()
    def write(self):
        raise NotYetImplemented()

class UploadManagerFactory(object):
    '''
    Create a class to manage upload performance
    '''
    def __init__(self, data=None, fractional_upload=1):
        if not isinstance(data, bytes):
            self.data = ''.encode('utf-8')
        else:
            self.data = data
        logger.info('UMF data %s' % (self.data,))

        self.fractional_upload = int(fractional_upload)
        if self.fractional_upload <= 1:
            self.fractional_upload = 1

        self.completed_uploads = 0

        self.write_lock = threading.Lock()
        self.write_lock.acquire()

        self.process_lock = threading.Lock()

    def incremement_successful(self):
        with self.process_lock: # do this atomically
            if self.write_lock.locked():
                self.completed_uploads += 1
                logger.info('upload #%d / %d' % (self.completed_uploads, self.fractional_upload,))
                if self.completed_uploads >= self.fractional_upload:
                    logger.info('releasing write lock')
                    self.write_lock.release()
            else:
                logger.info('upload skipped by logic')

    def generate_manager(self):
        return UploadManager(data=self.data, callback=self.incremement_successful)

    def block_until_upload(self):
        with self.write_lock:
            logger.debug('upload manager completed uploads')

class UploadManager(AbstractFileManager):
    '''
    Manage thread read for uploads
    '''
    def __init__(self, data=None, callback=None):
        self.index = 0
        self.id_ = 'Upload Manager'
        if not isinstance(data, bytes):
            self.data = ''.encode('utf-8')
        else:
            self.data = data

        self.callback = callback

        logger.info('UM data %s, callback %s' % (self.data, self.callback,))

    def read(self, size=None, *args, **kwargs):
        # returns bytes, reads the data
        if size is None:
            size = len(self.data)
        size = int(size)
        
        if self.index + size >= len(self.data):
            old_index = self.index + 0
            self.index = len(self.data)
            logger.info('read %s from %s' % (self.data[old_index:], self.id_,))
            if old_index >= len(self.data) and self.callback is not None:
                self.callback()
            return self.data[old_index:]
        else:
            old_index = self.index + 0
            self.index += size
            logger.info('read %s from %s' % (self.data[old_index:self.index], self.id_,))
            return self.data[old_index:self.index]

class DownloadManager(AbstractFileManager):
    '''
    Manage thread write for downloads

    fractional_download: select the minimum number of downloads that must
        complete before the data is unlocked and future downloads are skipped.
        <= 1 - accept the first download that completes and unlock data.
            Other downloads ignored
        > 1 - require n downloads
    verify_download: if True, compare all downloads and ensure that the version
        matches. Implies that all downloads must complete before the lock is
        released
    consensus_download: if True, compare all downloads and accept the data that
        appears in the most downloads. Currently implies that all downloads must
        complete before the data is unlocked. This may change if one data set
        has shown up as a majority, then the data can be unlocked early.
    '''
    def __init__(self, fractional_download=0, verify_download=False, consensus_download=False):
        self.data = ''.encode('utf-8')
        self.read_lock = threading.Lock()
        logger.info('acquiring lock')
        self.read_lock.acquire()
        self.process_lock = threading.Lock()

        # TODO(buckbaskin): is there a better way to write this logic?
        if verify_download:
            self.fractional_download = int(fractional_download)
            self.verify_download = True
            self.consensus_download = False
        elif consensus_download:
            self.fractional_download = int(fractional_download)
            self.consensus_download = True
            self.verify_download = False
        else:
            self.fractional_download = int(fractional_download)
            if self.fractional_download <= 1:
                self.fractional_download = 1
            self.consensus_download = False
            self.verify_download = False

        self.downloads_complete = 0

    def write(self, bytes_): # TODO what happens if it needs to write more data?
        with self.process_lock: # enforce atomic write
            if self.verify_download:
                raise NotYetImplemented()
            elif self.consensus_download:
                raise NotYetImplemented()
            else:
                if self.read_lock.locked():
                    self.downloads_complete += 1
                    logger.info('write #%d / %d' % (self.downloads_complete, self.fractional_download,))
                    self.data = bytes_
                    if self.downloads_complete >= self.fractional_download:
                        logger.info('releasing lock')
                        self.read_lock.release()
                else:
                    logger.info('write skipped by download logic')

    def block_until_downloaded(self):
        with self.read_lock:
            logger.debug('blocked until download complete')

class AbstractRegion(object):
    def __init__(self, region_id):
        if self.validate_region_id(region_id):
            self.region_id = region_id
        else:
            self.region_id = None

    def __str__(self):
        return 'Region("%s")' % (self.region_id,)

    def __repr__(self):
        return 'Region("%s")' % (self.region_id,)

    def validate_region_id(self, region_id):
        return True

class AbstractProvider(object):
    def __str__(self):
        raise NotYetImplemented()

    def list(self):
        raise NotYetImplemented()

    def create(self, bucket_name, region):
        raise NotYetImplemented()

    def delete(self, bucket_name):
        raise NotYetImplemented()

    def delete_all(self):
        raise NotYetImplemented()

    def upload(self, bucket_name, file_key, file_obj):
        raise NotYetImplemented()

    def download(self, bucket_name, file_key, file_obj):
        raise NotYetImplemented()

class S3(AbstractProvider):
    def __init__(self, region):
        if isinstance(region, S3.Region):
            self.region = region
            self.s3 = boto3.resource('s3', region_name=region.region_id)
            self.s3_client = boto3.client('s3', region_name=region.region_id)

    class Region(AbstractRegion):
        def validate_region_id(self, region_id):
            return region_id in {
                'ap-northeast-1',
                'ap-northeast-2',
                'ap-south-1',
                'ap-southeast-1',
                'ap-southeast-2',
                'ca-central-1',
                'eu-central-1',
                'eu-east-1',
                'eu-west-1',
                'eu-west-2',
                'sa-east-1',
                'us-east-1',
                'us-east-2',
                'us-west-1',
                'us-west-2',
            }

    def list(self):
        for bucket in self.s3_client.list_buckets()['Buckets']:
            yield bucket

    def create(self, bucket_name):
        try:
            if self.region.region_id == 'us-east-1':
                self.s3.Bucket(bucket_name).create()
            else:
                self.s3.Bucket(bucket_name).create(
                    CreateBucketConfiguration = {
                        'LocationConstraint': self.region.region_id,
                    })
            return True
        except botocore.exceptions.ClientError as e:
            if '%s' % (type(e),) == 'botocore.errorfactory.BucketAlreadyOwnedByYou':
                print('bucket %s already exists' % (bucket_name,))
            raise
            return False


    def delete(self, bucket_name):
        # All objects (including all object versions and Delete Markers) in the 
        #  bucket must be deleted before the bucket itself can be deleted.
        # print('begin delete %s' % (bucket_name,))
        self.s3.Bucket(bucket_name).objects.all().delete()
        self.s3.Bucket(bucket_name).delete()
        # print('end delete %s' % (bucket_name,))

    def delete_all(self):
        for bucket in self.list():
            self.delete(bucket['Name'])

    def upload(self, bucket_name, file_key, file_obj):
        self.s3.Bucket(bucket_name).upload_fileobj(Fileobj=file_obj, Key=file_key)

    def download(self, bucket_name, file_key, file_obj):
        self.s3.Bucket(bucket_name).download_fileobj(Key=file_key, Fileobj=file_obj)

class R4(AbstractProvider):
    def __init__(self):
        pass

    class Region(AbstractRegion):
        def validate_region_id(self, region_id):
            # accept 'filesystem' and '<portnum>.LocalR4'
            if region_id == 'filesystem':
                return True
            else:
                if '.' in region_id:
                    splits = region_id.split('.', 2)
                    if len(splits) == 2:
                        try:
                            num = int(splits[0])
                        except ValueError:
                            return False
                        return 1024 <= num <= 49151 and splits[1] == 'LocalR4'
                    return False


SUPPORTED_SERVICES = [
    'Amazon Web Services S3',
    'R4 Filesystem',
    'R4 Local Server',
    ]

class Client(AbstractProvider):
    '''
    A Client is an AbstractProvider that accepts any and all regions and 
    distributes its actions around all of the regions. It abstracts away needing
    to deal with each individual service and region while also automatically 
    increasing performance through parallelization and increasing reliability by
    eliminating a single point of failure
    '''
    default_regions = [
        S3.Region('us-east-1'),
        S3.Region('us-east-2'),
    ]
    def __init__(self, regions):
        self.clients = {}
        if regions is None:
            self.regions = default_regions
        else:
            self.regions = regions
        self._setup_regions()

    def _setup_regions(self):
        for region in self.regions:
            if isinstance(region, S3.Region):
                if 's3.'+region.region_id not in self.clients:
                    self.clients['s3.'+region.region_id] = S3(region)
            elif isinstance(region, R4.Region):
                if 'r4' not in self.clients:
                    self.clients['r4'] = R4()
            else:
                print('Unsupported Region %s' % (region,))

    def list(self):
        '''
        list all of the buckets that are available across all regions
        '''
        # TODO parallelize this with threads so that all the buckets are
        #  returned as soon as possible, not blocking for one long call

        for region in self.regions:
            if isinstance(region, S3.Region):
                client = 's3.'+region.region_id
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                for bucket in self.clients[client].list():
                    yield bucket

    def create(self, bucket_name):

        threads = []

        for region in self.regions:
            if isinstance(region, S3.Region):
                client = 's3.'+region.region_id
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                args = (region.region_id + '.' + bucket_name,)
                print('create %s' % (args,))
                threads.append(threading.Thread(target=self.clients[client].create, args=args))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def delete(self, bucket_name):
        threads = []

        for region in self.regions:
            if isinstance(region, S3.Region):
                client = 's3.'+region.region_id
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                threads.append(threading.Thread(target=self.clients[client].delete, args=(region.region_id + '.' + bucket_name,)))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def delete_all(self):
        threads = []

        for region in self.regions:
            if isinstance(region, S3.Region):
                client = 's3.'+region.region_id
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                threads.append(threading.Thread(target=self.clients[client].delete_all))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def upload(self, bucket_name, file_key, data, fractional_upload=None):
        threads = []

        if fractional_upload is None:
            fractional_upload = len(self.regions)

        umf = UploadManagerFactory(data=data, fractional_upload=int(fractional_upload))

        for region in self.regions:
            if isinstance(region, S3.Region):
                client = 's3.'+region.region_id
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                threads.append(threading.Thread(target=self.clients[client].upload, args=(region.region_id + '.' + bucket_name, file_key, umf.generate_manager(),)))

        for t in threads:
            t.start()

        logger.info('waiting on upload block')
        umf.block_until_upload()
        logger.info('completed upload block')
        return umf.data

    def download(self, bucket_name, file_key, fractional_download=None, verify_download=False, consensus_download=False):
        threads = []

        if fractional_download is None:
            fractional_download = len(self.regions)

        d = DownloadManager(fractional_download=fractional_download)

        for region in self.regions:
            if isinstance(region, S3.Region):
                client = 's3.'+region.region_id
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                threads.append(threading.Thread(target=self.clients[client].download, args=(region.region_id + '.' + bucket_name, file_key, d,)))

        for t in threads:
            t.start()

        d.block_until_downloaded()
        return d.data


if __name__ == '__main__':

    s3 = Client(regions=[
        S3.Region('us-east-1'),
        S3.Region('us-east-2'),
        S3.Region('us-west-1'),
        S3.Region('us-west-2'),
        ])
    
    bucket_name = 'io.r4.username03'

    # print('Client.create("%s")' % (bucket_name,))
    # s3.create(bucket_name)

    # for bucket in s3.list():
    #     print('Bucket? %s' % bucket['Name'])

    upload_this = 'Hello AWS World. 4 Threads!'.encode('utf-8')
    key = 'test_file'

    s3.upload(bucket_name, key, upload_this)
    print('uploaded file %s to bucket %s' % (key, bucket_name))

    # data = s3.download(bucket_name, key, fractional_download=1)
    # print('downloaded file %s from bucket %s\n%s' % (key, bucket_name, data))

    # s3.delete_all_buckets()
