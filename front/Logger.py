import logging
from datetime import datetime

class Logger:
    def __init__(self, _gui):
         self.set_config()
         self.gui = _gui

    def print_log(self, text):
        logging.info(text)
        #self.gui.text_print("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "+ text)

    def print_log_server(self, type, status, data):
        logging.info("-------- HTTP --------")
        if type:
            logging.info(type)
        if status:
            logging.info(status)
        if data:
            logging.info(data)
        logging.info("----------------------")
        
    def print_file_list(self, _list):
        logging.info("[")
        for li in _list:
            dics_keys = li.keys()
            logging.info("  {")
            for key in dics_keys:
                logging.info("    %s : %s" %(key, li[key]))
            logging.info("  }")
        logging.info("]")
        
    def set_config(self):
        logging.basicConfig(
            format='[%(asctime)s] %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
        )