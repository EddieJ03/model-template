from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
import pandas as pd
import lightgbm as lgb
import mlflow.lightgbm
import os
import sys

# adds the parent directory to path in case you have sibling folders with stuff you need
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# List of required environment variables
REQUIRED_ENV_VARS = ["MLFLOW_TRACKING_URI", "AZURE_STORAGE_CONNECTION_STRING"]

# Check if all required variables are set
missing_vars = [var for var in REQUIRED_ENV_VARS if var not in os.environ]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# If all required variables are set, proceed
print("All required environment variables are set.")

mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
mlflow.lightgbm.autolog()

# Prepare training data
df = pd.read_csv('data/iris.csv')
flower_names = {'Setosa': 0, 'Versicolor': 1, 'Virginica': 2}


X = df[['sepal.length', 'sepal.width', 'petal.length', 'petal.width']]
y = df['variety'].map(flower_names)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

train_data = lgb.Dataset(X_train, label=y_train)

def main():
    mlflow.set_experiment({{cookiecutter.project_slug}})
    with mlflow.start_run() as run:
        # Train model
        params = {
            "objective": "multiclass",
            "num_class": 3, 
            "learning_rate": 0.2,
            "metric": "multi_logloss",
            "feature_fraction": 0.8,
            "bagging_fraction": 0.9,
            "seed": 42,
        }
        
        model = lgb.train(params, train_data, valid_sets=[train_data])

        # Evaluate model
        y_proba = model.predict(X_test)
        y_pred = y_proba.argmax(axis=1)
        
        loss = log_loss(y_test, y_proba)
        acc = accuracy_score(y_test, y_pred)
    
        mlflow.log_metrics({
            'log loss': loss,
            'accuracy score': acc
        })

if __name__ == "__main__":
    main()