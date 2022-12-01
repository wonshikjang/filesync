import logging
from datetime import datetime

class logger:
    def __init__(self, _gui):
         self.set_config()
         self.gui = _gui

    def print_log(self, text):
        logging.info(text)
        self.gui.text_print("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "+ text)

    def set_config(self):
        logging.basicConfig(
            format='[%(asctime)s] %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
        )