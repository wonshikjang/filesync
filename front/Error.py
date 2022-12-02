class AlreadyChecked(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class NeedToUpdated(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg