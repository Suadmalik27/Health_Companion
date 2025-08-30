# backend/app/schemas/tip.py (Nayi File)

from pydantic import BaseModel, Field
from typing import Optional

# --- Base Schema ---
# Ismein woh common fields hain jo har tip schema mein honge.
class TipBase(BaseModel):
    tip_text: str = Field(..., min_length=10)
    category: Optional[str] = Field("General", max_length=50)


# --- Schema for Creating a Tip ---
# Jab frontend se nayi tip add karne ki request aayegi,
# toh woh is format mein honi chahiye.
class TipCreate(TipBase):
    pass


# --- Schema for Reading/Returning a Tip ---
# Jab API database se ek tip return karega,
# toh woh is format mein hogi (ID ke saath).
class Tip(TipBase):
    id: int

    class Config:
        from_attributes = True
