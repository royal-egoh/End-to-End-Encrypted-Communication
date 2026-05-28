from pydantic import BaseModel, ConfigDict, EmailStr, model_validator, Field
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., max_length=20)
    password: str = Field(..., min_length=6)
    public_key: str = Field(...)
    
class UserResponse(BaseModel):
    id: int
    username: str
    public_key: str
    
    model_config  = ConfigDict(from_attributes=True)
    
class MessageCreate(BaseModel):
    recipient_id: int = Field(...)
    content_for_sender: str = Field(...)
    content_for_receiver: str = Field(...)
    
    
class MessageResponse(BaseModel):
    sender_id: int
    recipient_id: int
    timestamp:datetime
    content_for_sender: str 
    content_for_receiver: str
    
    model_config  = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    
    model_config  = ConfigDict(from_attributes=True)
    

    
