from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import verify_token, save_message
from app.schemas import MessageCreate, MessageResponse
from app.models import User
import json

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
        
    def connect(self, user_id:int, websocket: WebSocket):
        self.active_connections[user_id] = websocket
        
    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)
    
    async def send_to_user(self, user_id, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

manager = ConnectionManager() #
