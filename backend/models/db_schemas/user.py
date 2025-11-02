from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    """User schema in database."""
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("username", 1)],
                "name": "username_index_1",
                "unique": True
            },
            {
                "key": [("email", 1)],
                "name": "email_index_1",
                "unique": True
            }
        ]

    
