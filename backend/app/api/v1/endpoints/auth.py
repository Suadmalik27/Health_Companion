# backend/app/api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any
import secrets
from datetime import datetime, timedelta, timezone

from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.schemas import token as token_schema, user as user_schema
from app.utils.email_utils import send_password_reset_email

router = APIRouter()

# ... (login_access_token function remains the same) ...
@router.post("/login/access-token", response_model=token_schema.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# --- NEW FORGOT PASSWORD ENDPOINT ---
@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    email: str = Body(..., embed=True),
    db: Session = Depends(deps.get_db)
):
    """
    Send a password reset email to a user.
    """
    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        # For security, don't reveal if the user exists or not
        print(f"Password reset requested for non-existent user: {email}")
        return {"msg": "If an account with this email exists, a password reset link has been sent."}

    # Generate a secure, URL-safe token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1) # Token is valid for 1 hour
    
    # Store the token in the database
    crud_user.set_password_reset_token(db, db_user=user, token=token, expires_at=expires_at)
    
    # Create the full reset link
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    # Send the email
    send_password_reset_email(recipient_email=email, reset_link=reset_link)
    
    return {"msg": "If an account with this email exists, a password reset link has been sent."}


# --- NEW RESET PASSWORD ENDPOINT ---
@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db)
):
    """
    Reset user's password using a reset token.
    """
    # Find the user by the reset token
    user = db.query(models.User).filter(models.User.reset_password_token == token).first()

    if not user or not user.reset_token_expires_at or user.reset_token_expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired password reset token.")
    
    # Update the user's password
    user.hashed_password = security.get_password_hash(new_password)
    # Invalidate the reset token
    user.reset_password_token = None
    user.reset_token_expires_at = None
    
    db.add(user)
    db.commit()
    
    return {"msg": "Password has been reset successfully."}