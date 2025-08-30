# backend/app/crud/crud_tip.py (Nayi File)

from sqlalchemy.orm import Session
from app.db import models
from app.schemas import tip as tip_schema
from typing import List, Optional

def create_tip(db: Session, tip: tip_schema.TipCreate) -> models.HealthTip:
    """
    Database mein ek nayi health tip create karta hai.
    
    Args:
        db: The database session.
        tip: The tip data from the TipCreate schema.
        
    Returns:
        The newly created HealthTip object from the database.
    """
    # TipCreate schema se ek database model object banata hai
    db_tip = models.HealthTip(
        tip_text=tip.tip_text,
        category=tip.category
    )
    
    # Naye tip ko session mein add karta hai
    db.add(db_tip)
    
    # Changes ko database mein save (commit) karta hai
    db.commit()
    
    # db_tip object ko database se aayi nayi information (jaise ID) se refresh karta hai
    db.refresh(db_tip)
    
    return db_tip

# --- Naye Functions Yahan Jode Gaye Hain ---

def get_tip_by_id(db: Session, tip_id: int) -> Optional[models.HealthTip]:
    """
    Database se ek specific tip ko uske ID se get karta hai.
    """
    return db.query(models.HealthTip).filter(models.HealthTip.id == tip_id).first()

def get_all_tips(db: Session) -> List[models.HealthTip]:
    """
    Database se saari health tips ko get karta hai.
    """
    return db.query(models.HealthTip).all()

def delete_tip(db: Session, db_tip: models.HealthTip) -> models.HealthTip:
    """
    Database se ek specific tip ko delete karta hai.
    """
    db.delete(db_tip)
    db.commit()
    return db_tip

