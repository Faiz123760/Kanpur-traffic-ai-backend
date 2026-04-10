import pandas as pd
import joblib
import sys
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, "traffic_model.pkl")
COLUMNS_PATH = os.path.join(MODEL_DIR, "model_columns.pkl")

def make_prediction(location, day_type, time_slot, weather):
    try:
        model = joblib.load(MODEL_PATH)
        model_columns = joblib.load(COLUMNS_PATH)
    except FileNotFoundError:
        return {"error": "Model files not found. Please ensure the 'models' folder exists and contains the .pkl files."}

    input_data = pd.DataFrame({
        'locality': [location],
        'day_type': [day_type],
        'time_slot': [time_slot],
        'weather': [weather]
    })
    
    input_encoded = pd.get_dummies(input_data).reindex(columns=model_columns, fill_value=0)

    predicted_speed = model.predict(input_encoded)[0]

    if predicted_speed > 0:
        travel_time = (5 / predicted_speed) * 60
    else:
        travel_time = float('inf') 

    result = {
        "predicted_speed_kmh": round(predicted_speed, 2),
        "travel_time_minutes": round(travel_time) if travel_time != float('inf') else "N/A"
    }
    
    return result

if __name__ == '__main__':
    if len(sys.argv) == 5:
        location_arg = sys.argv[1]
        day_type_arg = sys.argv[2]
        time_slot_arg = sys.argv[3]
        weather_arg = sys.argv[4]
        
        prediction = make_prediction(location_arg, day_type_arg, time_slot_arg, weather_arg)
        
        print(json.dumps(prediction))
    else:
        error_message = {"error": f"Invalid number of arguments. Expected 4, but got {len(sys.argv) - 1}."}
        print(json.dumps(error_message))
