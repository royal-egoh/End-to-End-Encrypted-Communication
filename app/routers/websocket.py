from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from app.services import verify_token, save_message, get_current_user
from app.schemas import MessageCreate, MessageResponse
import json
from app.services import create_user, verify_password, create_token, get_current_user, save_message, get_message_history
from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas import UserCreate, UserResponse, MessageCreate, MessageResponse, Token
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User, Message

router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
        
    def connect(self, websocket: WebSocket, user_id:int):
        self.active_connections[user_id] = websocket
        
    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)
    
    async def send_to_user(self, user_id, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    payload = verify_token(token=token)
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        await websocket.close(code=1008)
        return    
    await websocket.accept()
    manager.connect(user.id, websocket)
    try:
        while True:
            # text = await websocket.receive_text()
            # data = json.loads(text)
            # message_create = MessageCreate.model_validate(data)
            # message = save_message(message_create, current_user=user, db=db)
            # message_response = MessageResponse.model_validate(message)
            # await manager.send_to_user(message_create.recipient_id, message_response.json())    
            text = await websocket.rece

# 1. verify token → get username → look up user in DB
    # 2. accept the connection
    # 3. register: manager.connect(user.id, websocket)
    # 4. try:
    #       while True:
    #           receive text
    #           parse JSON → MessageCreate
    #           save_message(message, current_user, db)
    #           forward: manager.send_to_user(recipient_id, text)
    #    except WebSocketDisconnect:
    #       manager.disconnect(user.id)
    