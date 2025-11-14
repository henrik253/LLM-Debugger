from fastapi import APIRouter
from managers.model_manager import ModelManager
from wrappers.model_wrapper import ModelWrapper

router = APIRouter(prefix="/model", tags=["Model"])

model_manager = ModelManager() 


@router.post("/load")
def instatiate_model(model: str):
    status = model_manager.load_wrapper(model)
    return {"status": status, "model": model }

@router.get("/architecture")
def get_model_architecture(model: str): 
  try: 
    wrapper = model_manager.get_wrapper(model)
  except Exception as e: 
    return {'status': 'ERROR'}

  return {'status' : 'SUCCESS', 'architecture' : wrapper.get_network_architecture_to_json()}


