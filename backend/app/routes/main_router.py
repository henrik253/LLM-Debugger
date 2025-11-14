from fastapi import APIRouter
from models.item import Item
from services.item_service import save_item

router = APIRouter(prefix="/items", tags=["Items"])

@router.post("/")
def create_item(item: Item):
    save_item(item)
    return {"status": "saved", "item": item}