class SourceSettings:
    def __init__(self, record):
        self.id = record['id']
        self.source_type = record['source_type']
        self.address = record['address']
        self.port = record['port']
        self.login = record['login']
        self.password = record['password']
        self.db_name = record['database_name']
        self.query_new_tickets = record['query_new_tickets']
