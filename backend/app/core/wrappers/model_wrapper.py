import json
from transformers import AutoTokenizer, AutoModelForCausalLM


class ModelWrapper():
    def __init__(self,model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
        self.current_timestep = 0  # Keep track of the current timestep
        self.model_output = ''
        self.current_model_output = ''
        self.current_prompt = ''

    def get_network_output(self, prompt: str):
        if prompt == self.current_prompt:
            return self.model_output

        self.current_prompt = prompt
        input_ids = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**input_ids)
        self.model_output = self.tokenizer.decode(outputs[0])
        return self.model_output

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

    def get_network_output(self, prompt: str):
        pass  # Return the model output for a given text prompt

    def get_summarized_layers(self) -> dict[list[int], list]:
        pass  # Return a list describing the types of layers in the model

    def get_layer_activations(self, layer_index: int):
        pass  # Return the activations of a specific layer

    def set_layer_activation(self, layer_index: int, neuron_index: int):
        pass  # Manually set the activation value of a specific neuron

    def get_layer_input_param_avgs(self, layer_index: int):
        pass  # Return average input parameter values for a given layer

    def get_layer_input_param_stds(self, layer_index: int):
        pass  # Return standard deviations of input parameters for a given layer

    def get_layer_param(self, layer_index: int, neuron_index: int, input_index: int):
        pass  # Get a specific parameter (e.g., weight) of a neuron input connection

    def set_layer_param(self, layer_index: int, neuron_index: int, input_index: int, param_value: float):
        pass  # Set a specific parameter (e.g., weight) to a new value

    def set_timestep(self, index: int):
        self.current_timestep = index
