# works on my machine
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///rake.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = int(1.5 * 1024 * 1024)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "sign in to continue"

    from app.routes.auth import auth_bp
    from app.routes.courses import courses_bp
    from app.routes.modules import modules_bp
    from app.routes.quiz import quiz_bp
    from app.routes.teach import teach_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(modules_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(teach_bp)
    app.register_blueprint(dashboard_bp)

    from app.models import user, course, module, question, teach_session

    return app
