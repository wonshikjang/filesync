import configparser
import os

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.ini_path = self.findIni()
        #self.ini_path = self.findIni2()
        
    def findIni(self):
        for (path, dir, files) in os.walk("."):
            for filename in files:
                ext = os.path.splitext(filename)[-1]
                if ext == ".ini":
                    return path + "/" + 'clientConfig.ini'
    
    def findIni2(self):
        for (path, dir, files) in os.walk("."):
            for filename in files:
                ext = os.path.splitext(filename)[-1]
                if ext == ".ini":
                    return path + "/" + 'clientConfig2.ini'
        
    def getConfig(self, section, name):
        self.config.read(self.ini_path)
        return self.config[section][name]
    
    def setConfig(self, section, name, value):
        self.config.read(self.ini_path)
        self.config[section][name] = value
        with open(self.ini_path, "w") as f:
            self.config.write(f)
        
    def resetConfig(self):
        self.config.read("clientConfig.ini")
        self.config["CLIENT_CONFIG"] = {
            "SERVER_IP" : "서버주소",
            "PORT" : "포트번호",
        }
        with open(self.ini_path, "w") as f:
            self.config.write(f)
            