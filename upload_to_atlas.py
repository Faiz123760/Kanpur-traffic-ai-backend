import json
import os
from pymongo import MongoClient

# 🌐 ATLAS CONNECTION
ATLAS_URI = "mongodb+srv://faiz47532_db_user:kvvsu53VZljKp0Da@cluster0.qcn9eor.mongodb.net/?appName=Cluster0"
DB_NAME = "kanpur_trafficdb"

def upload_data():
    client = None
    try:
        print(f"Connecting to MongoDB Atlas...")
        client = MongoClient(ATLAS_URI)
        db = client[DB_NAME]
        
        # 1. Upload Traffic Patterns
        print("Loading local traffic patterns...")
        with open('kanpur_traffic_profile.json', 'r') as f:
            data = json.load(f)
        
        collection = db['traffic_patterns']
        
        # Clear existing data in Atlas to avoid duplicates
        print("Clearing 'traffic_patterns' in Atlas...")
        collection.delete_many({})
        
        print(f"Uploading {len(data)} localities to Atlas...")
        collection.insert_many(data)
        print("SUCCESS: Traffic patterns uploaded successfully.")

        # 2. Re-trigger Seeding for Training Data
        print("\nNote: You should also run 'python process_and_seed.py' after updating it with the Atlas URI to populate training data.")
        
    except Exception as e:
        print(f"ERROR during upload: {e}")
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    upload_data()
