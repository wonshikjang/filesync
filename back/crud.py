from sqlalchemy import func
from sqlalchemy.orm import Session
from model import FileData
import schema



def get_list(db: Session):
    return db.query(FileData).all()


def get_record(db: Session, id: str):
    return db.query(FileData).filter(FileData.id == id).first()


def create_record(db: Session, data: schema.BaseFileData):
    db_record = FileData(**data.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def delete_record(db: Session, id: str):
    db_record = get_record(db, id)
    if db_record:
        db.delete(db_record)
        db.commit()
        return 1
    else:
        return -1


def update_record(db: Session, db_record: schema.ReadFileData, body: schema.BaseFileData):
    req = body.dict()
    for key, value in req.items():
        setattr(db_record, key, value)
    db.commit()

    return db_record