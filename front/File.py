import uuid
import hashlib
import os
import re

class FileList():
    def __init__(self):
        self.fileList = []
        # 서버에서 총 파일 리스트 업데이트
    
    def __str__(self):
        file_list = "[\n"
        for file in self.fileList:
            file_list += file.__str__()
            file_list += ", "
        file_list += "\n]"
        return file_list
            
    def append(self, path):
        f = File(path)
        self.fileList.append(f)
        return f
    
    def move(self, src, dest):
        for file in self.fileList:
            if file.path == src:
                file.move(dest)
                return file
        return -1
    
    def modify(self, path):
        for file in self.fileList:
            if file.path == path:
                file_before = file.copy()
                file.modify(path)
                if file.md5 == file_before.md5:
                    del file_before
                    return 0
                else:
                    return [file_before, file]
        return -1
    
    def del_dir(self, path): # delete Directory
        del_files = []
        i = len(self.fileList)
        while i > 0:
            i -= 1
            file = self.fileList[i]
            pattern = "%s.*" % path
            if re.match(pattern, file.path):
                self.fileList.remove(file)
                del_files.append(file)
            
        return del_files if len(del_files) > 0 else -1
    
    def del_file(self, path): # deltet File
        for file in self.fileList:
            if file.path == path:
                self.fileList.remove(file)
                return file
        return -1
    
    
class File():
    def __init__(self, path):
        self.id = uuid.uuid4()
        self.name = path.split("/")[-1] 
        self.path = path
        self.dir = path[:len(path)-(len(self.name)+1)]
        self.size = os.path.getsize(path)
        self.md5 = self.makeMd5(path)
    
    def __del__(self):
        pass
    
    def __str__(self):
        return "File : { \n\tid : %s, \n\tname : %s, \n\tpath : %s, \n\tsize : %d, \n\tmd5 : %s \n}" % (self.id, self.name, self.path, self.size, self.md5)
    
    def modify(self, path):
        self.size = os.path.getsize(path)
        self.md5 = self.makeMd5(path)
        
    def move(self, path):
        self.name = path.split("/")[-1] 
        self.path = path
        self.dir = path[:len(path)-(len(self.name)+1)]
        
    def copy(self):
        f = File(self.path)
        f.id = "Not Valid"
        f.size = self.size
        f.md5 = self.md5
        return f
        
    def makeMd5(self, path):
        f = open(path, 'r').read()
        md5 = hashlib.md5(f.encode()).hexdigest()
        return md5