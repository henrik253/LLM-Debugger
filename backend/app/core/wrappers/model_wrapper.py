import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import gc

class ModelWrapper:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map="cuda")
        self.model_name = model_name
        self.current_timestep = 0
        self.model_output = ''
        self.current_model_output = ''
        self.current_prompt = ''
        self.max_new_tokens = 20

    def get_model_output(self, prompt: str):
        if prompt == self.current_prompt:
            return self.model_output

        self.current_prompt = prompt
        input_ids = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**input_ids,max_new_tokens = self.max_new_tokens)
        self.model_output = self.tokenizer.decode(outputs[0])
        return self.model_output

    def get_layer_names(self):
      return [name for name, _ in self.model.named_modules()]

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
        return summary

    def get_layer_activations(self, layer_name: str):
      activations = {}

      # Find the layer/module
      module = dict(self.model.named_modules()).get(layer_name)
      if module is None:
          raise ValueError(f"Layer '{layer_name}' not found in model")

      # Hook to capture activations
      def hook_fn(_module, _input, output):
          if isinstance(output, tuple):
              output = output[0]
          activations["value"] = output.detach().cpu()

      hook = module.register_forward_hook(hook_fn)

      # Encode the prompt
      prompt = self.current_prompt or ""
      device = next(self.model.parameters()).device
      encoded = self.tokenizer(prompt, return_tensors="pt").to(device)
      input_ids = encoded["input_ids"]

      # Current timestep = desired length for prompt + generated tokens
      total_length = self.current_timestep

      # If timestep is 0 or too small, use full prompt only
      if total_length == 0 or total_length <= input_ids.shape[1]:
          effective_ids = input_ids[:, :max(1, total_length)] # Ensure at least 1 token if total_length is 0 but input_ids is not empty
      else:
          # Need to generate to reach total length
          generate_tokens = total_length - input_ids.shape[1]

          # Generate-only the needed amount
          gen_outputs = self.model.generate(
              input_ids,
              max_new_tokens=generate_tokens,
              do_sample=False,
          )

          effective_ids = gen_outputs  # full sequence: prompt + output

          # Save model output text
          self.model_output = self.tokenizer.decode(
              gen_outputs[0], skip_special_tokens=True
          )

      # Now run full forward pass on the final sequence to capture activations
      with torch.no_grad():
          # Check if effective_ids is empty before passing to model
          if effective_ids.numel() == 0: # Check if the tensor has any elements
              raise ValueError("Effective input IDs are empty, cannot get activations. Ensure a valid prompt and timestep.")
          self.model(input_ids=effective_ids)

      hook.remove()

      if "value" not in activations:
          raise RuntimeError(f"No activations captured for layer '{layer_name}'")

      # Size will be [1, total_length, hidden_size]
      return activations["value"].tolist()

    def get_layer_biases(self, layer_name: str):

        # Find the layer
        module = dict(self.model.named_modules()).get(layer_name)
        if module is None:
            raise ValueError(f"Layer '{layer_name}' not found in model")

        # Find the single bias tensor
        bias_param = None
        for name, param in module.named_parameters():
            if "bias" in name.lower():
                bias_param = param
                break

        if bias_param is None:
            raise RuntimeError(f"Layer '{layer_name}' has no bias parameter")

        tensor = bias_param.detach().cpu()

        # Flatten for finding min/max
        flat = tensor.flatten()

        min_val = flat.min().item()
        max_val = flat.max().item()

        min_idx = flat.argmin().item()
        max_idx = flat.argmax().item()

        # Since it's a vector, unravel index just returns [index]
        return {
            "bias": tensor.tolist(),
            "min_value": min_val,
            "min_index": min_idx,
            "max_value": max_val,
            "max_index": max_idx,
        }


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


    def set_neuron_bias(self, layer_name: str, neuron_index: int, bias_value: float):
        with torch.no_grad():
            for name, param in self.model.named_parameters():
                if name == f"{layer_name}.bias":

                    if neuron_index >= param.shape[0]:
                        raise ValueError(
                            f"Neuron index {neuron_index} out of range "
                            f"for bias of size {param.shape[0]}"
                        )

                    # Set the bias value
                    param[neuron_index] = bias_value
                    return  # Done!

        # If we finished the loop without returning:
        raise ValueError(f"Layer '{layer_name}'.bias not found or has no bias")

    def reset_model_params(self):
      del self.model
      gc.collect()
      self.model = AutoModelForCausalLM.from_pretrained(self.model_name, device_map="cuda")
      torch.cuda.empty_cache()

    def set_timestep(self, index: int):
        self.current_timestep = index

    def set_max_new_tokens(self,max_new_tokens : int): 
        self.max_new_tokens = max_new_tokens