import time
from log import printLog
from File import File, FileList
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ModuleNotFoundError as e:
    print("Module \'watchdog\' is not found")
    os.system("pip install watchdog")

def setObserver(target):
    observer = Observer()
    file_checker = FileChecker(target)
    observer.schedule(file_checker, target, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
            printLog("watching file changed...")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


class FileChecker(FileSystemEventHandler):
    def __init__(self, target):
        self.target = target
        self.filelist = FileList()
    
    def on_created(self, event):
        print("----------created------------")
        print(event)
        
        # f = File(event.src_path)
        
    def on_moved(self, event):
        print("----------moved--------------")
        print(event)
    
    def on_deleted(self, event):
        print("----------deleted------------")
        print(event)
    
    def on_modified(self, event):
        if event.is_directory:
            return
        print("----------modified-----------")
        print(event)
        f = File(event.src_path)
        print("File ID :", f.id)
        print("File Name :", f.name)
        print("File Dir :", f.dir)
        print("File MD5 :", f.md5)
        print("File SIZE :", f.size)