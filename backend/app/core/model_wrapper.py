from abc import ABC, abstractmethod

class ModelWrapper():
    def __init__(self,model): 
        self.model = model 
        self.current_timestep = 0

    @abstractmethod
    def get_network_output(self,prompt : str): 
        pass
    
    @abstractmethod
    def get_layer_types(self):
            pass


    def set_timestep(self,index : int):
        self.current_timestep = index
    
   


  
