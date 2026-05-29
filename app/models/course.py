
from app import db
from datetime import datetime
import secrets


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    source_filename = db.Column(db.String(255))
    share_token = db.Column(db.String(32), unique=True, default=lambda: secrets.token_urlsafe(16))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)

    modules = db.relationship("Module", backref="course", lazy=True, order_by="Module.order")
    enrollments = db.relationship("Enrollment", backref="course", lazy=True)

    def to_dict(self, user_id=None):
        enrollment = None # TS SO PEAK 
        if user_id:
            enrollment = Enrollment.query.filter_by(course_id=self.id, user_id=user_id).first()

        completed = sum(1 for m in self.modules if enrollment and self._module_complete(m.id, user_id))
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "share_token": self.share_token,
            "module_count": len(self.modules),
            "completed_modules": completed,
            "created_at": self.created_at.isoformat(),
        }

    def _module_complete(self, module_id, user_id):
        from app.models.teach_session import TeachSession
        return TeachSession.query.filter_by(
            module_id=module_id, user_id=user_id, passed=True
        ).first() is not None


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "course_id"),)
