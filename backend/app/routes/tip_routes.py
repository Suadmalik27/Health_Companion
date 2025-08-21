# /backend/app/routes/tip_routes.py (Fully Updated with Full CRUD)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from typing import List # <--- Yeh import add karein

from .. import models
from ..database import get_db
from ..schemas import tip_schema
from ..auth import get_current_user

router = APIRouter(
    prefix="/tips",
    tags=["Health Tips"]
)

# --- NAYA FUNCTION: Saare tips ki list paane ke liye ---
@router.get("/", response_model=List[tip_schema.TipShow])
def get_all_tips(db: Session = Depends(get_db)):
    """Fetches a list of all health tips from the database."""
    tips = db.query(models.Tip).order_by(models.Tip.id.desc()).all()
    return tips

@router.get("/random", response_model=tip_schema.TipShow)
def get_random_tip(db: Session = Depends(get_db)):
    """Fetches a single random health tip from the database."""
    random_tip = db.query(models.Tip).order_by(func.random()).first()
    if not random_tip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No health tips found.")
    return random_tip

# --- UPDATE KIYA GAYA FUNCTION: Ab tip create karne ke liye login zaroori hai ---
@router.post("/", response_model=tip_schema.TipShow, status_code=status.HTTP_201_CREATED)
def create_tip(
    tip: tip_schema.TipCreate, 
    db: Session = Depends(get_db),
    # Note: Humne is route ko protect kar diya hai. Sirf logged-in user hi tip add kar sakta hai.
    current_user: models.User = Depends(get_current_user) 
):
    """Creates a new health tip in the database. Requires authentication."""
    new_tip = models.Tip(**tip.model_dump())
    db.add(new_tip)
    db.commit()
    db.refresh(new_tip)
    return new_tip

# --- NAYA FUNCTION: Tip ko update karne ke liye ---
@router.put("/{tip_id}", response_model=tip_schema.TipShow)
def update_tip(
    tip_id: int,
    tip_update: tip_schema.TipUpdate, # Iske liye humein schema update karna hoga
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Updates an existing health tip by its ID."""
    tip_query = db.query(models.Tip).filter(models.Tip.id == tip_id)
    db_tip = tip_query.first()

    if not db_tip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tip with id {tip_id} not found")

    update_data = tip_update.model_dump(exclude_unset=True)
    tip_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(db_tip)
    return db_tip

# --- NAYA FUNCTION: Tip ko delete karne ke liye ---
@router.delete("/{tip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tip(
    tip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deletes a health tip by its ID."""
    tip_query = db.query(models.Tip).filter(models.Tip.id == tip_id)
    db_tip = tip_query.first()

    if not db_tip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tip with id {tip_id} not found")

    tip_query.delete(synchronize_session=False)
    db.commit()
    return None