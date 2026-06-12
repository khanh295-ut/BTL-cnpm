from flask import Flask, jsonify, redirect, url_for, request
from flask_login import LoginManager
from config import Config
from models import db, bcrypt, User, Role, Permission
from auth_user_management import auth_bp
from user import user_bp

login_manager = LoginManager()


@login_manager.unauthorized_handler
def unauthorized():
    if request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]:
        return jsonify({"error": "Chưa đăng nhập."}), 401
    return redirect(url_for("auth.login"))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Bạn cần đăng nhập để truy cập trang này."

    @login_manager.user_loader
    def load_user(user_id):
        if user_id is None:
            return None
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    @app.errorhandler(403)
    def forbidden(error):
        if request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]:
            return jsonify({"error": "Không đủ quyền truy cập."}), 403
        return redirect(url_for("auth.login"))

    with app.app_context():
        db.create_all()
        create_sample_data()

    return app


def create_sample_data():
    admin_role = Role.query.filter_by(name="Admin").first()
    user_role = Role.query.filter_by(name="User").first()
    if admin_role is None:
        admin_role = Role(name="Admin", description="Administrator role")
        db.session.add(admin_role)
    if user_role is None:
        user_role = Role(name="User", description="Standard user role")
        db.session.add(user_role)

    manage_users_permission = Permission.query.filter_by(name="manage_users").first()
    reset_password_permission = Permission.query.filter_by(name="reset_password").first()
    if manage_users_permission is None:
        manage_users_permission = Permission(
            name="manage_users",
            description="Quản lý người dùng"
        )
        db.session.add(manage_users_permission)
    if reset_password_permission is None:
        reset_password_permission = Permission(
            name="reset_password",
            description="Reset mật khẩu"
        )
        db.session.add(reset_password_permission)

    db.session.commit()

    if manage_users_permission not in admin_role.permissions:
        admin_role.permissions.append(manage_users_permission)
    if reset_password_permission not in admin_role.permissions:
        admin_role.permissions.append(reset_password_permission)
    if reset_password_permission not in user_role.permissions:
        user_role.permissions.append(reset_password_permission)

    db.session.commit()

    if User.query.filter_by(username="admin").first() is not None:
        return

    admin = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin System",
        bio="Tài khoản Admin mẫu."
    )
    admin.set_password("Admin@123")
    db.session.add(admin)

    member = User(
        username="alice",
        email="alice@example.com",
        full_name="Alice Nguyen",
        bio="Người dùng mẫu."
    )
    member.set_password("User@123")
    db.session.add(member)

    db.session.flush()
    admin.roles.append(admin_role)
    member.roles.append(user_role)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)