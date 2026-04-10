import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import time

MONGO_URI = "mongodb+srv://faiz47532_db_user:kvvsu53VZljKp0Da@cluster0.qcn9eor.mongodb.net/?appName=Cluster0"
DB_NAME = "kanpur_trafficdb" 
COLLECTION_NAME = "training_data"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, 'models')
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

MODEL_PATH = os.path.join(MODEL_DIR, "traffic_model.pkl")
COLUMNS_PATH = os.path.join(MODEL_DIR, "model_columns.pkl")


def main():
    print("--- Starting the ADVANCED Model Training Pipeline for Kanpur ---")

    print(f"\n[INFO] Loading data from MongoDB collection: '{COLLECTION_NAME}'...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        data = list(collection.find())
        df = pd.DataFrame(data)
        client.close()

        if df.empty:
            print("[ERROR] No data found in MongoDB. Please run the process_and_seed.py script for Kanpur first.")
            return
            
        print(f"[SUCCESS] Loaded {len(df)} records from the database.")
        
    except Exception as e:
        print(f"[ERROR] Failed to load data from MongoDB. Please ensure it is running. Details: {e}")
        return

    print("\n[INFO] Performing advanced feature engineering...")

    target_variable = 'speed_kmh'
    categorical_features = ['locality', 'day_type', 'weather', 'time_slot']
    
    X = df.drop(columns=[target_variable, '_id'])
    y = df[target_variable]
    
    X_encoded = pd.get_dummies(X, columns=categorical_features)
    
    print(f"[SUCCESS] Data prepared. Number of features after encoding: {X_encoded.shape[1]}")
    
    joblib.dump(X_encoded.columns, COLUMNS_PATH)
    print(f"[INFO] Model feature columns saved to: {COLUMNS_PATH}")

    print("\n[INFO] Starting hyperparameter tuning to find the best model...")
    
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

    param_grid = {
        'n_estimators': [100, 200, 300, 500],
        'max_features': ['sqrt', 'log2'],
        'max_depth': [10, 20, 30, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    rf = RandomForestRegressor(random_state=42)
    rf_random_search = RandomizedSearchCV(estimator=rf, param_distributions=param_grid, 
                                          n_iter=50, cv=3, verbose=1, random_state=42, n_jobs=-1)

    start_time = time.time()
    rf_random_search.fit(X_train, y_train)
    end_time = time.time()

    print(f"[SUCCESS] Hyperparameter tuning completed in {end_time - start_time:.2f} seconds.")
    print("\nBest parameters found:")
    print(rf_random_search.best_params_)

    best_model = rf_random_search.best_estimator_

    print("\n[INFO] Evaluating the best model on the test data...")
    
    predictions = best_model.predict(X_test)
    
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print("\n--- FINAL MODEL EVALUATION RESULTS ---")
    print(f"  -> Mean Absolute Error (MAE): {mae:.2f} km/h")
    print(f"  -> R-squared (R²) Score: {r2:.2%}")
    print("------------------------------------")
    
    joblib.dump(best_model, MODEL_PATH)
    print(f"\n[SUCCESS] Final trained model saved to: {MODEL_PATH}")
    print("\n--- Training Pipeline Finished ---")

if __name__ == "__main__":
    main()