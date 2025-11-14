from .model_wrapper import ModelWrapper
from transformers import AutoTokenizer, AutoModelForCausalLM
import json

class Gemma3Wrapper(ModelWrapper):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b")
        self.model = AutoModelForCausalLM.from_pretrained("google/gemma-2b", device_map="auto")
        super().__init__(self.model)
    

    def get_layer_activations(self, layer_index: int, layer_name: str):
        print(f"Dummy: get_layer_activations called for layer {layer_name} ({layer_index})")

    def set_layer_activation(self, layer_index: int, layer_name: str, neuron_index: int):
        print(f"Dummy: set_layer_activation called for layer {layer_name} ({layer_index}), neuron {neuron_index}")

    def get_layer_input_param_avgs(self, layer_index: int, layer_name: str):
        print(f"Dummy: get_layer_input_param_avgs called for layer {layer_name} ({layer_index})")

    def get_layer_input_param_stds(self, layer_index: int, layer_name: str):
        print(f"Dummy: get_layer_input_param_stds called for layer {layer_name} ({layer_index})")

    def get_layer_param(self, layer_index: int, layer_name: str, source_index: int, target_index: int):
        print(f"Dummy: get_layer_param called for layer {layer_name} ({layer_index}), source {source_index}, target {target_index}")

    def layer_has_param(self, layer):
        print(f"Dummy: layer_has_param called for layer {layer}")

    # Optional override: already defined in base class, but you can keep for debug
    def set_timestep(self, index: int):
        self.current_timestep = index
        print(f"Dummy: set_timestep called with index {index}")
