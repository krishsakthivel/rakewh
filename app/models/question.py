
from app import db
from datetime import datetime


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    correct_index = db.Column(db.Integer, nullable=False)
    explanation = db.Column(db.Text)
    concept_tag = db.Column(db.String(128))
    difficulty = db.Column(db.Float, default=0.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # frfrfr
    attempts = db.relationship("QuizAttempt", backref="question", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "module_id": self.module_id,
            "text": self.text,
            "options": self.options,
            "concept_tag": self.concept_tag,
        }


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected_index = db.Column(db.Integer, nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    response_time_ms = db.Column(db.Integer)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
