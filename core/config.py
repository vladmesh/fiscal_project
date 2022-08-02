import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    POSTGRES_USER_DBF = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PW_DBF = os.environ.get('POSTGRES_PW', 'postgres')
    POSTGRES_URL_DBF = os.environ.get('POSTGRES_URL')
    POSTGRES_DB_DBF = os.environ.get('POSTGRES_DB', 'postgres')
    WEBAX_URL = os.environ.get('WEBAX_URL')



class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
