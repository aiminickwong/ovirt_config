from . import config
class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

property=classproperty
class Const(object):
    @property
    def ENGINE_DB_ENV_KEYS(self):
        return {
            'host': EngineDBEnv.HOST,
            'port': EngineDBEnv.PORT,
            'secured': EngineDBEnv.SECURED,
            'hostValidation': EngineDBEnv.SECURED_HOST_VALIDATION,
            'user': EngineDBEnv.USER,
            'password': EngineDBEnv.PASSWORD,
            'database': EngineDBEnv.DATABASE,
            'connection': EngineDBEnv.CONNECTION,
            'pgpassfile': EngineDBEnv.PGPASS_FILE,
            'newDatabase': EngineDBEnv.NEW_DATABASE,
        }

class EngineDBEnv(object):

    @property
    def HOST(self):
        return 'OVESETUP_DB/host'

    @property
    def PORT(self):
        return 'OVESETUP_DB/port'
    @property
    def SECURED(self):
        return 'OVESETUP_DB/secured'

    @property
    def SECURED_HOST_VALIDATION(self):
        return 'OVESETUP_DB/securedHostValidation'

    @property
    def DATABASE(self):
        return 'OVESETUP_DB/database'
    @property
    def USER(self):
        return 'OVESETUP_DB/user'
    @property
    def PASSWORD(self):
        return 'OVESETUP_DB/password'

    CONNECTION = 'OVESETUP_DB/connection'
    STATEMENT = 'OVESETUP_DB/statement'
    PGPASS_FILE = 'OVESETUP_DB/pgPassFile'
    NEW_DATABASE = 'OVESETUP_DB/newDatabase'

    @property
    def FIX_DB_VIOLATIONS(self):
        return 'OVESETUP_DB/fixDbViolations'


class FileLocations(object):

    OVIRT_ENGINE_SERVICE_CONFIG_DEFAULTS = \
        config.ENGINE_SERVICE_CONFIG_DEFAULTS

    OVIRT_ENGINE_SERVICE_CONFIG = config.ENGINE_SERVICE_CONFIG
