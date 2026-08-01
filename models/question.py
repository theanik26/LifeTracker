from database.connection import db

class QuestionConfig(db.Model):
    __tablename__ = 'question_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    short_title = db.Column(db.String(50), nullable=False)
    placeholder = db.Column(db.String(255), nullable=True)
    is_inverted = db.Column(db.Boolean, nullable=False, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'description': self.description,
            'short_title': self.short_title,
            'placeholder': self.placeholder,
            'is_inverted': self.is_inverted
        }
