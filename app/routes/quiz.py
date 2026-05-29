
from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models.module import Module
from app.models.course import Course, Enrollment
from app.models.question import Question, QuizAttempt
from app.services.scheduler import select_questions_for_quiz

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/modules/<int:module_id>/quiz")
@login_required
def view(module_id):
    module = Module.query.get_or_404(module_id)
    course = Course.query.get_or_404(module.course_id)

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course.id
    ).first()
    if not enrollment:
        abort(403)

    all_questions = Question.query.join(Module).filter(Module.course_id == course.id).all() 
    all_attempts = QuizAttempt.query.filter_by(user_id=current_user.id).filter(
        QuizAttempt.question_id.in_([q.id for q in all_questions])
    ).all()

    selected = select_questions_for_quiz(
        all_questions=[q.__dict__ for q in all_questions],
        attempts=[a.__dict__ for a in all_attempts],
        current_module_id=module_id,
        n=5,
    ) 
    # BRO WHY ISNT THIS WORKING
    # wrk on tmrw
    selected_ids = [q["id"] for q in selected]
    questions = Question.query.filter(Question.id.in_(selected_ids)).all()

    return render_template("quiz.html", module=module, course=course, questions=questions)


@quiz_bp.route("/api/quiz/answer", methods=["POST"])
@login_required
def answer():
    data = request.get_json()
    question_id = data.get("question_id")
    selected_index = data.get("selected_index")
    response_time_ms = data.get("response_time_ms")

    question = Question.query.get_or_404(question_id)
    correct = selected_index == question.correct_index

    attempt = QuizAttempt(
        user_id=current_user.id,
        question_id=question_id,
        selected_index=selected_index,
        correct=correct,
        response_time_ms=response_time_ms,
    )
    db.session.add(attempt)
    db.session.commit()

    return jsonify({
        "correct": correct,
        "correct_index": question.correct_index,
        "explanation": question.explanation,
    })
