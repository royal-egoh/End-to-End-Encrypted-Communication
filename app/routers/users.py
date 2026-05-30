from app.services import create_user, verify_password, create_token, get_current_user
from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas import UserCreate, UserResponse, MessageCreate, MessageResponse, Token
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User, Message
from sqlalchemy import or_, and_

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{username}/public_key")
async def get_public_key(username: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user.id, "username": user.username, "public_key": user.public_key}


@router.get("/{username}/conversations")
async def get_conversations(username: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # last_message = db.query(Message).filter(or_(Message.sender_id == user.id,
    #                                             Message.recipient_id == user.id)).order_by(Message.timestamp.desc()).first()
    sent_messages = db.query(Message).filter(
        Message.sender_id == user.id).all()
    received_messages = db.query(Message).filter(
        Message.recipient_id == user.id).all()
    conversations = set()
    if sent_messages:
        for message in sent_messages:
            conversations.add(message.recipient_id)
    if received_messages:
        for message in received_messages:
            conversations.add(message.sender_id)

    conversations_users = []

    for id_s in conversations:
        other_user = db.query(User).filter(User.id == id_s).first()

        if other_user:

            last_message = db.query(Message).filter(
                or_(
                    and_(
                        Message.sender_id == user.id,
                        Message.recipient_id == id_s
                    ),
                    and_(
                        Message.sender_id == id_s,
                        Message.recipient_id == user.id
                    )
                )
            ).order_by(Message.timestamp.desc()).first()

            preview = ""
            if last_message:
                if last_message.sender_id == user.id:
                    preview = last_message.content_for_sender
                else:
                    preview = last_message.content_for_recipient

            conversations_users.append({
                "id": id_s,
                "username": other_user.username,
                "last_message": preview
            })
    # print(f"HERE!!!!!{last_message.content_for_sender[0: 10]}")
    # print(f"{last_message.content_for_recipient[0: 10]}")
    return conversations_users
