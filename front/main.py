import os
import Logger
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
        self.window.geometry("600x600+0+0")

        self.menu = tkinter.Menu(self.window)

        self.menu_setting =  tkinter.Menu(self.menu, tearoff = 0)
        self.menu_setting.add_command(label="Set server", command=self.set_server)
        self.menu_setting.add_command(label="Set path", command=self.set_path)
        self.menu_setting.add_separator()
        self.menu_setting.add_command(label="Exit", command=self.set_exit)
        self.menu.add_cascade(label="Setting", menu=self.menu_setting)

        self.scrollbar_vertical = tkinter.Scrollbar(self.window, orient="vertical")
        self.scrollbar_vertical.pack(side="right", fill="y")
        self.scrollbar_horizontal = tkinter.Scrollbar(self.window, orient="horizontal")
        self.scrollbar_horizontal.pack(side="bottom", fill="x")

        self.text_terminal = tkinter.Text(self.window, wrap="none", xscrollcommand=self.scrollbar_horizontal.set, yscrollcommand=self.scrollbar_vertical.set)
        self.text_terminal.bind("<Key>", lambda e: "break")
        self.text_terminal.pack(side="left", fill="both", expand=True)

        self.scrollbar_vertical.config(command=self.text_terminal.yview)
        self.scrollbar_horizontal.config(command=self.text_terminal.xview)

        self.window.config(menu=self.menu)

        # app setting
        self.target = self.checkFirstExec()
        self.logger = Logger.Logger(self)
        self.fileChecker = self.createFileChecker()
        self.observer = self.fileChecker.observer
        # self.observer.start()
        
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
        return FileChecker(self.target, self.logger, config)
    
    def run(self):
        self.logger.print_log("WATCHING FILE CHANGED...")
        self.window.after(5000, self.run)
    
    def text_print(self, text):
        self.text_terminal.insert(tkinter.END, text+"\n")
        self.text_terminal.see(tkinter.END)

    def set_server(self):
        server = tkinter.simpledialog.askstring("Input", "Input server IP", parent=self.window)
        port = tkinter.simpledialog.askstring("Input", "Input server port", parent=self.window)
        config.setConfig("CLIENT_CONFIG", "server_ip", server)
        config.setConfig("CLIENT_CONFIG", "port", port)

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
        