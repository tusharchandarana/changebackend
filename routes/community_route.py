# community_route.py
from flask import Blueprint, request, jsonify
from models.user_model import find_user_by_id
from routes.user_route import token_required
from config import user_collection, habit_collection
from bson import ObjectId

community_bp = Blueprint('community_bp', __name__)

@community_bp.route("/updates", methods=["GET"])
@token_required
def get_community_updates(user_id):
    try:
        # Get users that the current user follows
        current_user = find_user_by_id(user_id)
        following = current_user.get("following", [])
        
        # Get community updates (recent activities from other users)
        updates = []
        
        # Get recent habit completions and new habits
        recent_habits = habit_collection.find({
            "$or": [
                {"user_id": {"$in": following}},  # Activities from followed users
                {"user_id": {"$ne": user_id}}     # Activities from other users
            ]
        }).sort("created_at", -1).limit(10)
        
        for habit in recent_habits:
            user = find_user_by_id(habit["user_id"])
            if not user:
                continue
                
            # Check if this is a new habit or a check-in
            check_ins = habit.get("check_ins", [])
            if len(check_ins) <= 1:
                activity = f"Started a new habit: {habit['habit_name']}"
            else:
                activity = f"Completed {habit['habit_name']}"
            
            updates.append({
                "user_id": str(user["_id"]),
                "username": user["username"],
                "profile_photo": user.get("profile_photo", ""),
                "activity": activity,
                "following": str(user["_id"]) in following
            })
            
        return jsonify({"updates": updates}), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve community updates", "error": str(e)}), 400

@community_bp.route("/follow/<target_user_id>", methods=["POST"])
@token_required
def follow_user(user_id, target_user_id):
    try:
        # Make sure the target user exists
        target_user = find_user_by_id(target_user_id)
        if not target_user:
            return jsonify({"message": "User not found"}), 404
            
        # Add target user to current user's following list
        user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"following": target_user_id}}
        )
        
        return jsonify({"message": "User followed successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Failed to follow user", "error": str(e)}), 400

@community_bp.route("/unfollow/<target_user_id>", methods=["POST"])
@token_required
def unfollow_user(user_id, target_user_id):
    try:
        # Remove target user from current user's following list
        user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"following": target_user_id}}
        )
        
        return jsonify({"message": "User unfollowed successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Failed to unfollow user", "error": str(e)}), 400

# Leaderboard route
@community_bp.route("/leaderboard", methods=["GET"])
@token_required
def get_leaderboard(user_id):
    try:
        # Get all users
        users = list(user_collection.find())
        
        # Calculate streaks for each user
        leaderboard = []
        for user in users:
            # Get all habits for this user
            habits = list(habit_collection.find({"user_id": str(user["_id"])}))
            
            # Calculate the maximum streak among all habits
            max_streak = 0
            for habit in habits:
                check_ins = habit.get("check_ins", [])
                streak = calculate_streak(check_ins)
                max_streak = max(max_streak, streak)
            
            leaderboard.append({
                "user_id": str(user["_id"]),
                "username": user["username"],
                "profile_photo": user.get("profile_photo", ""),
                "streak": max_streak,
                "is_current_user": str(user["_id"]) == user_id
            })
        
        # Sort by streak (descending)
        leaderboard.sort(key=lambda x: x["streak"], reverse=True)
        
        # Return top 10
        return jsonify({"leaders": leaderboard[:10]}), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve leaderboard", "error": str(e)}), 400

# Helper function to calculate streak from check-ins
def calculate_streak(check_ins):
    if not check_ins or len(check_ins) == 0:
        return 0
        
    from datetime import datetime, timedelta
    
    # Sort check-ins by date
    sorted_dates = sorted([datetime.strptime(date, "%Y-%m-%d") for date in check_ins])
    
    # Get today's date
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    # Check if user checked in today or yesterday (streak is still valid)
    last_check_in = sorted_dates[-1].date()
    if last_check_in != today and last_check_in != yesterday:
        return 0  # Streak broken
    
    # Count consecutive days
    streak = 1
    for i in range(len(sorted_dates) - 2, -1, -1):
        current_date = sorted_dates[i].date()
        next_date = sorted_dates[i + 1].date()
        
        # Check if dates are consecutive
        if (next_date - current_date).days == 1:
            streak += 1
        else:
            break  # Streak broken
    
    return streak

# Add helper function to find user by ID
def find_user_by_id(user_id):
    try:
        return user_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return None