import configparser

from .utils import first_existent_path

__all__ = [
    'interception_config'
]


class InterceptionConfiguration(object):
    _sources = [
        "interception.ini",
        "resources/interception.ini",
        "C:/wafec/interception.ini",
        "/usr/wafec/interception.ini"
    ]

    def __init__(self):
        self.connection_string = "mysql+pymysql://testd:testd@localhost/testd?charset=utf8mb4"
        self.port = 7654

    def auto_initialize(self):
        source = first_existent_path(InterceptionConfiguration._sources)
        if source:
            config = configparser.ConfigParser()
            config.read(source)
            self.connection_string = config.get('database', 'connection_string', fallback=self.connection_string)
            self.port = config.getint('DEFAULT', 'port', fallback=self.port)


interception_config = InterceptionConfiguration()
interception_config.auto_initialize()
