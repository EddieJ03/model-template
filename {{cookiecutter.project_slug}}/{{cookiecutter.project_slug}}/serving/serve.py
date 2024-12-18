from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import mlflow
import pandas as pd
import os
import sys

# adds the parent directory to path in case you have sibling folders with stuff you need
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import lightgbm as lgb

# List of required environment variables
REQUIRED_ENV_VARS = ["MLFLOW_RUN_ID", "AZURE_STORAGE_CONNECTION_STRING", "MLFLOW_TRACKING_URI"]

# Check if all required variables are set
missing_vars = [var for var in REQUIRED_ENV_VARS if var not in os.environ]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# If all required variables are set, proceed
print("All required environment variables are set.")

app = FastAPI()

model: lgb.Booster = mlflow.lightgbm.load_model(f"runs:/{os.environ['MLFLOW_RUN_ID']}/model")

class FlowerPartSize(BaseModel):
    width: float
    length: float

class PredictRequest(BaseModel):
    petal: FlowerPartSize
    sepal: FlowerPartSize

@app.post('/predict')
def predict(request: PredictRequest):
    X: pd.DataFrame = pd.DataFrame(
        columns=['sepal.length', 'sepal.width', 'petal.length', 'petal.width']
    )
    
    X.loc[len(X)] = [request.sepal.length, request.sepal.width, request.petal.length, request.petal.width]
    
    y_proba = model.predict(X)
    y_pred = y_proba.argmax(axis=1)
    
    return {"flower": int(y_pred[0])}
    

@app.get("/")
def root():
    return {"message": "Hello world"}

def main():
    uvicorn.run(app, host='0.0.0.0', port=os.environ['LISTEN_PORT'])
    
if __name__ == "__main__":
    main()