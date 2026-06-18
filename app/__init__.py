from flask import Flask

from app.config import Config
from app.extensions import db, migrate


def create_app():
    app = Flask(
        __name__, template_folder="../templates", static_folder="../static"
    )  # Set template and static folder paths

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth_routes import auth_bp

    app.register_blueprint(auth_bp)

    return app
