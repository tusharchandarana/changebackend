from bson.objectid import ObjectId
from datetime import datetime
from config import habit_collection

def create_habit(user_id, name, frequency, goal, reminder_time=None):
    """Create a new habit for a user"""
    habit = {
        "user_id": user_id,
        "habit_name": name,
        "frequency": frequency,
        "goal": goal,
        "reminder_time": reminder_time,
        "created_at": datetime.now(),
        "check_ins": [],
        "check_in_logs": [],
        "active": True
    }
    
    result = habit_collection.insert_one(habit)
    return str(result.inserted_id)

def check_in_habit(habit_id):
    """Record a check-in for a habit"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Add today's date to the check_ins array if not already present
    result = habit_collection.update_one(
        {"_id": habit_id, "check_ins": {"$ne": today}},
        {"$push": {"check_ins": today}}
    )
    
    return result.modified_count > 0

def get_habit_by_id(habit_id):
    """Get a single habit by ID"""
    return habit_collection.find_one({"_id": habit_id})

def get_habits_by_user(user_id):
    """Get all habits for a user"""
    cursor = habit_collection.find({"user_id": user_id})
    habits = []
    
    for habit in cursor:
        # Convert ObjectId to string for JSON serialization
        habit["_id"] = str(habit["_id"])
        habits.append(habit)
    
    return habits

def update_habit(habit_id, updates):
    """Update a habit's details"""
    result = habit_collection.update_one(
        {"_id": habit_id},
        {"$set": updates}
    )
    return result.modified_count > 0

def delete_habit(habit_id):
    """Delete a habit or mark it as inactive"""
    result = habit_collection.update_one(
        {"_id": habit_id},
        {"$set": {"active": False}}
    )
    return result.modified_count > 0