import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

import mlflow
from mlflow.tracking import MlflowClient
from mlflow.sklearn import load_model
from joblib import dump
from config.config import Config


MODEL_PATH = r'../assets/model.pkl'     # Access locally.


class ModelRetriever:
    def __init__(self):
        mlflow.set_tracking_uri("http://localhost:5000")
        self.client = MlflowClient()
    
    
    def get_model_info(self):
        versions = self.client.search_model_versions("")
        production_models = [m for m in versions if m.current_stage == "Production"]
        
        if len(production_models) > 1:
            raise ValueError("There should be only one model in Production stage.")

        if not production_models:
            raise ValueError("No model found in Production stage.")
        
        run = self.client.get_run(production_models[0].run_id)
        model_name = production_models[0].name
        model_metrics = run.data.metrics
        return model_name, model_metrics
    
    
    def retrieve_model(self, model_name):
        model = load_model(f"models:/{model_name}/Production")
        return model

        
    def export_model(self, model):
        dump(model, MODEL_PATH)


if __name__ == "__main__":
    model_retriever = ModelRetriever()
    model_name, model_metrics = model_retriever.get_model_info()
    model = model_retriever.retrieve_model(model_name)
    model_retriever.export_model(model)
    
    print(f"Saved model with name: {model_name} \nand metrics: {model_metrics}")
