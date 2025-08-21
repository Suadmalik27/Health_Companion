# /backend/app/schemas/tip_schema.py (Updated)

from pydantic import BaseModel
from typing import Optional

class TipBase(BaseModel):
    content: str
    category: Optional[str] = "General"

class TipCreate(TipBase):
    pass

# --- NAYA SCHEMA: Tip ko update karne ke liye ---
class TipUpdate(BaseModel):
    content: Optional[str] = None
    category: Optional[str] = None
# --- NAYA SCHEMA KHATAM ---

class TipShow(TipBase):
    id: int
    class Config:
        from_attributes = True