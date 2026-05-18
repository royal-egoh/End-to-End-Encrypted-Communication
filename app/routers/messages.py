from app.services import create_user,get_message_history, verify_password,get_current_user, create_token, get_current_user
from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas import UserCreate, UserResponse, MessageCreate, MessageResponse, Token
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User, Message

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.get("/history/{username}")
async def get_history(username: str ,db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    other_user = db.query(User).filter(User.username == username).first()
    if not other_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    messages = get_message_history(current_user=current_user, recipient_id=other_user.id, db=db)
    return messages