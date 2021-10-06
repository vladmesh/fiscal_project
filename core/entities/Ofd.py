
class Ofd:
    redis_key = 'ofds'

    def __init__(self, inn=None, ip=None, port=None, domain=None, name=None, email=None):
        self.id = inn
        self.inn = inn
        self.ip = ip
        self.port = port
        self.domain = domain
        self.name = name
        self.email = email
