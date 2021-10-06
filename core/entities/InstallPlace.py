class InstallPlace:
    redis_key = 'install_places'


    def __init__(self, id, address):
        self.id = id
        self.address = address
