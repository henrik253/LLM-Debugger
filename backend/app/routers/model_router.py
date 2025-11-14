from fastapi import APIRouter
from managers.model_manager import ModelManager

router = APIRouter(prefix="/model", tags=["Model"])

@router.post("/")
def instatiate_model(model: str):

    
    return {"status": "loaded", "model": model }
