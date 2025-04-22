# This file makes the routes directory a Python package
# It can be left empty or used to expose specific modules/functions

from routes.habit_route import habit_bp
from routes.user_route import user_bp

__all__ = ['habit_bp', 'user_bp']