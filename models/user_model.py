from werkzeug.security import generate_password_hash, check_password_hash
from config import user_collection

def create_user(username, email, password):
    hashed_pw = generate_password_hash(password)
    user = {
        "username": username,
        "email": email,
        "password": hashed_pw
    }
    return user_collection.insert_one(user)

def find_user_by_email(email):
    return user_collection.find_one({"email": email})
