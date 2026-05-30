from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.database import engine, Base
from app.routers import auth, users, messages
from app.routers.websocket import manager
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from app.services import verify_token, save_message
from app.schemas import MessageCreate, MessageResponse
from app.models import User
import json
from fastapi.staticfiles import StaticFiles


app = FastAPI()
Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(messages.router)

# ?Websocket endpoint, issue with apirouter


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
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
            text = await websocket.receive_text()
            data = json.loads(text)

            # heartbeat ping
            if data.get("type") == "ping":
                continue

            message_create = MessageCreate.model_validate(data)
            message = save_message(message_create, current_user=user, db=db)
            message_response = MessageResponse.model_validate(message)
            await manager.send_to_user(message_create.recipient_id, message_response.model_dump_json())
    except WebSocketDisconnect:
        manager.disconnect(user.id)


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse(request, "chat.html")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html")
