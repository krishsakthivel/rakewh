# teach session model, where the real work gets judged
from app import db
from datetime import datetime


class TeachSession(db.Model):
    __tablename__ = "teach_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    transcript = db.Column(db.JSON, default=list)
    rubric_coverage = db.Column(db.JSON, default=dict)
    coverage_score = db.Column(db.Float, default=0.0)
    passed = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "module_id": self.module_id,
            "transcript": self.transcript,
            "rubric_coverage": self.rubric_coverage,
            "coverage_score": self.coverage_score,
            "passed": self.passed,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
