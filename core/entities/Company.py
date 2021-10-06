


class Company:
    redis_key = 'companies'

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
