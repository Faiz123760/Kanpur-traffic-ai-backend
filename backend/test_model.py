import pandas as pd
import joblib
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, "traffic_model.pkl")
COLUMNS_PATH = os.path.join(MODEL_DIR, "model_columns.pkl")

def test_prediction():
    try:
        model = joblib.load(MODEL_PATH)
        model_columns = joblib.load(COLUMNS_PATH)
        print("Model loaded successfully!")
        
        # Test some predictions
        test_cases = [
            {"locality": "Mall Road", "day_type": "weekday", "time_slot": "morning_rush_8am_11am", "weather": "clear"},
            {"locality": "Panki", "day_type": "weekday", "time_slot": "evening_rush_5pm_9pm", "weather": "rainy"},
            {"locality": "Civil Lines", "day_type": "weekend", "time_slot": "afternoon_12pm_5pm", "weather": "clear"}
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            input_data = pd.DataFrame([test_case])
            input_encoded = pd.get_dummies(input_data).reindex(columns=model_columns, fill_value=0)
            
            predicted_speed = model.predict(input_encoded)[0]
            travel_time = (5 / predicted_speed) * 60  # 5km distance
            
            print(f"\nTest Case {i}:")
            print(f"Input: {test_case}")
            print(f"Predicted Speed: {predicted_speed:.2f} km/h")
            print(f"Travel Time for 5km: {travel_time:.1f} minutes")
            
    except FileNotFoundError:
        print("Model files not found. Please run train_model.py first.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_prediction()