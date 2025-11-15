from backend.app.core.wrappers.model_wrapper import ModelWrapper

STANDARD_MODEL_NAME = 'google/gemma-3-12b-it'

class ModelManager:
    _model_manager_instance = None

    def __new__(cls, *args, **kwargs):
        if cls._model_manager_instance is None:
            cls._model_manager_instance = super().__new__(cls)
        return cls._model_manager_instance

    def __init__(self):
        self.user_to_models = dict()

    # Just Refactored using GPT! 
    def load_wrapper(self, model_name=STANDARD_MODEL_NAME, user_id=0):

        if user_id not in self.user_to_models:
            self.user_to_models[user_id] = dict()


        if model_name not in self.user_to_models[user_id]:
            try:
                wrapper = ModelWrapper(model_name)
                self.user_to_models[user_id][model_name] = wrapper
                return 'Instantiated'
            except Exception as e:
                print(f"Exception occurred when instantiating wrapper: {e}")

        return 'Already Instantiated'

    # Generated
    def get_wrapper(self, model_name=STANDARD_MODEL_NAME, user_id=0) -> ModelWrapper:
        if user_id not in self.user_to_models:
            raise Exception(f"No models loaded for user {user_id}")

        if model_name not in self.user_to_models[user_id]:
            raise Exception(f"Wrapper for model '{model_name}' not loaded for user {user_id}")

        return self.user_to_models[user_id][model_name]
