# backend/app/api/deps.py

from app.db.database import get_db# backend/app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.core.config import settings
from app.core import security
from app.db.database import get_db
from app.db import models
from app.crud import crud_user
from app.schemas import token as token_schema

# This scheme tells FastAPI where to look for the token (in the Authorization header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login/access-token")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    Dependency to get the current user from a JWT token.
    1. Decodes the token.
    2. Validates the token data.
    3. Fetches the user from the database.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Decode the JWT to get the payload
       
        # Extract the email from the payload's 'sub' (subject) field
        token_data = token_schema.TokenData(email=payload.get("sub"))
    except (JWTError, ValidationError):
        # If the token is invalid or expired, raise an error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch the user from the database using the email from the token
    user = crud_user.get_user_by_email(db, email=token_data.email)
    
    if not user:
        # If a user with that email doesn't exist (e.g., account was deleted)
        raise HTTPException(status_code=404, detail="User not found")
        
    return user