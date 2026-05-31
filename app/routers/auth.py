from app.services import create_user, verify_password, create_token
from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas import UserCreate, UserResponse, MessageCreate, MessageResponse, Token
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User, Message

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(user: UserCreate, db:Session = Depends(get_db)):
    new_user = create_user(user, db)
    return new_user

@router.post("/login")
async def login(form:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "encrypted_private_key": user.encrypted_private_key}