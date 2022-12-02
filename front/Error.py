class CustomError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

# try:
#     raise CustomError("hi")
# except CustomError as e:
#     print(e)