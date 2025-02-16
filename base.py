from flask import Blueprint, jsonify
from routes.patient import patient_bp
from routes.image import image_bp
from config.database import DatabaseConfig
from utils import get_or_create_eventloop, run_async

def configure_routes(app):
    """Configure all routes and database for the application"""
    
    # Initialize database connection
    db_config = DatabaseConfig()
    
    # Initialize database using the global event loop
    app.db = run_async(db_config.connect())
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        return jsonify({
            'status': 'error',
            'message': str(error),
            'error_type': error.__class__.__name__
        }), 500

    # Register patient blueprint
    app.register_blueprint(patient_bp)

    # Register image blueprint
    app.register_blueprint(image_bp)

    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'status': 'success',
            'message': 'Diabetic Retinopathy API Server',
            'version': '1.0'
        })

    return app