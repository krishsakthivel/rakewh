# module view, just renders the reading
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models.module import Module
from app.models.course import Course, Enrollment
from app.models.teach_session import TeachSession

modules_bp = Blueprint("modules", __name__)

# ezezez
@modules_bp.route("/modules/<int:module_id>")
@login_required
def view(module_id):
    module = Module.query.get_or_404(module_id)
    course = Course.query.get_or_404(module.course_id)

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course.id
    ).first()
    if not enrollment:
        abort(403)

    completed_ids = {
        s.module_id for s in TeachSession.query.filter_by(
            user_id=current_user.id, passed=True
        ).all()
    }

    sorted_modules = sorted(course.modules, key=lambda m: m.order)
    module_index = next(i for i, m in enumerate(sorted_modules) if m.id == module_id)

    if module_index > 0:
        prev_module = sorted_modules[module_index - 1]
        if prev_module.id not in completed_ids:
            abort(403)

    completed = module.id in completed_ids
    teach_session = TeachSession.query.filter_by(
        user_id=current_user.id, module_id=module_id, passed=True
    ).first()

    return render_template(
        "module.html",
        module=module,
        course=course,
        completed=completed,
        teach_session=teach_session,
    )
