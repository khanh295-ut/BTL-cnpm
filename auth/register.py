from flask import request, jsonify

from . import auth_bp
from models import db, User, Role


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or request.form
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "Username, email và password là bắt buộc."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username đã tồn tại."}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email đã tồn tại."}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)

    user_role = Role.query.filter_by(name="User").first()
    if user_role is None:
        user_role = Role(name="User", description="Standard user role")
        db.session.add(user_role)
        db.session.flush()

    user.roles.append(user_role)
    db.session.commit()

    return jsonify({"message": "Đăng ký thành công. Vui lòng đăng nhập."}), 201
