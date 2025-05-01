from flask import Flask, jsonify
from flask_cors import CORS
from routes.user_route import user_bp
from routes.habit_route import habit_bp
import os
from flask_cors import CORS
def create_app():
    app = Flask(__name__)
    # Enable CORS for all routes and origins
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # JWT Secret Key - in production, use a secure random key and environment variables
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'my_temporary_secret_key')
    
    # Register blueprints with URL prefixes
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(habit_bp, url_prefix='/api/habits')
    
    # Health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "Server is running"}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)  