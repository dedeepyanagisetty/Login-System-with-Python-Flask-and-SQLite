from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app,
)

from app.models.account import Account
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


# Health check endpoint
# Then:
# http://127.0.0.1:5001/health
@auth_bp.route("/health", methods=["GET"])
def health():
    return {"status": "UP", "service": "login-system"}, 200


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    msg = ""  # So four spaces needed and tab pressed emans its four spaces defaLT TAKEN IN PYTHON

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        success, account, msg = AuthService.authenticate_user(
            username=username,
            password=password,
            secret_key=current_app.config["SECRET_KEY"],
        )

        if success:
            session["loggedin"] = True
            session["id"] = account.id
            session["username"] = account.username

        return redirect(url_for("auth.home"))

        return render_template("index.html", msg=msg)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    msg = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        success, msg = AuthService.register_user(
            username=username,
            password=password,
            email=email,
            secret_key=current_app.config["SECRET_KEY"],
        )

    return render_template("register.html", msg=msg)


@auth_bp.route("/home")
def home():
    if "loggedin" not in session:
        return redirect(url_for("auth.login"))

    return render_template("home.html", username=session["username"])


@auth_bp.route("/profile")
def profile():
    if "loggedin" not in session:
        return redirect(url_for("auth.login"))

    account = Account.query.get(session["id"])

    return render_template("profile.html", account=account)


@auth_bp.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)

    return redirect(url_for("auth.login"))
