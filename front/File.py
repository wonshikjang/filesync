import uuid
import hashlib
import os
import re

class FileList():
    def __init__(self, target):
        self.target = target
        self.fileList = []
        # 서버에서 총 파일 리스트 업데이트
    
    def __str__(self):
        file_list = "[\n"
        for file in self.fileList:
            file_list += file.__str__()
            file_list += ", "
        file_list += "\n]"
        return file_list
    
    def search(self, path):
        for f in self.fileList:
            if f.path == path:
                return f
        return None

    # def pop(self, path=None):
    #     if path:
    #         for file in self.fileList:
    #             if file.path == path:
    #                 self.fileList.remove(file)
    #                 return file
    #         return None
    #     else:
    #         return self.fileList.pop()
    
    def append(self, path):
        f = File(self.target, path)
        self.fileList.append(f)
        return f
                
    def move(self, src, dest):
        for file in self.fileList:
            if file.real_path == src:
                file.move(dest)
                return file
        return -1
    
    def modify(self, path):
        for file in self.fileList:
            if file.real_path == path:
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
            if re.match(pattern, file.real_path):
                self.fileList.remove(file)
                del_files.append(file)
            
        return del_files
    
    def del_file(self, path): # deltet File
        for file in self.fileList:
            if file.real_path == path:
                self.fileList.remove(file)
                return file
        return -1
    
    
class File():
    def __init__(self, target, path): # target 경로, 파일 실제 경로
        self.id = uuid.uuid4()
        self.name = path.split("/")[-1] # 파일 이름
        self.target = target # 타겟 경로
        self.real_path = path # 파일 실제 경로
        self.sync_path = re.sub(self.target, "Root", path) # 파일 가상 경로
        self.dir = self.sync_path[:len(self.sync_path)-(len(self.name)+1)] # 파일 가상 디렉토리
        self.size = os.path.getsize(path) # 파일 사이즈
        self.md5 = self.makeMd5(path) # 파일 md5
    
    def __del__(self):
        pass
    
    def __str__(self):
        return "File : { \n\tid : %s, \n\tname : %s, \n\ttarget : %s, \n\tpath : %s, \n\tsize : %d, \n\tmd5 : %s \n}" % (self.id, self.name, self.target, self.sync_path, self.size, self.md5)
    
    def modify(self, path):
        self.size = os.path.getsize(path)
        self.md5 = self.makeMd5(path)
        
    def move(self, path):
        self.name = path.split("/")[-1] 
        self.real_path = path # 파일 실제 경로
        self.sync_path = re.sub(self.target, "Root", path) # 파일 가상 경로
        self.dir = self.sync_path[:len(self.sync_path)-(len(self.name)+1)] # 파일 가상 디렉토리
        
    def copy(self):
        f = File(self.target, self.real_path)
        f.id = "Not Valid"
        f.size = self.size
        f.md5 = self.md5
        return f
        
    def makeMd5(self, path):
        try:
            f = open(path, 'r').read()
            md5 = hashlib.md5(f.encode()).hexdigest()
            return md5
        except UnicodeDecodeError:
            f = open(path, 'rb').read()
            md5 = hashlib.md5(f).hexdigest()
            return md5