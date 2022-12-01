from pydantic import BaseModel
from datetime import datetime

class BaseFileData(BaseModel):
    id: str
    name: str
    path: str
    md5: str

    class Config:
        orm_mode = True

class ReadFileData(BaseFileData):
    create_time: datetime
    update_time: datetime