from sqlalchemy import Column, String, VARCHAR, TIMESTAMP,text

from database import Base


class FileData(Base):
    __tablename__ = "file_data"

    id = Column(VARCHAR(36), primary_key=True)
    name = Column(VARCHAR(100), nullable=False)
    path = Column(VARCHAR(100), nullable=False)
    md5 = Column(VARCHAR(32), nullable= False)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )