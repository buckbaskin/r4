class AbstractFileManager(object):
    def read(self, size):
        raise NotYetImplemented()
    def write(self):
        raise NotYetImplemented()

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

SUPPORTED_SERVICES = [
    'Amazon Web Services S3',
    # 'R4 Filesystem',
    # 'R4 Local Server',
    ]

from r4.client.rclient import Client