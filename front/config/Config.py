import configparser

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        
    def getConfig(self, section, name):
        self.config.read("./config/clientConfig.ini")
        return self.config[section][name]
    
    def setConfig(self, section, name, value):
        self.config.read("./config/clientConfig.ini")
        self.config[section][name] = value
        with open("./config/clientConfig.ini", "w") as f:
            self.config.write(f)
        
    def resetConfig(self):
        self.config.read("clientConfig.ini")
        self.config["CLIENT_CONFIG"] = {
            "SERVER_IP" : "서버주소",
            "PORT" : "포트번호",
        }
        with open("./config/clientConfig.ini", "w") as f:
            self.config.write(f)
            