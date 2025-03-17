import configparser


class CaseSensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr


class Config:
    def __init__(self):
        self.config = CaseSensitiveConfigParser()
        self.config.read('config.ini')
        self.config.read('config.secrets.ini')

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, key, value):
        self.config[key] = value
    
# Config       
config = Config()
