# This file makes the models directory a Python package
# It can be left empty or used to expose specific modules/functions

from models.habit_model import create_habit, check_in_habit
from models.user_model import create_user, find_user_by_email

__all__ = [
    'create_habit', 
    'check_in_habit',
    'create_user',
    'find_user_by_email'
]