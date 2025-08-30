# backend/app/api/v1/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.crud import crud_user
from app.schemas import user as user_schema

router = APIRouter()

# This endpoint remains for registration (creating a new user)
@router.post("/", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: user_schema.UserCreate
):
    """
    Create a new user.
    """
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    user = crud_user.create_user(db=db, user=user_in)
    return user


# --- NEW ENDPOINT TO GET CURRENT USER'S PROFILE ---
@router.get("/me", response_model=user_schema.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get current user's profile.
    """
    # The dependency already fetches the user, so we just return it.
    return current_user


# --- NEW ENDPOINT TO UPDATE CURRENT USER'S PROFILE ---
@router.put("/me", response_model=user_schema.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: user_schema.UserUpdate,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Update current user's profile.
    """
    user = crud_user.update_user(db, db_user=current_user, user_in=user_in)
    return user