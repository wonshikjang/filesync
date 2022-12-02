from File import File, FileList
import asyncio
import os, re
import uuid
from Error import CustomError
try:
    from watchdog.observers import Observer
    from watchdog.events import RegexMatchingEventHandler
except ModuleNotFoundError as e:
    print("Module \'watchdog\' is not found")
    os.system("pip install watchdog")

class FileChecker(RegexMatchingEventHandler):
    def __init__(self, _target, _logger, _api):
        super().__init__(None, [".*\.py",".*\.pyc",".*\.ini", ".*\.DS\_Store", ".*thumbs\.db"], False, False)
        self.target = _target
        self.filelist = FileList(self.target)
        self.logger = _logger
        self.api = _api
        
        # initial file sync
        self.syncToServer(self.findToUpdate())
        
        self.observer = self.setObserver(_target)

    def findToUpdate(self):
        need_update = asyncio.run(self.api.getFileList())
        print(need_update)
        for (path, dir, file) in os.walk(self.target):
            for f in file:
                f_loc = self.filelist.append("%s/%s" % (path, f))
                # print(f_loc)
                try:
                    for f_ser in need_update:
                        if f_loc.sync_path == f_ser["path"]:
                            if f_loc.md5 == f_ser["md5"]:
                                f_loc.id = uuid.UUID(f_ser["id"])
                                need_update.remove(f_ser)
                                raise CustomError("Already checked")
                            else:
                                print(f_loc.name, "Delete Content modified file")
                                os.remove(f_loc.real_path)
                                self.filelist.pop()
                                raise CustomError("Already checked")
                            break
                    raise NotImplementedError("Delete path modified file")
                except NotImplementedError as e:
                    print(f_loc.name, e)
                    os.remove(f_loc.real_path)
                    self.filelist.pop()
                except CustomError as e:
                    continue
                
        for (path, dir, file) in os.walk(self.target):
            for d in dir:
                try:
                    os.rmdir("%s/%s" % (path, d))
                except:
                    print("Directory is not Empty :", d)
                    continue
        return need_update
    
    def syncToServer(self, need_update):
        # 파일 데이터 생성
        for file in need_update:
            ############
            # 파일 다운로드
            ############
            asyncio.run(self.api.downloadFile(file["id"]))
            
            # 다운로드 한 뒤에 append해야 size랑 md5 계산 가능
            f = self.filelist.append("%s%s" % (self.target, file["path"][:5]))
            f.id = uuid.UUID(file["id"])

        # print(self.filelist)
    
    def setObserver(self, target):
        observer = Observer()
        observer.schedule(self, target, recursive=True)
        return observer
        
    def on_created(self, event):
        if event.is_directory:
            return
        f = self.filelist.append(event.src_path)
        # 서버에 파일 정보 등록
        asyncio.run(self.api.createFile(f))
        
        ###########
        # 파일 업로드
        ###########
        asyncio.run(self.api.uploadFile(f))
        
        self.logger.print_log("File '%s' created at %s" % (f.name, f.dir))
        
    def on_moved(self, event):
        f = self.filelist.move(event.src_path, event.dest_path)
        asyncio.run(self.api.modifyFile(f))
        asyncio.run(self.api.uploadFile(f))
        if f == -1:
            self.logger.print_log("MOVE ERROR :", event.src_path, "to", event.dest_path)
            return
        else:
            self.logger.print_log("File '%s' moved \n\t\t\tfrom %s \n\t\t\tto   %s" % (f.name, re.sub(self.target, "Root", event.src_path), re.sub(self.target, "Root", event.dest_path)))
    
    def on_deleted(self, event):
        if event.is_directory:
            fs = self.filelist.del_dir(event.src_path)
            if fs == []:
                self.logger.print_log("DELETE EMPTY DIR :", event.src_path)
                return
            else:
                for f in fs:
                    asyncio.run(self.api.deleteFile(f))
                    self.logger.print_log("File '%s' deleted at %s" % (f.name, f.dir))
                    del f
        else:
            f = self.filelist.del_file(event.src_path)
            if f == -1:
                self.logger.print_log("DELETE FILE ERROR :", event.src_path)
                return
            else:
                asyncio.run(self.api.deleteFile(f))
                self.logger.print_log("File '%s' deleted at %s" % (f.name, f.dir))
                del f
        
    def on_modified(self, event):
        if event.is_directory:
            return
        f = self.filelist.modify(event.src_path)
        if f == -1:
            self.logger.print_log("MODIFY ERROR")
            return
        elif f == 0:
            return
        else:
            asyncio.run(self.api.modifyFile(f))
            asyncio.run(self.api.uploadFile(f))
            self.logger.print_log("File '%s' Modified %d bytes to %d bytes" % (f[1].name, f[0].size, f[1].size)) 
            del f[0]        