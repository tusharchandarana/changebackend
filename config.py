import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
# MongoDB connection
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/habit_tracker')
mongo_client = MongoClient(mongo_uri)

# Get database
db = mongo_client.get_database()

# Collections
user_collection = db.users
habit_collection = db.habits

user_id='680bdff53594ac777b56c273';

def generate_check_ins_and_logs(start_date, end_date, probability=0.6):
    current_date = start_date
    check_ins = []
    check_in_logs = []
    while current_date <= end_date:
        if random.random() < probability:
            check_in_date = current_date.strftime("%Y-%m-%d")
            check_ins.append(check_in_date)
            check_in_logs.append({
                "date": check_in_date,
                "time": current_date.strftime("%H:%M:%S"),
                "note": "Completed successfully"
            })
        current_date += timedelta(days=1)
    return check_ins, check_in_logs

# Define the date range for two months
start_date = datetime(2025, 3, 1)
end_date = datetime(2025, 4, 30)

# Dummy habits
dummy_habits = [
    {
        "user_id": user_id,
        "habit_name": "Morning Walk",
        "frequency": "daily",
        "goal": "30 days",
        "reminder_time": "06:00 AM",
        "created_at": datetime(2025, 2, 28),
        "check_ins": [],
        "check_in_logs": [],
        "active": True
    },
    {
        "user_id": user_id,
        "habit_name": "Meditation",
        "frequency": "daily",
        "goal": "15 days",
        "reminder_time": "07:00 AM",
        "created_at": datetime(2025, 3, 1),
        "check_ins": [],
        "check_in_logs": [],
        "active": True
    }
]

# Generate check-ins and logs for each habit
for habit in dummy_habits:
    check_ins, check_in_logs = generate_check_ins_and_logs(start_date, end_date)
    habit["check_ins"] = check_ins
    habit["check_in_logs"] = check_in_logs

# Insert habits into the database
result = habit_collection.insert_many(dummy_habits)

# Output the inserted IDs
print(f"Inserted Habit IDs: {result.inserted_ids}")