from fastapi import APIRouter, Depends
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/db-structure")
def get_db_structure(db: Session = Depends(get_db)):
    inspector = inspect(db.bind)
    structure = {}
    
    for table_name in inspector.get_table_names():
        structure[table_name] = {
            "columns": inspector.get_columns(table_name),
            "primary_keys": inspector.get_primary_keys(table_name),
            "foreign_keys": inspector.get_foreign_keys(table_name)
        }
    
    return structure 