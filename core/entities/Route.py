class FinkRoute:
    def __init__(self, record=None):
        if record:
            self.id = record['routeid']
            self.code = record['routecode']
            self.company_id = record['companyid']
            self.vat = record['vat']
