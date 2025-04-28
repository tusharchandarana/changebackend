from flask import Blueprint, request, jsonify, current_app
from models.user_model import create_user, find_user_by_email
from werkzeug.security import check_password_hash
import jwt
import datetime
from config import user_collection


user_bp = Blueprint('user_bp', __name__)

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    
    # Validate input
    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing required fields"}), 400
    
    if find_user_by_email(data["email"]):
        return jsonify({"message": "Email already exists"}), 400

    user_id = create_user(data["username"], data["email"], data["password"])
    return jsonify({
        "message": "User created successfully",
        "user_id": str(user_id.inserted_id)
    }), 201

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    
    # Validate input
    if not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing email or password"}), 400
    
    user = find_user_by_email(data["email"])
    
    if user and check_password_hash(user["password"], data["password"]):
        # Generate JWT token
        token = jwt.encode({
            'user_id': str(user["_id"]),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            "message": "Login successful", 
            "user_id": str(user["_id"]),
            "token": token
        }), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

# Function to validate JWT token
def token_required(f):
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Decode token
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(user_id, *args, **kwargs)
    
    return decorated
from bson import ObjectId  # Ensure this import is present

@user_bp.route("/profile", methods=["GET"])
@token_required
def get_profile(user_id):
    user = user_collection.find_one({ "_id": ObjectId(user_id) })  # Corrected line
    if not user:
        return jsonify({"error": "User not found"}), 404

    profile = {
        "username": user["username"],
        "email": user["email"]
    }
    return jsonify({"profile": profile}), 200
