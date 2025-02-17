from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from config.database import DatabaseConfig
from base import configure_routes
from asgiref.wsgi import WsgiToAsgi
from config.cloudinary_config import configure_cloudinary
from utils import run_async

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configure Cloudinary
    configure_cloudinary()
    
    # Initialize database
    db_config = DatabaseConfig()
    app.db = run_async(db_config.connect())
    
    # Configure routes
    configure_routes(app)
    
    return app

# Create app instance
app = create_app()

# Create ASGI app
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    app.run(debug=True)