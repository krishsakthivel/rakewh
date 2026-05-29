# this file does too much and i refuse to fix it
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.course import Course, Enrollment
from app.models.module import Module
from app.models.question import Question
from app.services.pdf_parser import parse_pdf
from app.services.course_generator import generate_full_course

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/courses/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    if "pdf" not in request.files:
        flash("no file uploaded.", "error")
        return render_template("upload.html")

    file = request.files["pdf"]
    if not file.filename.endswith(".pdf"):
        flash("only PDF files are accepted.", "error")
        return render_template("upload.html")

    pdf_bytes = file.read()
    chunks = parse_pdf(pdf_bytes)

    if not chunks:
        flash("could not extract text from that PDF. try a different file.", "error")
        return render_template("upload.html")

    course_data = generate_full_course(chunks)

    course = Course(
        user_id=current_user.id,
        title=course_data["metadata"]["title"],
        description=course_data["metadata"]["description"],
        source_filename=file.filename,
    )
    db.session.add(course)
    db.session.flush()

    for mod_data in course_data["modules"]:
        module = Module(
            course_id=course.id,
            order=mod_data["order"],
            title=mod_data["title"],
            explanation=mod_data["explanation"],
            key_concepts=mod_data.get("key_concepts", []),
            teaching_rubric=mod_data.get("teaching_rubric", {}),
        )
        db.session.add(module)
        db.session.flush()

        for q_data in mod_data.get("questions", []):
            question = Question(
                module_id=module.id,
                text=q_data["text"],
                options=q_data["options"],
                correct_index=q_data["correct_index"],
                explanation=q_data.get("explanation", ""),
                concept_tag=q_data.get("concept_tag", ""),
                difficulty=q_data.get("difficulty", 0.5),
            )
            db.session.add(question)

    enrollment = Enrollment(user_id=current_user.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()

    return redirect(url_for("courses.view", course_id=course.id))


@courses_bp.route("/courses/<int:course_id>")
@login_required
def view(course_id):
    course = Course.query.get_or_404(course_id)

    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id, course_id=course_id
    ).first()

    if not enrollment:
        if course.is_public:
            enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
            db.session.add(enrollment)
            db.session.commit()
        else:
            abort(403)

    from app.models.teach_session import TeachSession
    from app.models.question import QuizAttempt
    from app.services.scheduler import get_mastery_scores

    all_questions = Question.query.join(Module).filter(Module.course_id == course_id).all()
    all_attempts = QuizAttempt.query.filter_by(user_id=current_user.id).filter(
        QuizAttempt.question_id.in_([q.id for q in all_questions])
    ).all()

    mastery = get_mastery_scores(
        [q.__dict__ for q in all_questions],
        [a.__dict__ for a in all_attempts],
    )

    completed_module_ids = {
        s.module_id for s in TeachSession.query.filter_by(
            user_id=current_user.id, passed=True
        ).all()
    }

    modules_with_status = []
    for i, module in enumerate(course.modules):
        is_unlocked = i == 0 or course.modules[i - 1].id in completed_module_ids
        modules_with_status.append({
            "module": module,
            "completed": module.id in completed_module_ids,
            "unlocked": is_unlocked,
            "in_progress": is_unlocked and module.id not in completed_module_ids,
        })

    return render_template(
        "course.html",
        course=course,
        modules_with_status=modules_with_status,
        mastery=mastery,
    )


@courses_bp.route("/c/<share_token>")
def shared(share_token):
    course = Course.query.filter_by(share_token=share_token).first_or_404()
    if current_user.is_authenticated:
        return redirect(url_for("courses.view", course_id=course.id))
    return render_template("shared_preview.html", course=course)
