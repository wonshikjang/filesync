import os
from log import setLogging
from config import Config
from FileChecker import setObserver
from config.Config import Config

if __name__ == '__main__':
    if not os.path.isfile("client.ini"):
        # client.ini 파일 존재하지 않을 시
        target = input("Input yout SYNC PATH: ")
        Config.createConfig(target)
    
    setLogging()
    setObserver(target)