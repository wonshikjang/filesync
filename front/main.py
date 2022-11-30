import os
import time
from log import printLog
from log import setLogging
from FileChecker import FileChecker
from config.Config import Config

if __name__ == '__main__':
    app = App()
    target = app.checkFirstExec()           # target setting
    fileChecker = FileChecker(target)       # create File Checker
    
    # run
    app.run(fileChecker.observer)           # run file checker
    
class App:
    def __init__(self):
        # app setting
        setLogging()
        
    def checkFirstExec():
        config = Config()
        try:
            target = config.getConfig("CLIENT_CONFIG", "target_path")
        except KeyError:
            target = input("Input yout SYNC PATH: ")
            config.setConfig("CLIENT_CONFIG", "target_path", target)
        return target
    
    def run(observer):
        observer.start()
        try:
            while True:
                time.sleep(1)
                printLog("watching file changed...")
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        