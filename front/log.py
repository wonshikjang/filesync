import logging

def printLog(text):
    logging.info(text)

def setLogging():
    logging.basicConfig(
        format='[%(asctime)s] %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )