import configparser

conf = configparser.ConfigParser()
conf.read("config.ini",encoding="utf-8")


class Config():
    def __init__(self):
        self.default = Default()
        self.address = Address()
        self.secret = Secret()


class Default():
    def __init__(self):
        self.bsc = conf.get("default","bsc")
        self.slippageTolerance = int(conf.get("default","slippageTolerance"))

class Address():
    def __init__(self):
        self.tokenContract = conf.get("address","tokenContract")
        self.panRouterContract = conf.get("address","panRouterContract")
        self.wbnbContract = conf.get("address","wbnbContract")
        self.sender = conf.get("address","sender")

class Secret():
    def __init__(self):
        self.pricateKey = conf.get("secret","pricateKey")

