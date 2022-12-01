from File import File, FileList
import os
try:
    from watchdog.observers import Observer
    from watchdog.events import RegexMatchingEventHandler
except ModuleNotFoundError as e:
    print("Module \'watchdog\' is not found")
    os.system("pip install watchdog")

class FileChecker(RegexMatchingEventHandler):
    def __init__(self, _target, _logger):
        super().__init__(None, [".*\.py"], False, False)
        self.target = _target
        self.filelist = FileList()
        self.observer = self.setObserver(_target)
        self.logger = _logger
    
    def setObserver(self, target):
        observer = Observer()
        observer.schedule(self, target, recursive=True)
        return observer
        
    def on_created(self, event):
        if event.is_directory:
            return
        f = self.filelist.append(event.src_path)
        self.logger.print_log("File '%s' created at %s" % (f.name, f.dir))
        
    def on_moved(self, event):
        f = self.filelist.move(event.src_path, event.dest_path)
        if f == -1:
            self.logger.print_log("MOVE ERROR")
            return
        else:
            self.logger.print_log("File '%s' moved \n\t\t\tfrom %s \n\t\t\tto   %s" % (f.name, event.src_path, event.dest_path))
    
    def on_deleted(self, event):
        if event.is_directory:
            print(event)
            fs = self.filelist.del_dir(event.src_path)
            if fs == -1:
                self.logger.print_log("DELETE DIR ERROR")
                return
            else:
                for f in fs:
                    self.logger.print_log("File '%s' deleted at %s" % (f.name, f.dir))
                    del f
        else:
            f = self.filelist.del_file(event.src_path)
            if f == -1:
                self.logger.print_log("DELETE FILE ERROR")
                return
            else:
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
            self.logger.print_log("File '%s' Modified %d bytes to %d bytes" % (f[1].name, f[0].size, f[1].size)) 
            del f[0]        