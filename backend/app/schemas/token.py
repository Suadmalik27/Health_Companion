# backend/app/schemas/token.py

from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """

    Schema for the token response after a successful login.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for the data contained within a JWT token.
    This will hold the user's identifier (e.g., email).
    """
    email: Optional[str] = None