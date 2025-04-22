import os
from pymongo import MongoClient

# MongoDB connection
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/habit_tracker')
mongo_client = MongoClient(mongo_uri)

# Get database
db = mongo_client.get_database()

# Collections
user_collection = db.users
habit_collection = db.habits