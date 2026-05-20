from app.services import create_user, verify_password, create_token, get_current_user
from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas import UserCreate, UserResponse, MessageCreate, MessageResponse, Token
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User, Message

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{username}/public_key")
async def get_public_key(username: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"username": user.username, "public_key": user.public_key}
