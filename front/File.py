import uuid
import hashlib
import os

class FileList():
    def __init__(self):
        self.fileList = []
    
    def append(path): # create File
        pass
        # f = File(path)
        # self.fileList.append(f)
    
    def update(): # modify File
        pass
    
    def del_dir(): # delete Directory
        pass
    
    def del_file(): # deltet File
        pass
    
    
class File():
    def __init__(self, path):
        self.id = uuid.uuid4()
        self.update(path)
    
    def update(self, path):
        self.name = path.split("/")[-1] 
        self.dir = path[:len(path)-(len(self.name)+1)]
        self.size = os.path.getsize(path)
        self.md5 = self.makeMd5(path)
        
    def makeMd5(self, path):
        f = open(path, 'r').read()
        md5 = hashlib.md5(f.encode()).hexdigest()
        return md5