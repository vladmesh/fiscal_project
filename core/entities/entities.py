class Cashbox:
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


class Company:
    def __init__(self, id=None,
                 inn=None, kpp=None,
                 name=None,
                 full_name=None,
                 region=None,
                 payment_place=None,
                 authorized_person_name=None,
                 agent_agent=None,
                 tax=None,
                 provider_name=None,
                 provider_phone=None,
                 additional_field_meaning=None,
                 additional_field_value=None
                 ):
        self.id = id
        self.inn = inn
        self.kpp = kpp
        self.name = name
        self.full_name = full_name
        self.region = region
        self.payment_place = payment_place
        self.authorized_person_name = authorized_person_name
        self.agent_agent = agent_agent
        self.tax = tax
        self.provider_name = provider_name
        self.provider_phone = provider_phone
        self.additional_field_meaning = additional_field_meaning
        self.additional_field_value = additional_field_value

    def init_from_fink(self, record):
        self.id = record['companyid']
        self.inn = record['companyinn']
        self.kpp = record['companykpp']
        self.division = record['divisionid']
        self.tax = record['tax']


class InstallPlace:
    redis_key = 'install_places'

    def __init__(self, id, address):
        self.id = id
        self.address = address


class Ofd:
    def __init__(self, inn=None, ip=None, port=None, domain=None, name=None, email=None):
        self.id = inn
        self.inn = inn
        self.ip = ip
        self.port = port
        self.domain = domain
        self.name = name
        self.email = email
