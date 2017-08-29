import boto3
import botocore
import copy
import logging
import threading

from collections import deque
from r4.client import AbstractFileManager, AbstractProvider
from r4.client.s3 import S3
from r4.client.r4 import R4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print = logger.info

class UploadManagerFactory(object):
    '''
    Create a class to manage upload performance
    '''
    def __init__(self, data=None, fractional_upload=1):
        if not isinstance(data, bytes):
            self.data = ''.encode('utf-8')
        else:
            self.data = data
        logger.debug('UMF data %s' % (self.data,))

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

        logger.debug('UM data %s, callback %s' % (self.data, self.callback,))

    def read(self, size=None, *args, **kwargs):
        # returns bytes, reads the data
        if size is None:
            size = len(self.data)
        size = int(size)
        
        if self.index + size >= len(self.data):
            old_index = self.index + 0
            self.index = len(self.data)
            logger.debug('read %s from %s' % (self.data[old_index:], self.id_,))
            if old_index >= len(self.data) and self.callback is not None:
                self.callback()
            return self.data[old_index:]
        else:
            old_index = self.index + 0
            self.index += size
            logger.debug('read %s from %s' % (self.data[old_index:self.index], self.id_,))
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
                        self.read_lock.release()
                else:
                    logger.info('write skipped by download logic')

    def block_until_downloaded(self):
        with self.read_lock:
            logger.debug('blocked until download complete')

class Client(AbstractProvider):
    '''
    A Client is an AbstractProvider that accepts any and all regions and 
    distributes its actions around all of the regions. It abstracts away needing
    to deal with each individual service and region while also automatically 
    increasing performance through parallelization and increasing reliability by
    eliminating a single point of failure
    '''
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
        bucket_name = 'io.r4.client.%s' % (bucket_name,)

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
            if isinstance(region, R4.Region):
                client = 'r4'
            elif isinstance(region, S3.Region):
                client = 's3.'+region.region_id
            else:
                client = None
            if client is not None:
                threads.append(threading.Thread(target=self.clients[client].upload, args=(region.region_id + '.' + bucket_name, file_key, umf.generate_manager(),)))

        for t in threads:
            t.start()

        logger.debug('waiting on upload block')
        umf.block_until_upload()
        logger.debug('completed upload block')
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
