import requests
from main import config

class HTTP_API():
    def __init__(self):
        self.server_ip = config.getConfig("CLIENT_CONFIG", "server_ip")
        self.port = config.getConfig("CLIENT_CONFIG", "port")
        
    def getTotalFiles():
        pass

    def createFiles():
        pass

    def downloadFiles():
        pass

    def updateFiles():
        pass