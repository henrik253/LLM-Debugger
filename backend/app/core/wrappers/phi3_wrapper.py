from backend.app.core.wrappers.model_wrapper import ModelWrapper  # Import the abstract base class
from layer_type import LayerType 

# Wrapper class for the Phi-3 model that implements all abstract methods from ModelWrapper
class Phi3Wrapper(ModelWrapper): 
    def __init__(self, model):
        super().__init__(model)  # Initialize the base ModelWrapper with the model

    def get_network_output(self, prompt: str):
        # Compute and return the model output for the given prompt
        pass

    def get_summarized_layers(self) -> dict[list[int],list]:
        pass

    def get_layer_activations(self, layer_index: int):
        # Return the activations of the specified layer
        pass

    def set_layer_activation(self, layer_index: int, neuron_index: int):
        # Set or modify the activation value of a specific neuron
        pass

    def get_layer_input_param_avgs(self, layer_index: int):
        # Return average input parameter values for the given layer
        pass

    def get_layer_input_param_stds(self, layer_index: int):
        # Return standard deviations of input parameters for the given layer
        pass

    def get_layer_param(self, layer_index: int, neuron_index: int, input_index: int):
        # Get a specific parameter (e.g., weight) of a neuron’s input connection
        pass

    def set_layer_param(self, layer_index: int, neuron_index: int, input_index: int, param_value: float):
        # Set a specific parameter (e.g., weight) in the model to a new value
        pass
