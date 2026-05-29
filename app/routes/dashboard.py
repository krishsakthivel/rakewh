# dashboard, dead simple, touch grass
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.course import Course, Enrollment

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def home():
    my_courses = Course.query.filter_by(user_id=current_user.id).order_by(Course.created_at.desc()).all()
    enrolled_ids = [e.course_id for e in Enrollment.query.filter_by(user_id=current_user.id).all()]
    enrolled_courses = Course.query.filter(
        Course.id.in_(enrolled_ids),
        Course.user_id != current_user.id
    ).all()

    return render_template(
        "dashboard.html",
        my_courses=my_courses,
        enrolled_courses=enrolled_courses,
    )
