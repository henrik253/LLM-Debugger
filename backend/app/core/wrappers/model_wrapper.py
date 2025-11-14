from abc import ABC, abstractmethod  # Import abstract base class utilities

# Base class for model wrappers that define a common interface for interacting with models
class ModelWrapper(ABC):
    def __init__(self, model): 
        self.model = model  # Store the model instance
        self.current_timestep = 0  # Keep track of the current timestep
        self.model_output = ''
        self.current_model_output = ''
        self.current_prompt = '' 
        
    @abstractmethod
    def get_network_output(self, prompt: str): 
        pass  # Return the model output for a given text prompt

    @abstractmethod
    def get_network_architecture(self): 
      pass

    @abstractmethod
    def get_layer_activations(self, layer_index: int, layer_name : str): 
        pass  # Return the activations of a specific layer
    
    @abstractmethod
    def set_layer_activation(self, layer_index: int, layer_name : str, neuron_index: int):
        pass  # Manually set the activation value of a specific neuron
    
    @abstractmethod
    def get_layer_input_param_avgs(self, layer_index: int, layer_name : str):
        pass  # Return average input parameter values for a given layer
    
    @abstractmethod
    def get_layer_input_param_stds(self, layer_index: int, layer_name : str):
        pass  # Return standard deviations of input parameters for a given layer
    
    @abstractmethod
    def get_layer_param(self, layer_index: int, layer_name : str, source_index : int,target_index : int): 
        pass  # Get a specific parameter (e.g., weight) of a neuron input connection
    
    # Set the timestep from which the model information should be retrieved
    def set_timestep(self, index: int):
        self.current_timestep = index

    def layer_has_param(layer):
        pass
