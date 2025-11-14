from .model_wrapper import ModelWrapper
from transformers import AutoTokenizer, AutoModelForCausalLM
import json

class Gemma3Wrapper(ModelWrapper):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b")
        self.model = AutoModelForCausalLM.from_pretrained("google/gemma-2b", device_map="auto")
        super().__init__(self.model)
    
    def get_network_output(self, prompt: str):
        if prompt == self.current_prompt:
            return self.model_output
        
        self.current_prompt = prompt
        input_ids = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**input_ids)
        self.model_output = self.tokenizer.decode(outputs[0])
        return self.model_output

    # generated
    def get_network_architecture_to_json(self):
      """
      Converts a PyTorch model architecture into a nested JSON string
      with the same information as print_model_layers.
      """
      model_dict = {}
      total_params = 0
      unique_layers = set()

      for name, module in self.model.named_modules():
          # Skip the root module
          if name == "":
              continue

          layer_info = {
              "type": module.__class__.__name__,
              "parameters": {}
          }

          has_params = False
          for param_name, param in module.named_parameters(recurse=False):
              has_params = True
              num_params = param.numel()
              total_params += num_params
              unique_layers.add(module.__class__.__name__)
              
              layer_info["parameters"][param_name] = {
                  "shape": list(param.shape),
                  "num_params": num_params
              }

          if not has_params:
              layer_info["parameters"] = {
                  "-": {"shape": None, "num_params": 0}
              }
              unique_layers.add(module.__class__.__name__)

          # Insert into nested dict based on layer name
          keys = name.split(".")
          current = model_dict
          for k in keys[:-1]:
              if k not in current:
                  current[k] = {}
              current = current[k]
          current[keys[-1]] = layer_info

      summary = {
          "total_params": total_params,
          "unique_layers": list(unique_layers),
          "layers": model_dict
      }

      return json.dumps(summary, indent=4)

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
