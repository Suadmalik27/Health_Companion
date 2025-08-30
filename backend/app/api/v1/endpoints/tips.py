# backend/app/api/v1/endpoints/tips.py (Nayi File)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.api import deps
from app.db import models
from app.crud import crud_tip
from app.schemas import tip as tip_schema

router = APIRouter()

# Yeh endpoint admin ya authorized users ke liye ho sakta hai
@router.post("/", response_model=tip_schema.Tip, status_code=status.HTTP_201_CREATED)
def create_new_tip(
    *,
    db: Session = Depends(deps.get_db),
    tip_in: tip_schema.TipCreate,
    # Yahan hum yeh check kar sakte hain ki current user admin hai ya nahi
    # Abhi ke liye, koi bhi logged-in user tip create kar sakta hai
    current_user: models.User = Depends(deps.get_current_user) 
):
    """
    Database mein ek nayi health tip create karta hai.
    """
    if not tip_in.tip_text or len(tip_in.tip_text) < 10:
        raise HTTPException(status_code=400, detail="Tip text must be at least 10 characters long.")
        
    tip = crud_tip.create_tip(db=db, tip=tip_in)
    return tip


@router.get("/", response_model=List[tip_schema.Tip])
def get_all_tips(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Database se saari health tips ko get karta hai.
    """
    return crud_tip.get_all_tips(db)


@router.get("/random", response_model=tip_schema.Tip)
def get_random_tip(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Database se ek random health tip get karta hai.
    Dashboard is endpoint ka istemal karega.
    """
    random_tip = db.query(models.HealthTip).order_by(func.random()).first()
    if not random_tip:
        # Agar database mein koi tip na ho, toh ek default tip bhejna
        return models.HealthTip(id=0, tip_text="Remember to stay hydrated and have a great day!", category="General")
    return random_tip


@router.delete("/{tip_id}", response_model=tip_schema.Tip)
def delete_tip_by_id(
    *,
    db: Session = Depends(deps.get_db),
    tip_id: int,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Ek specific tip ko uske ID se delete karta hai.
    """
    tip_to_delete = crud_tip.get_tip_by_id(db, tip_id=tip_id)
    if not tip_to_delete:
        raise HTTPException(status_code=404, detail="Health tip not found")
        
    # Yahan hum user ke role ko check kar sakte hain (e.g., is_admin)
    # Abhi ke liye, koi bhi logged-in user delete kar sakta hai
    
    deleted_tip = crud_tip.delete_tip(db, db_tip=tip_to_delete)
    return deleted_tip
