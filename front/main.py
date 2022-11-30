import os
import time
from log import printLog, setLogging
from FileChecker import FileChecker
from config.Config import Config
    
class App:
    def __init__(self):
        # app setting
        setLogging()
        self.config = Config()
        self.target = self.checkFirstExec()
        self.fileChecker = self.createFileChecker()
        self.observer = self.fileChecker.observer
        
    def checkFirstExec(self):
        try:
            target = self.config.getConfig("CLIENT_CONFIG", "target_path")
        except KeyError:
            target = input("Input yout SYNC PATH: ")
            self.config.setConfig("CLIENT_CONFIG", "target_path", target)
        return target
    
    def createFileChecker(self):
        return FileChecker(self.target)
    
    def run(self):
        self.observer.start()
        try:
            while True:
                time.sleep(1)
                printLog("watching file changed...")
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
        

if __name__ == '__main__':
    app = App()
    app.run()
        