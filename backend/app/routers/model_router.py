from fastapi import APIRouter, HTTPException
from backend.app.core.managers.model_manager import ModelManager

router = APIRouter(prefix="/model", tags=["Model"])

model_manager = ModelManager()

@router.post("/load")
def instatiate_model(model: str):
    status = model_manager.load_wrapper(model)
    return {"status": status, "model": model}


@router.get("/architecture")
def get_model_architecture(model: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {"architecture": wrapper.get_network_architecture_to_json()}


@router.get("/generate")
def get_model_output(model: str, prompt: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {"generated": wrapper.get_model_output(prompt)}


@router.get("/layer/{layer_name}/activations")
def get_layer_activations(model: str, layer_name: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {"activations": wrapper.get_layer_activations(layer_name)}


@router.post("/layer/{layer_name}/activation/{neuron_index}/set")
def set_layer_activation(model: str, layer_name: str, neuron_index: int, value: float):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    wrapper.set_layer_activation(layer_name, neuron_index, value)
    return {}


@router.get("/layer/{layer_name}/input-avgs")
def get_layer_input_param_avgs(model: str, layer_name: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {"input_avgs": wrapper.get_layer_input_param_avgs(layer_name)}


@router.get("/layer/{layer_name}/input-stds")
def get_layer_input_param_stds(model: str, layer_name: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {"input_stds": wrapper.get_layer_input_param_stds(layer_name)}


@router.get("/layer/{layer_name}/neuron/{neuron_index}/param/{input_index}")
def get_layer_param(model: str, layer_name: str, neuron_index: int, input_index: int):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {"param": wrapper.get_layer_param(layer_name, neuron_index, input_index)}


@router.post("/layer/{layer_name}/neuron/{neuron_index}/param/{input_index}/set")
def set_layer_param(model: str, layer_name: str, neuron_index: int, input_index: int, param_value: float):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    wrapper.set_layer_param(layer_name, neuron_index, input_index, param_value)
    return {}


@router.post("/timestep/set")
def set_timestep(model: str, index: int):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    wrapper.set_timestep(index)
    return {"timestep": index}
