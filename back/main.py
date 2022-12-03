import os, os.path
import uuid
import re
import time
import json
import asyncio
import websockets
from typing import List
from fastapi import FastAPI,Depends, UploadFile, WebSocket, HTTPException, WebSocketDisconnect
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_204_NO_CONTENT
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT
import model, crud, schema
from database import engine
from database import SessionLocal
from fastapi.responses import FileResponse, HTMLResponse
from fastapi_socketio import SocketManager
# import nest_asyncio
# nest_asyncio.apply()

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
    
    filenames = os.listdir("./static")
    print(filenames)
    for filename in filenames:
        if re.match(f"{id}\..*?", filename):
            os.remove(f"./static/{filename}")
    
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
async def upload_file(file: UploadFile):
    UPLOAD_DIR = "./static"  # 이미지를 저장할 서버 경로

    content = await file.read()
    filename = file.filename
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    return {"filename": filename}

@app.get("/download/file/{file_id}")
async def download_file(file_id:str, db: Session = Depends(get_db)):
    db_record = crud.get_record(db, file_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record

@app.get("/static/{file_name}")
async def download_file(file_name:str, db: Session = Depends(get_db)):
    return FileResponse(f"./static/{file_name}")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    manager = ConnectionManager()
    await manager.connect(websocket)
    
    while True:
        try:
            print("hlhl")
            time.sleep(10)
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: ", websocket)
            await manager.broadcast(f"Client #{websocket.client} says: ")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(f"Client #{websocket.client} left the chat")
