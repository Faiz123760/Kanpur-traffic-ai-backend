import pandas as pd
import numpy as np
from pymongo import MongoClient
import random
from datetime import datetime, timedelta

MONGO_URI = "mongodb+srv://faiz47532_db_user:kvvsu53VZljKp0Da@cluster0.qcn9eor.mongodb.net/?appName=Cluster0"
DB_NAME = "kanpur_trafficdb"
COLLECTION_NAME = "traffic_patterns"

def generate_training_data():
    """Generate training data from MongoDB traffic patterns"""
    print("Connecting to MongoDB...")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Load all traffic patterns
        traffic_patterns = list(collection.find())
        
        if not traffic_patterns:
            print("No traffic patterns found in MongoDB. Please import your data first.")
            return None
            
        print(f"Loaded {len(traffic_patterns)} traffic patterns from MongoDB")
        
        training_data = []
        
        # Weather conditions for variability
        weather_conditions = ['clear', 'rainy', 'foggy', 'cloudy']
        
        # Generate multiple samples for each pattern
        for pattern in traffic_patterns:
            locality = pattern['locality_name']
            
            # Generate weekday data
            for time_slot, speed_percent in pattern['patterns']['weekday'].items():
                for weather in weather_conditions:
                    # Convert percentage to actual speed (assuming 40km/h is 100%)
                    base_speed = speed_percent * 0.4  # Convert percentage to km/h
                    
                    # Apply weather modifiers
                    weather_modifiers = {
                        'clear': 1.0,
                        'cloudy': 0.9,
                        'rainy': 0.7,
                        'foggy': 0.6
                    }
                    
                    actual_speed = base_speed * weather_modifiers[weather]
                    
                    # Add some random variation
                    actual_speed += random.uniform(-2, 2)
                    actual_speed = max(5, min(60, actual_speed))  # Keep realistic bounds
                    
                    training_data.append({
                        'locality': locality,
                        'day_type': 'weekday',
                        'time_slot': time_slot,
                        'weather': weather,
                        'speed_kmh': actual_speed
                    })
            
            # Generate weekend data
            for time_slot, speed_percent in pattern['patterns']['weekend'].items():
                for weather in weather_conditions:
                    base_speed = speed_percent * 0.4  # Convert percentage to km/h
                    
                    weather_modifiers = {
                        'clear': 1.0,
                        'cloudy': 0.9,
                        'rainy': 0.7,
                        'foggy': 0.6
                    }
                    
                    actual_speed = base_speed * weather_modifiers[weather]
                    actual_speed += random.uniform(-2, 2)
                    actual_speed = max(5, min(60, actual_speed))
                    
                    training_data.append({
                        'locality': locality,
                        'day_type': 'weekend',
                        'time_slot': time_slot,
                        'weather': weather,
                        'speed_kmh': actual_speed
                    })
        
        df = pd.DataFrame(training_data)
        print(f"Generated {len(df)} training samples")
        
        # Save to MongoDB for future use
        training_collection = db['training_data']
        training_collection.delete_many({})  # Clear existing data
        training_collection.insert_many(df.to_dict('records'))
        
        print("Training data saved to MongoDB collection 'training_data'")
        
        client.close()
        return df
        
    except Exception as e:
        print(f"Error generating training data: {e}")
        return None

def main():
    print("--- Generating Training Data from Traffic Patterns ---")
    df = generate_training_data()
    
    if df is not None:
        print("\nSample of generated data:")
        print(df.head())
        print(f"\nTotal samples: {len(df)}")
        
        # Show some statistics
        print(f"\nSpeed statistics:")
        print(f"Min: {df['speed_kmh'].min():.2f} km/h")
        print(f"Max: {df['speed_kmh'].max():.2f} km/h")
        print(f"Mean: {df['speed_kmh'].mean():.2f} km/h")
        print(f"Std: {df['speed_kmh'].std():.2f} km/h")

if __name__ == "__main__":
    main()