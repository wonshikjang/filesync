import uuid
import hashlib
import re
import time
import asyncio
from pathlib import Path
from Error import AlreadyChecked

class FileList():
    def __init__(self, target):
        self.target = str(Path(target).as_posix())
        self.fileList = []
        # 서버에서 총 파일 리스트 업데이트
    
    def __str__(self):
        if len(self.fileList) == 0:
            return "[]"
        file_list = "[\n"
        for file in self.fileList:
            file_list += file.__str__()
            file_list += ", "
        file_list += "\n]"
        return file_list
    
    def updateTarget(self, target):
        self.target = str(Path(target).as_posix())
        for file in self.fileList:
            file.target = self.target
    
    def search(self, path):
        for f in self.fileList:
            if f.real_path.resolve() == Path(path).resolve():
                return f
        return None
    
    def search_id(self, _id):
        for f in self.fileList:
            if str(f.id) == str(_id):
                return f
        return None
    
    def getRealPath(self, sync_path):
        return Path(sync_path.replace("Root", str(Path(self.target).as_posix())))
    
    def getDirPath(self, real_path):
        return Path(real_path).parent
    
    def updateId(self, d_list):
        invalid = []
        for file in self.fileList:
            valid = False
            for d in d_list:
                # print(":D", d)
                if file.sync_path.resolve().as_posix() == Path(d["path"]).resolve().as_posix():
                    file.id = uuid.UUID(d["id"])
                    valid = True
                    break
            if not valid:
                invalid.append(file)
        return invalid
    
    def freeServerUpdate(self):
        for file in self.fileList:
            file.serverUpdating = False
            
    def pop(self, path=None):
        if path:
            for file in self.fileList:
                if file.path.resolve() == Path(path).resolve():
                    self.fileList.remove(file)
                    return file
            return None
        else:
            return self.fileList.pop()
    
    def append(self, path):
        # print("😀file append", path)
        if self.search(path):
            return -1
        f = File(self.target, str(Path(path)))
        self.fileList.append(f)
        return f
    
    def append_tmp(self, path):
        # print("😀file append_tmp", path)
        if self.search(path):
            return -1
        f = File(self.target, str(Path(path)), True)
        self.fileList.append(f)
        return f
                        
    def move(self, src, dest):
        # print("😀file move", src, "to", dest)
        for file in self.fileList:
            if file.real_path.resolve() == Path(src).resolve():
                file.move(dest)
                return file
        return -1
    
    def modify(self, path):
        for file in self.fileList:
            if file.real_path.resolve() == Path(path).resolve():
                file_before = file.copy()
                if file.makeMd5(path) == file_before.md5:
                    del file_before
                    return 0
                else:
                    file.modify(path)
                    return [file_before, file]
        return -1
    
    def serverUpdate(self, f, id=None):
        if f:
            f.serverUpdating = not f.serverUpdating
        else: 
            for file in self.fileList:
                if str(file.id) == id:
                    file.serverUpdating = not file.serverUpdating
    
    def del_dir(self, path): # delete Directory
        # print("😀del direcotry", path)
        del_files = []
        i = len(self.fileList)
        while i > 0:
            i -= 1
            file = self.fileList[i]
            pattern = "%s.*" % str(Path(path))
            if re.match(pattern, str(file.real_path)):
                self.fileList.remove(file)
                del_files.append(file)
            
        return del_files
    
    def del_file(self, path): # delete File
        # print("😀del file", path)
        for file in self.fileList:
            if file.real_path.resolve() == Path(path).resolve():
                if file.serverUpdating:
                    # print("😀socket updating file no delete")
                    return 0
                else:
                    self.fileList.remove(file)
                    return file
        return -1
    
class File():
    def __init__(self, _target, _path, _wait=None): # target 경로, 파일 실제 경로
        self.id = uuid.uuid4()
        self.target = Path(_target) # target 경로
        self.real_path = Path(_path) # 파일 실제 경로
        self.name = self.real_path.name # 파일 이름
        self.sync_path = Path(str(self.real_path.as_posix()).replace(str(self.target.as_posix()), "Root"))
        self.dir = self.sync_path.parent # 파일 가상 디렉토리
        self.serverUpdating = False
        if _wait:
            self.size = None
            self.md5 = None
        else:
            self.size = self.real_path.stat().st_size
            self.md5 = self.makeMd5(_path)
    
    def __del__(self):
        pass
    
    def __str__(self):
        return "    { \n    id : %s, \n    name : %s, \n    target : %s, \n    path : %s, \n    size : %d, \n    md5 : %s \n}" % (self.id, self.name, self.target, self.sync_path, self.size, self.md5)
    
    def modify(self, path):
        temp_path = Path(path)
        self.size = temp_path.stat().st_size
        self.md5 = self.makeMd5(temp_path)
        
    def move(self, path):
        temp_path = Path(path)
        self.name = temp_path.name
        self.real_path = temp_path # 파일 실제 경로
        self.sync_path = Path(str(self.real_path).replace(str(self.target), "Root")) # 파일 가상 경로
        self.dir = self.sync_path.parent # 파일 가상 디렉토리
        
    def copy(self):
        f = File(self.target, self.real_path)
        f.id = "Not Valid"
        f.size = self.size
        f.md5 = self.md5
        return f
    
    def makeMd5(self, path):
        temp_path = Path(path).resolve()
        try:
            f = open(str(temp_path), 'r').read()
            md5 = hashlib.md5(f.encode()).hexdigest()
            return md5
        except UnicodeDecodeError:
            f = open(temp_path, 'rb').read()
            md5 = hashlib.md5(f).hexdigest()
            return md5