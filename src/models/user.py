from typing import List, Optional
from datetime import datetime
from src.models.base import BaseModel

class User(BaseModel):
    user_id: str
    email: str
    username: str
    hashed_password: str
    is_active: bool = True
    created_at: str
    
    @property
    def pk(self):
        return f"USER#{self.user_id}"
    
    @property 
    def sk(self):
        return f"PROFILE#{self.user_id}"