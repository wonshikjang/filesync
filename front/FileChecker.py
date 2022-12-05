from File import File, FileList
import asyncio
import os, re
import uuid
from pathlib import Path
from Error import AlreadyChecked, NeedToUpdated
from API import API
import shutil
import nest_asyncio
nest_asyncio.apply()
try:
    from watchdog.observers import Observer
    from watchdog.events import RegexMatchingEventHandler
except ModuleNotFoundError as e:
    print("Module \'watchdog\' is not found")
    os.system("pip install watchdog")

class FileChecker(RegexMatchingEventHandler):
    def __init__(self, app, _target, _logger, _config):
        super().__init__(None, [".*\.py",".*\.pyc",".*\.ini", ".*\.DS\_Store", ".*thumbs\.db"], False, False)
        self.target = _target
        self.filelist = FileList(self.target)
        self.logger = _logger
        self.config = _config
        self.api = API(app, self.config, self.logger)
        self.observer = self.setObserver(self.target)
        # initial file sync
        self.syncToServer(self.findToUpdate())

    def findToUpdate(self):
        self.logger.print_log("GETTING FILE DATAS FROM SERVER")
        need_update = asyncio.run(self.api.getFileList())
        self.logger.print_log("ARRIVED FILE DATAS  TO  CLIENT")
        self.logger.print_file_list(need_update)
        self.logger.print_log("CHECKING FILE TO UPDATE...")
        self.logger.print_log("--------------------------")
        for (path, dir, file) in os.walk(self.target):
            for f in file:
                if f == ".DS_Store":
                    continue
                f_loc = self.filelist.append("%s/%s" % (path, f))
                try:
                    for f_ser in need_update:
                        if f_loc.sync_path == Path(f_ser["path"]):
                            if f_loc.md5 == f_ser["md5"]:
                                f_loc.id = uuid.UUID(f_ser["id"])
                                need_update.remove(f_ser)
                                raise AlreadyChecked("NO NEED TO UPDATE %s" % f_loc.name)
                            else:
                                os.remove(f_loc.real_path)
                                self.filelist.pop()
                                raise AlreadyChecked("NEED TO UPDATE %s" %f_loc.name)
                            break
                    raise NeedToUpdated("NEED TO UPDATE %s" % f_loc.name)
                except NeedToUpdated as e:
                    self.logger.print_log(str(e))
                    os.remove(f_loc.real_path)
                    self.filelist.pop()
                except AlreadyChecked as e:
                    self.logger.print_log(str(e))
                    continue
            if os.path.exists("%s/.DS_Store" % path):
                os.remove("%s/.DS_Store" % path)
                
        for (path, dir, file) in os.walk(self.target):
            for d in dir:
                try:
                    os.rmdir("%s/%s" % (path, d))
                except:
                    continue
        self.logger.print_log("--------------------------")
        self.logger.print_log("ALL FILE CHECKED")
        return need_update
    
    def syncToServer(self, need_update):
        self.logger.print_log("SYNCHRONIZING TO SERVER")
        for file in need_update:
            asyncio.run(self.api.downloadFile(file["id"]))
            f = self.filelist.append("%s%s" % (self.target, file["path"][4:]))
            f.id = uuid.UUID(file["id"])
        self.logger.print_log("SYNCHRONIZATION COMPLETE")
        self.observer.start()
    
    async def socketDataCheck(self, d_list):
        print(self.filelist)
        # self.logger.print_log("WATCHING FILE CHANGED...")
        # loc에 존재하는 invalid파일들 삭제
        for f_loc in self.filelist.checkInvalid(d_list):
            # 파일 삭제
            self.filelist.serverUpdate(f_loc)
            os.remove(f_loc.real_path)
            self.filelist.del_file(f_loc.real_path)
            self.logger.print_log("DELETED %s" % f_loc.name)
        
        for d in d_list:
            f_loc = self.filelist.search_id(d["id"])
            
            # 파일이 존재하지 않으면 생성
            if not f_loc:
                # 파일 다운로드
                f = self.filelist.append(str(self.filelist.getRealPath(d["path"])))
                f.id = d["id"]
                self.filelist.serverUpdate(f)
                asyncio.run(self.api.downloadFile(d["id"]))
                self.filelist.serverUpdate(f)
                print(self.filelist)
                print(d_list)                
                self.logger.print_log("CREATED %s" % d["name"])
                continue
            
            # 파일 내용이 변경되었으면 삭제 후 다시 다운로드
            elif d["md5"] != f_loc.md5:
                # 파일 삭제
                
                self.filelist.serverUpdate(f_loc)
                os.remove(f_loc.real_path)
                self.filelist.serverUpdate(f_loc)

                # 파일 다운로드
                self.filelist.serverUpdate(f_loc)
                asyncio.run(self.api.downloadFile(f_loc.id))
                self.filelist.serverUpdate(f_loc)
                
                self.logger.print_log("UPDATED %s" % f_loc.name)
                continue
            
            # 파일 경로(파일 이름) 변경 시 업데이트
            elif Path(d["path"]) != f_loc.sync_path:
                r_src_path_str = str(f_loc.real_path)
                r_dest_path_str = str(self.filelist.getRealPath(d["path"]))

                # 파일 경로 업데이트
                self.filelist.serverUpdate(f_loc)
                shutil.move(r_src_path_str, r_dest_path_str)
                self.filelist.serverUpdate(f_loc)
                
                self.logger.print_log("MOVED %s" % f_loc.name)
                continue
        
            
    def setObserver(self, target):
        observer = Observer()
        observer.schedule(self, target, recursive=True)
        return observer
        
    def on_created(self, event):
        if event.is_directory:
            return
        
        if self.filelist.search(event.src_path):
            return
        
        f = self.filelist.append(event.src_path)
        
        if not f.serverUpdating:
            self.logger.print_log("FILE '%s' CREATED AT '%s'" % (f.name, f.dir))
            asyncio.run(self.api.createFile(f))
            asyncio.run(self.api.uploadFile(f))
        
    def on_moved(self, event):
        f = self.filelist.move(event.src_path, event.dest_path)
        if f == -1:
            self.logger.print_log("MOVE ERROR : %s TO %s" % (event.src_path, event.dest_path))
            return
        else:
            if not f.serverUpdating:
                self.logger.print_log("FILE '%s' MOVED \n%sFROM %s \n%sTO%s" % (f.name, " "*21, re.sub(self.target, "Root", event.src_path), " "*21, re.sub(self.target, "Root", event.dest_path)))
                asyncio.run(self.api.modifyFile(f))
    
    def on_deleted(self, event):
        if event.is_directory:
            fs = self.filelist.del_dir(event.src_path)
            if fs == []:
                self.logger.print_log("DELETE EMPTY DIR : %s" % event.src_path)
                return
            else:
                for f in fs:
                    if not f.serverUpdating:
                        self.logger.print_log("FILE '%s' DELETED FROM '%s'" % (f.name, f.dir))
                        asyncio.run(self.api.deleteFile(f))
                        del f
        else:
            f = self.filelist.del_file(event.src_path)
            if f == -1:
                # self.logger.print_log("DELETE FILE ERROR : %s" % event.src_path)
                return
            else:
                if not f.serverUpdating:
                    self.logger.print_log("FILE '%s' DELETED FROM %s" % (f.name, f.dir))
                    asyncio.run(self.api.deleteFile(f))
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
            if not f.serverUpdating:
                asyncio.run(self.api.modifyFile(f[1]))
                asyncio.run(self.api.uploadFile(f[1]))
                self.logger.print_log("File '%s' Modified %d bytes to %d bytes" % (f[1].name, f[0].size, f[1].size)) 
                del f[0]        