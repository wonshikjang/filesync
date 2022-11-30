import configparser

class Config:
    def createConfig(target):
        config = configparser.ConfigParser()
        
        config["CLIENT_CONFIG"] = {
            "SERVER_IP" : "서버주소",
            "PORT" : "포트번호",
            "TARGET_PATH" : ""
        }
        
        with open("./config/config.ini", "w") as f:
            config.write(f)