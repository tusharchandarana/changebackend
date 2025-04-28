from flask import Blueprint, request, jsonify, current_app
from models.habit_model import create_habit, check_in_habit, get_habits_by_user, get_habit_by_id
from routes.user_route import token_required
from bson import ObjectId
from datetime import datetime
from calendar import monthrange
from config import habit_collection

habit_bp = Blueprint('habit_bp', __name__)



@habit_bp.route("/create", methods=["POST"])
@token_required
def create(user_id):
    data = request.json
    
    # Use the authenticated user_id instead of relying on the request data
    habit_id = create_habit(
        user_id=user_id,
        name=data["habit_name"],
        frequency=data["frequency"],
        goal=data["goal"],
        reminder_time=data.get("reminder_time")  # Using get() to make it optional
    )
    return jsonify({"message": "Habit created", "habit_id": str(habit_id)}), 201

@habit_bp.route("/checkin/<habit_id>", methods=["PATCH"])
@token_required
def check_in(user_id, habit_id):
    try:
        # First verify that the habit belongs to the user
        habit = get_habit_by_id(ObjectId(habit_id))
        
        if not habit or str(habit.get("user_id")) != str(user_id):
            return jsonify({"message": "Unauthorized or habit not found"}), 403
        
        # Check if already checked in today
        today = datetime.now().strftime("%Y-%m-%d")
        if today in habit.get("check_ins", []):
            return jsonify({"message": "Already checked in for today"}), 400
            
        result = check_in_habit(ObjectId(habit_id))
        if result:
            return jsonify({"message": "Check-in successful"}), 200
        else:
            return jsonify({"message": "Check-in failed"}), 400
    except Exception as e:
        return jsonify({"message": "Check-in failed", "error": str(e)}), 400

@habit_bp.route("/user", methods=["GET"])
@token_required
def get_user_habits(user_id):
    try:
        # Debugging information
        current_app.logger.info(f"Fetching habits for user: {user_id}")
        
        # Get all habits for the user
        habits = get_habits_by_user(user_id)
        
        # Return the habits as JSON
        return jsonify({"habits": habits}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching habits: {str(e)}")
        return jsonify({"message": "Failed to retrieve habits", "error": str(e)}), 400

@habit_bp.route("/month/<habit_id>/<year>/<month>", methods=["GET"])
@token_required
def get_monthly_data(user_id, habit_id, year, month):
    try:
        habit = get_habit_by_id(ObjectId(habit_id))
        if not habit or str(habit.get("user_id")) != str(user_id):
            return jsonify({"message": "Unauthorized or habit not found"}), 403
        
        year, month = int(year), int(month)
        monthly_data = get_monthly_check_ins(ObjectId(habit_id), year, month)
        return jsonify({"month_data": monthly_data}), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve data", "error": str(e)}), 400    
    

def get_monthly_check_ins(habit_id, year, month):
    """Fetch check-ins for a specific habit in a given month."""
    habit = habit_collection.find_one({"_id": habit_id}, {"check_ins": 1})
    if not habit:
        return None

    # Get all days in the month
    total_days = monthrange(year, month)[1]
    days = [f"{year}-{month:02d}-{day:02d}" for day in range(1, total_days + 1)]

    # Determine if each day is completed
    check_ins = habit.get("check_ins", [])
    return [{"date": day, "completed": day in check_ins} for day in days]    