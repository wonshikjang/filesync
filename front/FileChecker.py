from File import File, FileList
import asyncio
import os, re
import uuid
from Error import AlreadyChecked, NeedToUpdated
from API import API
import nest_asyncio
nest_asyncio.apply()
try:
    from watchdog.observers import Observer
    from watchdog.events import RegexMatchingEventHandler
except ModuleNotFoundError as e:
    print("Module \'watchdog\' is not found")
    os.system("pip install watchdog")

class FileChecker(RegexMatchingEventHandler):
    def __init__(self, _target, _logger, _config):
        super().__init__(None, [".*\.py",".*\.pyc",".*\.ini", ".*\.DS\_Store", ".*thumbs\.db"], False, False)
        self.target = _target
        self.filelist = FileList(self.target)
        self.logger = _logger
        self.config = _config
        self.api = API(self.config, self.logger)
        self.observer = self.setObserver(self.target)
        # initial file sync
        self.syncToServer(self.findToUpdate())
        self.observer.start()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(self.api.connectSocket());
        asyncio.get_event_loop().run_forever();

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
                        if f_loc.sync_path == f_ser["path"]:
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
        self.logger.print_log("FILE '%s' CREATED AT '%s'" % (f.name, f.dir))
        asyncio.run(self.api.createFile(f))
        asyncio.run(self.api.uploadFile(f))
        # socket file created
        
    def on_moved(self, event):
        f = self.filelist.move(event.src_path, event.dest_path)
        if f == -1:
            self.logger.print_log("MOVE ERROR :", event.src_path, "TO", event.dest_path)
            return
        else:
            self.logger.print_log("FILE '%s' MOVED \n%sFROM %s \n%sTO%s" % (f.name, " "*21, re.sub(self.target, "Root", event.src_path), " "*21, re.sub(self.target, "Root", event.dest_path)))
            asyncio.run(self.api.modifyFile(f))
            # socket file moved
    
    def on_deleted(self, event):
        if event.is_directory:
            fs = self.filelist.del_dir(event.src_path)
            if fs == []:
                self.logger.print_log("DELETE EMPTY DIR :", event.src_path)
                return
            else:
                for f in fs:
                    self.logger.print_log("FILE '%s' DELETED FROM '%s'" % (f.name, f.dir))
                    asyncio.run(self.api.deleteFile(f))
                    del f
                # socket Delete fs lists
        else:
            f = self.filelist.del_file(event.src_path)
            if f == -1:
                self.logger.print_log("DELETE FILE ERROR : %s" % event.src_path)
                return
            else:
                self.logger.print_log("FILE '%s' DELETED FROM %s" % (f.name, f.dir))
                asyncio.run(self.api.deleteFile(f))
                del f
                # socket Delete f
        
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