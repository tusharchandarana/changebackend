from config import habit_collection
from datetime import datetime
from bson import ObjectId

def create_habit(user_id, name, frequency, goal, reminder_time):
    habit = {
        "user_id": user_id,
        "habit_name": name,
        "frequency": frequency,  # daily / weekly / monthly
        "goal": goal,  # int
        "reminder_time": reminder_time,  # e.g. "08:00"
        "check_ins": [],  # to track daily check-ins
        "created_at": datetime.now()
    }
    return habit_collection.insert_one(habit)

def check_in_habit(habit_id):
    today = datetime.now().strftime("%Y-%m-%d")
    result = habit_collection.update_one(
        {"_id": habit_id},
        {"$addToSet": {"check_ins": today}}
    )
    if result.modified_count == 0:
        # Check if the habit exists
        habit = habit_collection.find_one({"_id": habit_id})
        if not habit:
            raise Exception("Habit not found")
        # If habit exists but wasn't modified, the user might have already checked in today
        if today in habit.get("check_ins", []):
            raise Exception("Already checked in today")
    return result

def get_habits_by_user(user_id):
    cursor = habit_collection.find({"user_id": user_id})
    
    # Convert MongoDB cursor to list and serialize ObjectId fields
    habits = []
    for habit in cursor:
        habit["_id"] = str(habit["_id"])  # Convert ObjectId to string
        habits.append(habit)
    
    return habits