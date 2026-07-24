import os
import webbrowser
from threading import Timer
from flask import Flask

from database.connection import db
from routes.main import main_bp
from routes.api import api_bp

def create_app():
    app = Flask(__name__)
    
    # Path configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(base_dir, 'instance')
    
    # Configure SQLite Database
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(instance_path, 'database.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Ensure directories exist
    os.makedirs(instance_path, exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'exports'), exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'reports'), exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'backups'), exist_ok=True)
    
    # Initialize connection
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
    return app

def open_browser():
    """
    Utility to open the system's default browser to LifeTrack.
    """
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    app = create_app()
    
    # Only open browser once in Flask main process (skip reloading sub-processes)
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        print("[Launcher] Starting LifeTrack. Auto-opening browser...")
        Timer(1.5, open_browser).start()
        
    app.run(host='127.0.0.1', port=5000, debug=True)
