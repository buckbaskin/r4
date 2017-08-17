import boto3
import botocore

class FileObj(object):
    def __init__(self, data=None, id_=None):
        if isinstance(data, bytes):
            self.data = data
        else:
            self.data = ''.encode('utf-8')
        self.id_ = id_
        self.index = 0

    def read(self, size=None, *args, **kwargs):
        # returns bytes, reads the data
        if size is None:
            size = len(self.data)
        size = int(size)
        print('read %s from %s' % (self.data, self.id_,))
        print('with size %d and args %s and kwargs %s' % (size, args, kwargs,))
        if self.index + size >= len(self.data):
            old_index = self.index + 0
            self.index = len(self.data)
            return self.data[old_index:]
        else:
            old_index = self.index + 0
            self.index += size
            return self.data[old_index:self.index]

    def write(self, bytes_, *args, **kwargs):
        print('write %s to %s' % (bytes_, self.id_,))
        self.data = bytes_

class AbstractRegion(object):
    def __init__(self, region_id):
        if self.validate_region_id(region_id):
            self.region_id = region_id
        else:
            self.region_id = None

    def validate_region_id(self, region_id):
        return True

class AbstractProvider(object):
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
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.s3_client = boto3.client('s3')

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

    def create(self, bucket_name, region):
        if not isinstance(region, S3.Region):
            return False
        try:
            self.s3.Bucket(bucket_name).create(
                CreateBucketConfiguration = {
                    'LocationConstraint': region.region_id,
                })
            return True
        except botocore.exceptions.ClientError:
            return False


    def delete(self, bucket_name):
        # All objects (including all object versions and Delete Markers) in the 
        #  bucket must be deleted before the bucket itself can be deleted.
        print('begin delete %s' % (bucket_name,))
        self.s3.Bucket(bucket_name).objects.all().delete()
        self.s3.Bucket(bucket_name).delete()
        print('end delete %s' % (bucket_name,))

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
                if 's3' not in self.clients:
                    self.clients['s3'] = S3()
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
                client = 's3'
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
                client = 's3'
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                threading.Thread(target=self.clients[client].create, args=(bucket_name,))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def delete(self, bucket_name):
        threads = []

        for region in self.regions:
            if isinstance(region, S3.Region):
                client = 's3'
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                threading.Thread(target=self.clients[client].delete, args=(bucket_name,))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def delete_all(self):
        threads = []

        for region in self.regions:
            if isinstance(region, S3.Region):
                client = 's3'
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                threading.Thread(target=self.clients[client].delete_all)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def upload(self, bucket_name, file_key, file_obj):
        threads = []

        for region in self.regions:
            if isinstance(region, S3.Region):
                client = 's3'
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                threading.Thread(target=self.clients[client].upload, args=(bucket_name, file_key, file_obj,))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def download(self, bucket_name, file_key, file_obj):
        threads = []

        for region in self.regions:
            if isinstance(region, S3.Region):
                client = 's3'
            elif isinstance(region, R4.Region):
                client = 'r4'
            else:
                client = None
            if client is not None:
                threading.Thread(target=self.clients[client].download, args=(bucket_name, file_key, file_obj))

        for t in threads:
            t.start()

        for t in threads:
            t.join()


if __name__ == '__main__':
    s3 = S3()
    bucket_found = False
    for bucket in s3.list():
        print('Bucket %s' % bucket['Name'])
        bucket_found = True

    if not bucket_found:
        print('No buckets found')

    upload_this = FileObj('Hello AWS World again'.encode('utf-8'), 'upload_this')
    key = 'test_file'
    bucket_name = 'io.r4.username03'

    s3.create(bucket_name, S3.Region('us-east-2'))

    s3.upload(bucket_name, key, upload_this)

    print('uploaded file %s to bucket %s' % (key, bucket_name))

    download_here = FileObj(None, 'download_here')

    s3.download(bucket_name, key, download_here)

    print('downloaded file %s from bucket %s\n%s' % (key, bucket_name, download_here.data))

    # s3.delete_all_buckets()
