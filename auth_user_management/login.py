from flask import request, jsonify, render_template, redirect, url_for
from flask_login import login_user, current_user
from sqlalchemy import or_

from . import auth_bp
from models import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("user.dashboard"))
        return render_template("login.html")

    if current_user.is_authenticated:
        return jsonify({"message": "Bạn đã đăng nhập."}), 200

    data = request.get_json(silent=True) or request.form
    login_input = (data.get("login") or data.get("username") or data.get("email") or "").strip()
    password = data.get("password", "")

    if not login_input or not password:
        return jsonify({"error": "Vui lòng nhập username/email và mật khẩu."}), 400

    user = User.query.filter(or_(User.username == login_input, User.email == login_input)).first()
    if user is None:
        return jsonify({"error": "Tài khoản không tồn tại."}), 404

    if not user.check_password(password):
        return jsonify({"error": "Sai mật khẩu."}), 401

    login_user(user)
    return jsonify({
        "message": "Đăng nhập thành công.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "bio": user.bio,
        },
    })
