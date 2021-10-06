
class Cashbox:
    redis_key = 'cashboxes'

    def __init__(self,
                 ip=None,
                 company_id=None,
                 port=None,
                 fn_number=None,
                 location_id=None,
                 registry_number=None,
                 factory_number=None,
                 ofd_inn=None,
                 auto_device_number=None
                 ):
        self.id = factory_number
        self.ip = ip
        self.company_id = company_id
        self.port = port
        self.fn_number = fn_number
        self.location_id = location_id
        self.registry_number = registry_number
        self.factory_number = factory_number
        self.ofd_inn = ofd_inn
        self.auto_device_number = auto_device_number
