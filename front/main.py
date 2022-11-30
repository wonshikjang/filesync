import os
import time
from log import printLog
from log import setLogging
from FileChecker import FileChecker
from config.Config import Config

if __name__ == '__main__':
    setLogging()
    config = Config()
    
    try:
        target = config.getConfig("CLIENT_CONFIG", "target_path")
    except KeyError:
        target = input("Input yout SYNC PATH: ")
        config.setConfig("CLIENT_CONFIG", "target_path", target)
        
    fileChecker = FileChecker(target)
    observer = fileChecker.observer
    observer.start()
    try:
        while True:
            time.sleep(1)
            printLog("watching file changed...")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()