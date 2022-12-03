import logging
from datetime import datetime

class Logger:
    def __init__(self, _gui):
         self.set_config()
         self.gui = _gui

    def print_log(self, text):
        logging.info(text)
        #self.gui.text_print("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "+ text)

    def print_log_server(self, status, res, data):
        logging.info(status)
        logging.info(res)
        logging.info(data)
        
    def print_file_list(self, _list):
        print("[")
        for li in _list:
            dics_keys = li.keys()
            print("  {")
            for key in dics_keys:
                print("    %s : %s" %(key, li[key]))
            print("  }")
        print("]")
        
    def set_config(self):
        logging.basicConfig(
            format='[%(asctime)s] %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
        )