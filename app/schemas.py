from pydantic import BaseModel, ConfigDict, EmailStr, model_validator, Field
from datetime import datetime

class UserCreate(BaseModel):
    password: str = Field(..., min_length=6)
    username: str = Field(..., max_length=20)
    public_key: str = Field(...)
    
class UserResponse(BaseModel):
    id: int
    username: str
    public_key: str
    
    model_config  = ConfigDict(from_attributes=True)
    
class MessageCreate(BaseModel):
    content: str = Field(...)
    recipient_id: int = Field(...)
    
class MessageResponse(BaseModel):
    sender_id: int
    recipient_id: int
    timestamp:datetime
    content: str
    
    model_config  = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    
    model_config  = ConfigDict(from_attributes=True)
    

    
