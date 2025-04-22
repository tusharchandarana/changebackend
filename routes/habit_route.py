from flask import Blueprint, request, jsonify
from models.habit_model import create_habit, check_in_habit, get_habits_by_user
from routes.user_route import token_required
from bson import ObjectId

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
        reminder_time=data["reminder_time"]
    )
    return jsonify({"message": "Habit created", "habit_id": str(habit_id.inserted_id)}), 201

@habit_bp.route("/checkin/<habit_id>", methods=["PATCH"])
@token_required
def check_in(user_id, habit_id):
    try:
        # First verify that the habit belongs to the user
        habit = get_habit_by_id(ObjectId(habit_id))
        
        if not habit or habit.get("user_id") != user_id:
            return jsonify({"message": "Unauthorized or habit not found"}), 403
            
        check_in_habit(ObjectId(habit_id))
        return jsonify({"message": "Check-in successful"}), 200
    except Exception as e:
        return jsonify({"message": "Check-in failed", "error": str(e)}), 400

@habit_bp.route("/user", methods=["GET"])
@token_required
def get_user_habits(user_id):
    try:
        habits = get_habits_by_user(user_id)
        return jsonify({"habits": habits}), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve habits", "error": str(e)}), 400

# Helper function to get a single habit by ID
def get_habit_by_id(habit_id):
    from config import habit_collection
    return habit_collection.find_one({"_id": habit_id})