import os
import socket
import webbrowser
from threading import Timer
from flask import Flask

from database.connection import db
from routes.main import main_bp
from routes.api import api_bp
from models.question import QuestionConfig

def get_local_ip():
    """
    Get local network IP address to display for phone connectivity on the same Wi-Fi.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

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
    
    # Create tables & seed default questions
    with app.app_context():
        db.create_all()
        seed_default_questions()
        
    return app

def seed_default_questions():
    """
    Seeds default habit tracking questions into database on first launch.
    """
    from models.question import QuestionConfig
    if QuestionConfig.query.first() is None:
        defaults = [
            QuestionConfig(
                id=1,
                question_text="Did you study today?",
                description="Did you spend time reading books, completing courses, learning new tech stacks, or expanding your academic base?",
                short_title="Studied today",
                placeholder="What did you study today? Any insights...",
                is_inverted=False
            ),
            QuestionConfig(
                id=2,
                question_text="Did you work on a project today?",
                description="Did you write code, design layout assets, architect databases, refactor styles, or make functional progress on a personal project?",
                short_title="Worked on project",
                placeholder="What project features did you build or plan?",
                is_inverted=False
            ),
            QuestionConfig(
                id=3,
                question_text="Did you exercise today?",
                description="Did you engage in physical activity like gym workouts, yoga, running, cycling, swimming, or brisk walking for at least 15-30 minutes?",
                short_title="Exercised",
                placeholder="Describe your workout, duration, or physical activity...",
                is_inverted=False
            ),
            QuestionConfig(
                id=4,
                question_text="Did you apply for a job or improve your career today?",
                description="Did you submit applications, update portfolio items, polish your resume/CV, practice system design/coding tests, or network on LinkedIn?",
                short_title="Career / Job building",
                placeholder="Mention job search efforts, CV tweaks, or networking milestones...",
                is_inverted=False
            ),
            QuestionConfig(
                id=5,
                question_text="Did you waste time on social media today?",
                description="Did you spend time scrolling YouTube shorts, Instagram reels, TikTok, or Twitter feeds instead of focusing on core goals?",
                short_title="Avoided social media",
                placeholder="How did you control distractions today? Screen limits...",
                is_inverted=True
            )
        ]
        for q in defaults:
            db.session.add(q)
        db.session.commit()

def open_browser():
    """
    Utility to open the system's default browser to LifeTrack.
    """
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    app = create_app()
    
    # Only open browser once in Flask main process (skip reloading sub-processes)
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        print("[Launcher] Starting LifeTrack...")
        local_ip = get_local_ip()
        print("=========================================================")
        print("   TO TRACK ON YOUR PHONE (Must be on same Wi-Fi):")
        print(f"   http://{local_ip}:5000/")
        print("=========================================================")
        Timer(1.5, open_browser).start()
        
    app.run(host='0.0.0.0', port=5000, debug=True)
