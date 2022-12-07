from File import File, FileList
import asyncio
import os, re
import uuid
from pathlib import Path
from Error import AlreadyChecked, NeedToUpdated
from API import API
import shutil
import time
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

    def reset_set_path(self, target):
        self.target = target
        self.filelist.updateTarget(target)
        self.api.target = target
        self.observer = self.setObserver(self.target)
        self.syncToServer(self.findToUpdate())

    def findToUpdate(self):
        self.logger.print_log("")
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
            time.sleep(0.5)
            f = self.filelist.append("%s%s" % (self.target, file["path"][4:]))
            f.id = uuid.UUID(file["id"])
        self.logger.print_log("SYNCHRONIZATION COMPLETE")
        self.logger.print_log("")
        self.observer.start()
    
    async def socketDataCheck(self, d_list):
        # 빈 폴더들 삭제
        # for (path, dir, file) in os.walk(self.target):
        #     for d in dir:
        #         try:
        #             if os.path.exists("%s/.DS_Store" % path):
        #                 os.remove("%s/.DS_Store" % path)
        #             os.rmdir("%s/%s" % (path, d))
        #         except:
        #             continue
        
        # 파일 받아오기
        # need_update = asyncio.run(self.api.getFileList())
        self.logger.print_log("(WATCHDOG) WATCHING FILES...")
        print("----WEBSOCKETS DATALIST----")
        if len(d_list) == 0:
            print("[]")
        else:
            print("[")
            for d in d_list:
                dics_keys = d.keys()
                print("  {")
                for key in dics_keys:
                    print("    %s : %s" %(key, d[key]))
                print("  }")
            print("]")
        print("----LOCAL FILE DATALIST----")
        print(self.filelist)
        
        # path 같을 시 id 업데이트
        # d_list에 존재하지 않는 파일 삭제
        invalid = self.filelist.updateId(d_list)
        # print("🤪", invalid)
        for f_loc in invalid:
            self.filelist.serverUpdate(f_loc)
            os.remove(f_loc.real_path)
            self.filelist.serverUpdate(f_loc)
            self.filelist.del_file(f_loc.real_path)
            self.logger.print_log("(WEBSOCKET) FILE DELETED : %s" % f_loc.name)

        for d in d_list:
            f_loc = self.filelist.search_id(d["id"])
        
            # 파일이 존재하지 않으면 생성
            if not f_loc:
                # 파일 다운로드
                # 임시 파일 생성 시 # 옵저버에서 컷
                # print("🤬", str(self.filelist.getRealPath(d["path"])))
                f = self.filelist.append_tmp(str(self.filelist.getRealPath(d["path"])))
                self.logger.print_log("(WEBSOCKET) NEW FILE UPLOADED %s" % d["name"])
                asyncio.run(self.api.downloadFile(d["id"]))
                
            elif d["md5"] != f_loc.md5:
                self.filelist.serverUpdate(f_loc)
                os.remove(f_loc.real_path)
                self.filelist.serverUpdate(f_loc)
                f = self.filelist.append_tmp(str(self.filelist.getRealPath(d["path"])))
                asyncio.run(self.api.downloadFile(f_loc.id))
                self.logger.print_log("(WEBSOCKET) FILE UPDATED %s" % f_loc.name)
                
            elif Path(d["path"]) != f_loc.sync_path:
                r_src_path_str = str(f_loc.real_path)
                r_dest_path_str = str(self.filelist.getRealPath(d["path"]))

                # print("😈", r_src_path_str)
                # print("😈", r_dest_path_str)
                
                self.filelist.serverUpdate(f_loc)
                os.makedirs(self.filelist.getDirPath(self.filelist.getRealPath(d["path"])), exist_ok=True)
                time.sleep(0.5)
                shutil.move(r_src_path_str, r_dest_path_str)
                self.filelist.del_file(f_loc.real_path)
                self.filelist.serverUpdate(f_loc)
                
                self.logger.print_log("(WEBSOCKET) FILE MOVED : MOVE %s" % f_loc.name)
            
    def socketDisconnect(self):
        # print("Free file from server update")
        self.filelist.freeServerUpdate()
            
    def setObserver(self, target):
        observer = Observer()
        observer.schedule(self, target, recursive=True)
        return observer
        
    def on_created(self, event):
        if event.is_directory:
            return
        
        # print("😡 on created", event.src_path)
        
        # 터미널 서 파일 생성 시 .파일이름.txt.swt? 무시
        if re.match(f"{self.target}/.*?\.txt\.[a-zA-Z0-9-~]+", str(event.src_path)):
            # print("first")
            # print(event.src_path)
            return
        
        # 이미 해당 경로에 파일이 존재하면 무시
        f = self.filelist.search(event.src_path) 
        if f:
            if f.md5 == None or f.size == None:
                f.md5 = f.makeMd5(event.src_path)
                f.size = Path(event.src_path).stat().st_size
                # print("🤩 updated! md5 and size")
                return
            else:
                return
            
        f = self.filelist.append(event.src_path)
        
        if not f.serverUpdating:
            self.logger.print_log("(WATCHDOG) FILE '%s' CREATED AT '%s'" % (f.name, f.dir))
            asyncio.run(self.api.createFile(f))
            asyncio.run(self.api.uploadFile(f))
        
    def on_moved(self, event):
        # print("😡 on moved", event.src_path, event.dest_path)
        
        # txt 파일 수정 시 임시 파일 생성으로 move 되고 moved 되는 것 무시
        if re.match(f"{self.target}/.*?\.txt\.[a-zA-Z0-9-]+", str(event.dest_path)):
            # print(event.dest_path)
            return
        
        f = self.filelist.move(event.src_path, event.dest_path)
        if f == -1:
            # self.logger.print_log("(WATCHDOG) MOVE DEST NOT FOUND : %s TO %s" % (event.src_path, event.dest_path))
            return
        else:
            if not f.serverUpdating:
                self.logger.print_log("(WATCHDOG) FILE '%s' MOVED \n%sFROM %s \n%sTO%s" % (f.name, " "*21, re.sub(self.target, "Root", event.src_path), " "*21, re.sub(self.target, "Root", event.dest_path)))
                asyncio.run(self.api.modifyFile(f))
    
    def on_deleted(self, event):
        # 임시 파일 삭제되는 것 무시
        if re.match(f"{self.target}/.*?\.txt\.[a-zA-Z0-9-]+", str(event.src_path)):
            # print(event.src_path)
            return
        
        if event.is_directory:
            # print("😡 on deleted dir", event.src_path)
            fs = self.filelist.del_dir(event.src_path)
            if fs == []:
                # self.logger.print_log("(WATCHDOG) DELETE EMPTY DIR : %s" % event.src_path)
                return
            else:
                for f in fs:
                    if not f.serverUpdating:
                        asyncio.run(self.api.deleteFile(f))
                        self.logger.print_log("(WATCHDOG) FILE '%s' DELETED FROM '%s'" % (f.name, f.dir))
                        del f
        else:
            # print("😡 on deleted file", event.src_path)
            f = self.filelist.del_file(event.src_path)
            if f == -1:
                # self.logger.print_log("(WATCHDOG) CLEAR INVALID FILE : %s" % event.src_path)
                return
            elif f == 0:
                # print("😀 on delete socket detected")
                return
            else:
                asyncio.run(self.api.deleteFile(f))
                self.logger.print_log("(WATCHDOG) FILE '%s' DELETED FROM %s" % (f.name, f.dir))
                del f
        
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # print("😡 on modified", event.src_path)
        
        # 임시 파일 변경 무시
        if re.match(f"{self.target}/.*?\.txt\.[a-zA-Z0-9-]+", str(event.src_path)):
            # print(event.src_path)
            return 
        
        f = self.filelist.modify(event.src_path)
        
        if f == -1:
            # self.logger.print_log("(WATCHDOG) CAN'T NOT FIND FILE")
            # print("😡 Modify error cannot find file", event.src_path)
            return
        elif f == 0:
            # print("😡 no matter", event.src_path)
            # _f = open(event.src_path, 'r')
            # print(_f.read())
            # _f.close()
            return
        else:
            # print("😡 modify server data and update", event.src_path)
            # if not f[1].serverUpdating:
            asyncio.run(self.api.modifyFile(f[1]))
            asyncio.run(self.api.uploadFile(f[1]))
            self.logger.print_log("(WATCHDOG) File '%s' Modified %d bytes to %d bytes" % (f[1].name, f[0].size, f[1].size)) 
            del f[0]        