import json
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "kanpur_trafficdb"
COLLECTION_NAME = "traffic_patterns"

def import_data():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Load the JSON data
        with open('kanpur_traffic_profile.json', 'r') as f:
            data = json.load(f)

        # Clear existing data
        collection.delete_many({})
        
        # Insert data
        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)

        print(f"[SUCCESS] Imported {len(data)} patterns into {COLLECTION_NAME}")
        client.close()
    except Exception as e:
        print(f"[ERROR] Failed to import data: {e}")

if __name__ == "__main__":
    import_data()
