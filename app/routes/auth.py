# the gate. if they get in without the password thats on them
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session as flask_session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

SITE_PASSWORD = os.getenv("SITE_PASSWORD", "")


def gate_required():
    if not SITE_PASSWORD:
        return False
    return not flask_session.get("site_unlocked")


@auth_bp.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        entered = request.form.get("site_password", "").strip()
        if entered == SITE_PASSWORD:
            flask_session["site_unlocked"] = True
            return redirect(url_for("auth.index"))
        else:
            flash("wrong password, try again.", "error")
            return render_template("index.html", gated=True)

    gated = gate_required()
    return render_template("index.html", gated=gated)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if gate_required():
        return redirect(url_for("auth.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("all fields are required.", "error")
            return render_template("signup.html")

        if len(password) < 8:
            flash("password must be at least 8 characters.", "error")
            return render_template("signup.html")

        if User.query.filter_by(email=email).first():
            flash("an account with that email already exists.", "error")
            return render_template("signup.html")

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("dashboard.home"))

    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    if gate_required():
        return redirect(url_for("auth.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("incorrect email or password.", "error")
            return render_template("login.html")

        login_user(user)
        next_page = request.args.get("next")
        return redirect(next_page or url_for("dashboard.home"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.index"))
