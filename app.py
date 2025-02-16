from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from config.database import DatabaseConfig
from base import configure_routes
from asgiref.wsgi import WsgiToAsgi

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    return app

# Create app instance
app = create_app()

# Configure routes and database
configure_routes(app)

# Create ASGI app
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        asgi_app,
        host='0.0.0.0',
        port=5000,
        workers=4
    )