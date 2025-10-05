from src.models.base import BaseModel

class Favorite(BaseModel):
    user_id: str
    request_id: str
    created_at: str
    
    @property
    def pk(self):
        return f"USER#{self.user_id}"
    
    @property
    def sk(self):
        return f"FAVORITE#{self.request_id}"