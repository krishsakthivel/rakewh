# i wrote this at 2am and it works so we're not touching it
from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.module import Module
from app.models.course import Course, Enrollment
from app.models.teach_session import TeachSession
from app.services.pip_chat import get_pip_response, evaluate_coverage

teach_bp = Blueprint("teach", __name__)


@teach_bp.route("/modules/<int:module_id>/teach")
@login_required
def view(module_id):
    module = Module.query.get_or_404(module_id)
    course = Course.query.get_or_404(module.course_id)

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course.id
    ).first()
    if not enrollment:
        abort(403)

    session = TeachSession.query.filter_by(
        user_id=current_user.id, module_id=module_id, passed=False
    ).order_by(TeachSession.started_at.desc()).first()

    if not session:
        session = TeachSession(user_id=current_user.id, module_id=module_id)
        db.session.add(session)
        db.session.commit()

    return render_template(
        "teach.html",
        module=module,
        course=course,
        session=session,
    )


@teach_bp.route("/api/teach/<int:session_id>/chat", methods=["POST"])
@login_required
def chat(session_id):
    session = TeachSession.query.get_or_404(session_id)

    if session.user_id != current_user.id:
        abort(403)

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    module = Module.query.get_or_404(session.module_id)

    transcript = list(session.transcript or [])
    transcript.append({"role": "user", "content": user_message})

    pip_reply = get_pip_response(
        module_title=module.title,
        rubric=module.teaching_rubric,
        transcript=transcript,
    )

    transcript.append({"role": "assistant", "content": pip_reply})
    session.transcript = transcript

    coverage_result = evaluate_coverage(module.teaching_rubric, transcript)
    session.rubric_coverage = coverage_result.get("coverage", {})
    session.coverage_score = coverage_result.get("coverage_score", 0.0)

    coverage_passed = coverage_result.get("passed", False)
    all_covered = (
        len(session.rubric_coverage) > 0
        and all(session.rubric_coverage.values())
    )
    threshold = module.teaching_rubric.get("minimum_coverage_threshold", 0.75)
    score_passed = session.coverage_score >= threshold

    if coverage_passed or (score_passed and all_covered):
        session.passed = True
        session.completed_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "pip_reply": pip_reply,
        "rubric_coverage": session.rubric_coverage,
        "coverage_score": session.coverage_score,
        "passed": session.passed,
        "gaps": coverage_result.get("gaps", []),
    })
