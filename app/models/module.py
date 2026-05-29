
from app import db
from datetime import datetime


class Module(db.Model):
    __tablename__ = "modules"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    key_concepts = db.Column(db.JSON, default=list)
    teaching_rubric = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship("Question", backref="module", lazy=True)
    teach_sessions = db.relationship("TeachSession", backref="module", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "order": self.order,
            "title": self.title,
            "explanation": self.explanation,
            "key_concepts": self.key_concepts,
        }
