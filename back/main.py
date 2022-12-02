import os.path
import uuid
from fastapi import FastAPI,Depends, UploadFile
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_204_NO_CONTENT
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT
import model, crud, schema
from database import engine
from database import SessionLocal
from fastapi.responses import FileResponse

model.Base.metadata.create_all(bind=engine)




app = FastAPI()
origins = [
    "http://127.0.0.1:5173",    # 또는 "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post( "/", name="file data 생성",response_model= schema.ReadFileData)
async def create_file_data(req: schema.BaseFileData, db: Session = Depends(get_db)):
    return crud.create_record(db, req)

@app.get("/list", name ="file data list 조회", response_model= list[schema.ReadFileData])
async def read_file_data_list(db: Session = Depends(get_db)):
    db_list = crud.get_list(db)

    return db_list

@app.get(
    "/{id}",
    name="uuid 로 파일데이터 가져오기",
    response_model = schema.ReadFileData
)
async def read_file_data(id: str, db: Session = Depends(get_db)):
    db_record = crud.get_record(db, id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record

@app.delete(
    "/{id}",
    name= "입력 id로 해당하는 파일 데이터 삭제"
)
async def delete_file_data(id:str,db: Session = Depends(get_db)):
    db_api = crud.delete_record(db, id)
    if db_api != 1:
        raise HTTPException(status_code=404, detail="Record not found")
        return -1
    return Response(status_code=HTTP_204_NO_CONTENT)

@app.put(
    "/{id}",
    name="입력 id로 해당하는 파일 데이터 수정",
    description="수정하고자 하는 id의 record 전체 수정, record 수정 데이터가 존재하지 않을시엔 생성",
    response_model=schema.ReadFileData,
)
async def update_file_data(req: schema.BaseFileData, id: str, db: Session = Depends(get_db)):
    db_record = crud.get_record(db, id)
    if db_record is None:
        return crud.create_record(db, req)

    return crud.update_record(db, db_record, req)

@app.post("/file")
async def upload_file(file:UploadFile):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath((__file__))))
    FILE_DIR = os.path.join(BASE_DIR,'static/')
    SERVER_IMG_DIR = os.path.join('http://localhost:8080/','static/')


    """
    UPLOAD_DIR = "./file"

    content = await file.read()
    filename = file.filename
    id = f"{str(uuid.uuid4())}"
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)
    return { "id": id, "name" : filename, "path": UPLOAD_DIR}
    """


@app.post("/photo")
async def upload_photo(file: UploadFile):
    UPLOAD_DIR = "./static"  # 이미지를 저장할 서버 경로

    content = await file.read()
    filename = file.filename
    #filename = f"{str(uuid.uuid4())}.jpg"  # uuid로 유니크한 파일명으로 변경
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    return {"filename": filename}

@app.get("/download/photo/{photo_id}")
async def download_photo(photo_id: str, db: Session = Depends(get_db)):
    file_path = f"./static/{photo_id}"
    return FileResponse(file_path)
