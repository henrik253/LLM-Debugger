import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class ModelWrapper:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
        self.current_timestep = 0
        self.model_output = ''
        self.current_model_output = ''
        self.current_prompt = ''

    def get_model_output(self, prompt: str):
        if prompt == self.current_prompt:
            return self.model_output

        self.current_prompt = prompt
        input_ids = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**input_ids)
        self.model_output = self.tokenizer.decode(outputs[0])
        return self.model_output

    def get_network_architecture_to_json(self):
        model_dict = {}
        total_params = 0
        unique_layers = set()

        for name, module in self.model.named_modules():
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

    def get_layer_activations(self, layer_name: str):
        activations = {}

        module = dict(self.model.named_modules()).get(layer_name, None)
        if module is None:
            raise ValueError(f"Layer '{layer_name}' not found in model")

        def hook_fn(_module, _input, output):
            if isinstance(output, tuple):
                output = output[0]
            activations["value"] = output.detach().cpu().tolist()

        hook = module.register_forward_hook(hook_fn)

        prompt = self.current_prompt or ""
        encoded = self.tokenizer(prompt, return_tensors="pt").to(next(self.model.parameters()).device)
        input_ids = encoded["input_ids"]

        timestep = self.current_timestep
        if timestep > 0:
            timestep = min(timestep, input_ids.shape[1])
            input_ids = input_ids[:, :timestep]

        with torch.no_grad():
            self.model(input_ids=input_ids)

        hook.remove()

        if "value" not in activations:
            raise RuntimeError(f"No activations captured for layer '{layer_name}'")

        return activations["value"]

    def set_layer_activation(self, layer_name: str, neuron_index: int, value: float):
        if self.current_prompt == "":
            raise ValueError("No prompt available. Run get_model_output() at least once.")

        module = dict(self.model.named_modules()).get(layer_name, None)
        if module is None:
            raise ValueError(f"Layer '{layer_name}' not found in model")

        timestep = int(self.current_timestep)
        enc = self.tokenizer(self.current_prompt, return_tensors="pt").to(next(self.model.parameters()).device)
        input_ids = enc["input_ids"]

        if timestep < 1 or timestep > input_ids.shape[1]:
            raise ValueError(f"Timestep {timestep} out of range for input length {input_ids.shape[1]}")

        input_ids = input_ids[:, :timestep]

        def hook_fn(_module, _input, output):
            if isinstance(output, tuple):
                output = output[0]
            output = output.clone()
            output[:, -1, neuron_index] = value
            return output

        hook = module.register_forward_hook(hook_fn)
        with torch.no_grad():
            self.model(input_ids=input_ids)
        hook.remove()

    def get_layer_input_param_avgs(self, layer_name: str):
        layer = dict(self.model.named_modules()).get(layer_name, None)
        if layer is None:
            raise ValueError(f"Layer '{layer_name}' not found in model")

        params = dict(layer.named_parameters())
        if "weight" not in params:
            raise ValueError(f"Layer '{layer_name}' has no 'weight' parameter")

        W = params["weight"].detach().cpu()
        W_flat_per_neuron = W.view(W.shape[0], -1)
        neuron_avgs = W_flat_per_neuron.mean(dim=1)
        return neuron_avgs.tolist()

    def get_layer_input_param_stds(self, layer_name: str):
        layer = dict(self.model.named_modules()).get(layer_name, None)
        if layer is None:
            raise ValueError(f"Layer '{layer_name}' not found in model")

        params = dict(layer.named_parameters())
        if "weight" not in params:
            raise ValueError(f"Layer '{layer_name}' has no 'weight' parameter")

        W = params["weight"].detach().cpu()
        W_flat_per_neuron = W.view(W.shape[0], -1)
        neuron_stds = W_flat_per_neuron.std(dim=1)
        return neuron_stds.tolist()

    def get_layer_param(self, layer_name: str, neuron_index: int, input_index: int):
        pass

    def set_layer_param(self, layer_name: str, neuron_index: int, input_index: int, param_value: float):
        pass

    def set_timestep(self, index: int):
        self.current_timestep = index
