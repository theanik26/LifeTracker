from datetime import datetime
from database.connection import db

class DailyLog(db.Model):
    __tablename__ = 'daily_logs'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False, index=True)
    
    # Question 1: Study
    q1_val = db.Column(db.Boolean, nullable=False, default=False)
    q1_note = db.Column(db.Text, nullable=True)
    
    # Question 2: Project work
    q2_val = db.Column(db.Boolean, nullable=False, default=False)
    q2_note = db.Column(db.Text, nullable=True)
    
    # Question 3: Exercise
    q3_val = db.Column(db.Boolean, nullable=False, default=False)
    q3_note = db.Column(db.Text, nullable=True)
    
    # Question 4: Career/Job Search
    q4_val = db.Column(db.Boolean, nullable=False, default=False)
    q4_note = db.Column(db.Text, nullable=True)
    
    # Question 5: Avoid social media wasting time
    q5_val = db.Column(db.Boolean, nullable=False, default=False)
    q5_note = db.Column(db.Text, nullable=True)
    
    # Stats
    score = db.Column(db.Integer, nullable=False, default=0) # 0 to 5
    completed = db.Column(db.Boolean, nullable=False, default=False) # True if score == 5

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'q1_val': self.q1_val,
            'q1_note': self.q1_note or '',
            'q2_val': self.q2_val,
            'q2_note': self.q2_note or '',
            'q3_val': self.q3_val,
            'q3_note': self.q3_note or '',
            'q4_val': self.q4_val,
            'q4_note': self.q4_note or '',
            'q5_val': self.q5_val,
            'q5_note': self.q5_note or '',
            'score': self.score,
            'completed': self.completed
        }

    def __repr__(self):
        return f"<DailyLog {self.date} - Score: {self.score}/5>"
