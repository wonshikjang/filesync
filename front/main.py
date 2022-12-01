import os
import log
from FileChecker import FileChecker
from config.Config import Config
import tkinter
import tkinter.filedialog
    
config = Config()

class App:
    def __init__(self):
        # gui terminal
        self.window = tkinter.Tk()
        self.window.title("File Sync")
        self.window.geometry("480x600")

        self.menu = tkinter.Menu(self.window)

        self.menu_setting =  tkinter.Menu(self.menu, tearoff = 0)
        self.menu_setting.add_command(label="Set path", command=self.set_path)
        self.menu_setting.add_separator()
        self.menu_setting.add_command(label="Exit", command=self.set_exit)
        self.menu.add_cascade(label="Setting", menu=self.menu_setting)

        self.scrollbar = tkinter.Scrollbar(self.window)
        self.scrollbar.pack(side="right", fill="y")

        self.text_terminal = tkinter.Text(self.window, yscrollcommand=self.scrollbar.set)
        self.text_terminal.bind("<Key>", lambda e: "break")
        self.text_terminal.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.text_terminal.yview)

        self.window.config(menu=self.menu)

        # app setting
        self.target = self.checkFirstExec()
        self.logger = log.logger(self)
        self.fileChecker = self.createFileChecker()
        self.observer = self.fileChecker.observer
        self.observer.start()
        
    def checkFirstExec(self):
        try:
            target = config.getConfig("CLIENT_CONFIG", "target_path")
        except KeyError:
            target = ""
            while not os.path.isdir(target):
                target = tkinter.filedialog.askdirectory(title='Select sync path')
            config.setConfig("CLIENT_CONFIG", "target_path", target)
        return target
    
    def createFileChecker(self):
        return FileChecker(self.target, self.logger)
    
    def run(self):
        self.logger.print_log("watching file changed...")
        self.window.after(5000, self.run)
    
    def text_print(self, text):
        self.text_terminal.insert(tkinter.END, text+"\n")
        self.text_terminal.see(tkinter.END)

    def set_path(self):
        self.target = tkinter.filedialog.askdirectory(initialdir=self.target, title='Select sync path')
        while not os.path.isdir(self.target):
            self.target = tkinter.filedialog.askdirectory(title='Select sync path')
        config.setConfig("CLIENT_CONFIG", "target_path", self.target)
        self.observer.stop()
        self.observer.join()

        del self.observer
        del self.fileChecker

        self.fileChecker = self.createFileChecker()
        self.observer = self.fileChecker.observer
        self.observer.start()
        self.logger.print_log("Changed sync folder to " + self.target)

    def set_exit(self):
        self.observer.stop()
        self.observer.join()
        # add some clean up...
        quit()

if __name__ == '__main__':
    app = App()
    app.window.after(0, app.run)
    app.window.mainloop()
        