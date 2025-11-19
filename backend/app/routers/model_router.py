from fastapi import APIRouter, HTTPException
from backend.app.core.managers.model_manager import ModelManager

router = APIRouter(prefix="/model", tags=["Model"])

model_manager = ModelManager()


@router.post("/load")
def instatiate_model(model: str):
    status = model_manager.load_wrapper(model)
    return {"status": status, "model": model}


@router.post("/reset")
def reset_model(model: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")

    wrapper.reset_model_params()
    return {"status": "reset", "model": model}


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


@router.get("/layers")
def get_layer_names(model: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {"layers": wrapper.get_layer_names()}


@router.get("/activations")
def get_layer_activations(model: str, layer_name: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {"activations": wrapper.get_layer_activations(layer_name)}


@router.get("/biases")
def get_layer_biases(model: str, layer_name: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return wrapper.get_layer_biases(layer_name)


@router.post("/set-neuron-bias")
def set_neuron_bias(model: str, layer_name: str, neuron_index: int, bias_value: float):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")

    wrapper.set_neuron_bias(layer_name, neuron_index, bias_value)
    return {"status": "ok"}


@router.get("/input-avgs")
def get_layer_input_param_avgs(model: str, layer_name: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {"input_avgs": wrapper.get_layer_input_param_avgs(layer_name)}


@router.get("/input-stds")
def get_layer_input_param_stds(model: str, layer_name: str):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")
    return {"input_stds": wrapper.get_layer_input_param_stds(layer_name)}


@router.post("/timestep")
def set_timestep(model: str, index: int):
    try:
        wrapper = model_manager.get_wrapper(model)
    except:
        raise HTTPException(status_code=404, detail="Model not loaded")

    wrapper.set_timestep(index)
    return {"timestep": index}

@router.post("/max-new-tokens")
def set_max_new_tokens(model: str,max_new_tokens: int):
  try: 
    wrapper = model_manager.get_wrapper(model)
  except: 
    raise HTTPException(status_code=404, detail="Model not loaded")
  
  wrapper.set_max_new_tokens(max_new_tokens)
  return {{"max_new_tokens": max_new_tokens}}
