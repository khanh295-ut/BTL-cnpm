from flask import request, jsonify, render_template, redirect, url_for

from . import auth_bp
from models import db, User


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "Username, email và password là bắt buộc."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username đã tồn tại."}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email đã tồn tại."}), 409

    user = User(username=username, email=email, role="User")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Đăng ký thành công. Vui lòng đăng nhập."}), 201
