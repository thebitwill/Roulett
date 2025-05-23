# webapp/__init__.py
from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration (e.g., secret key)
    # For sessions to work, a SECRET_KEY is needed.
    # In a real app, this should be a strong, random, and secret value.
    app.config['SECRET_KEY'] = os.urandom(24).hex() 
    
    # Construct the absolute path to the database within the roulette_game directory
    # Assuming run.py (and thus the project root) is one level above roulette_game
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app.config['DATABASE_PATH'] = os.path.join(project_root, 'roulette_game', 'roulette_game.db')
    
    # Import and register routes
    from . import routes
    app.register_blueprint(routes.main_bp) # Using a simple blueprint for now

    # Test if the database path is correct and the DB exists
    # (This is just for early diagnostics)
    if not os.path.exists(app.config['DATABASE_PATH']):
        print(f"WARNING from webapp/__init__.py: Database not found at {app.config['DATABASE_PATH']}")
    else:
        print(f"INFO from webapp/__init__.py: Database confirmed at {app.config['DATABASE_PATH']}")


    return app
