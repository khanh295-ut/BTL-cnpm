import secrets
from datetime import datetime

from flask import request, jsonify, render_template, redirect, url_for

from . import auth_bp
from models import db, User, PasswordResetToken


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")

    data = request.get_json(silent=True) or request.form
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Vui lòng nhập email."}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken.create_for_user(user, token)
        db.session.add(reset_token)
        db.session.commit()
        reset_url = url_for("auth.reset_password", token=token, _external=True)
    else:
        reset_url = None

    message = "Nếu email tồn tại trong hệ thống, đường dẫn reset mật khẩu đã được tạo."
    response = {"message": message}
    if reset_url:
        response["reset_url"] = reset_url
    return jsonify(response), 200


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    reset_item = PasswordResetToken.query.filter_by(token=token).first()
    if not reset_item or not reset_item.is_valid():
        return render_template("reset_password.html", invalid=True), 400

    if request.method == "GET":
        return render_template("reset_password.html", token=token, invalid=False)

    data = request.get_json(silent=True) or request.form
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    if not password or not confirm_password:
        return jsonify({"error": "Vui lòng nhập mật khẩu mới và xác nhận."}), 400

    if password != confirm_password:
        return jsonify({"error": "Mật khẩu xác nhận không khớp."}), 400

    user = reset_item.user
    user.set_password(password)
    db.session.delete(reset_item)
    db.session.commit()

    return jsonify({"message": "Đổi mật khẩu thành công. Bạn có thể đăng nhập lại."}), 200
