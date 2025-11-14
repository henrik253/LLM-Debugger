
STANDARD_MODEL_NAME = 'google/gemma-3-12b-it' 
# Singleton 
class ModelManager(): 
    _model_manager_instance = None 
    
    def __init__(self): 
       self.user_to_model_name = dict()
       self.user_to_model = dict()

    def __new__(cls, *args, **kwargs): 
        if cls._model_manager_instance == None: 
            cls._model_manager_instance = super().__new__(cls)
        return cls._model_manager_instance

    def load_model(model_name = STANDARD_MODEL_NAME, user_id = 0):
        if not user_to_model_name[user_id]: 
            user_to_model_name[user_id] = []
            user_to_model[user_id] = []
            
        
        if not model_name in user_to_model_name[user_id]:
            user_to_model_name[user_id].append(model_name)
            # Instatiate 

            user_to_model[user_id].append()
            
