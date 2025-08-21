# backend/app/routes/user_routes.py (Fully Updated with Password Reset)

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
import shutil
from jose import jwt, JWTError
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

# Local imports
from .. import models
from ..database import get_db
from ..schemas import user_schema, token_schema
from ..auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from ..config import settings # Settings import karna zaroori hai

router = APIRouter(
    prefix="/users",
    tags=["Users & Authentication"]
)

# --- DIRECTORY SETUP FOR PROFILE PHOTOS ---
UPLOAD_DIRECTORY = "./uploaded_images"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# --- EMAIL CONFIGURATION FOR PASSWORD RESET ---
conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
)

# --- Authentication Endpoints ---

@router.post("/register", response_model=user_schema.UserShow, status_code=status.HTTP_201_CREATED)
def register_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    """Registers a new user. Passwords are automatically hashed."""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")
    
    hashed_pwd = hash_password(user.password)
    new_user = models.User(
        full_name=user.full_name, 
        email=user.email, 
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/token", response_model=token_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs in a user and returns a JWT access token."""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# --- NAYA CODE: PASSWORD RESET ENDPOINTS ---

@router.post("/forgot-password")
async def forgot_password(
    request: user_schema.PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handles the logic for sending a password reset email."""
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        # For security, we don't reveal if an email is registered or not.
        return {"message": "If an account with that email exists, a reset link has been sent."}

    token = create_access_token(data={"sub": user.email})
    reset_link = f"{settings.FRONTEND_URL}/Reset_Password?token={token}"

    message = MessageSchema(
        subject="[Senior Health App] Password Reset Request",
        recipients=[user.email],
        body=f"""
            <p>Hello {user.full_name or 'user'},</p>
            <p>You requested a password reset. Please click the link below to set a new password:</p>
            <p><a href="{reset_link}">Reset Your Password</a></p>
            <p>This link will expire in {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes.</p>
            <p>If you did not request this, please ignore this email.</p>
        """,
        subtype="html"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    return {"message": "If an account with that email exists, a reset link has been sent."}

@router.post("/reset-password")
def reset_password(
    request: user_schema.PasswordReset,
    db: Session = Depends(get_db)
):
    """Resets the user's password using a valid token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token. It may be invalid or expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(request.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception

    user.hashed_password = hash_password(request.new_password)
    db.add(user)
    db.commit()

    return {"message": "Password has been reset successfully."}

# --- NAYA CODE KHATAM ---


# --- User Profile Management Endpoints ---

@router.get("/me", response_model=user_schema.UserShow)
def read_current_user_profile(current_user: models.User = Depends(get_current_user)):
    """Gets the profile information of the currently logged-in user."""
    return current_user

@router.put("/me", response_model=user_schema.UserShow)
def update_current_user_profile(
    user_update: user_schema.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Updates the profile information (name, DOB, address) of the current user."""
    update_data = user_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.put("/me/photo", response_model=user_schema.UserShow)
def upload_profile_photo(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    file: UploadFile = File(...)
):
    """Uploads or updates the profile photo for the current user."""
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"user_{current_user.id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    url_compatible_path = file_path.replace("\\", "/")
    current_user.profile_picture_url = url_compatible_path

    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.put("/me/password")
def update_current_user_password(
    password_update: user_schema.PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Updates the password for the currently logged-in user."""
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")
    
    new_hashed_password = hash_password(password_update.new_password)
    current_user.hashed_password = new_hashed_password
    
    db.add(current_user)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user_account(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes the account of the currently logged-in user."""
    if current_user.profile_picture_url and os.path.exists(current_user.profile_picture_url):
        os.remove(current_user.profile_picture_url)
        
    db.delete(current_user)
    db.commit()
    return None