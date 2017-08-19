from r4.client import AbstractProvider, AbstractRegion

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
