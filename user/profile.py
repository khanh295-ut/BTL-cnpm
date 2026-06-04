import os
import uuid
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db, User
from user.permissions import admin_required
from user.roles import ROLES

user_bp = Blueprint("user", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_avatar(file_storage):
    if not allowed_file(file_storage.filename):
        return None
    filename = secure_filename(file_storage.filename)
    name = f"avatar_{uuid.uuid4().hex}_{filename}"
    upload_folder = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, name)
    file_storage.save(path)
    return f"/static/uploads/{name}"


def _user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "bio": user.bio,
        "avatar": user.avatar or "/static/images/avatar-placeholder.svg",
    }


@user_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")


@user_bp.route("/profile", methods=["GET"])
@login_required
def profile_page():
    return render_template("profile.html")


@user_bp.route("/api/profile", methods=["GET"])
@login_required
def profile_api():
    return jsonify({"user": _user_payload(current_user)}), 200


@user_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    data = request.get_json(silent=True) or request.form
    full_name = data.get("full_name")
    email = (data.get("email") or "").strip().lower()
    bio = data.get("bio")
    avatar_file = request.files.get("avatar")

    if email and email != current_user.email:
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email đã tồn tại."}), 409
        current_user.email = email

    if full_name is not None:
        current_user.full_name = full_name.strip()

    if bio is not None:
        current_user.bio = bio.strip()

    if avatar_file and avatar_file.filename:
        avatar_url = save_avatar(avatar_file)
        if not avatar_url:
            return jsonify({"error": "Định dạng file không hợp lệ. Chỉ nhận png, jpg, jpeg, gif."}), 400
        current_user.avatar = avatar_url

    db.session.commit()
    return jsonify({"message": "Cập nhật hồ sơ thành công.", "user": _user_payload(current_user)}), 200


@user_bp.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    data = request.get_json() or request.form
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not current_password or not new_password:
        return jsonify({"error": "Cần cung cấp mật khẩu hiện tại và mật khẩu mới."}), 400

    if not current_user.check_password(current_password):
        return jsonify({"error": "Sai mật khẩu hiện tại."}), 401

    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Đổi mật khẩu thành công."}), 200


@user_bp.route("/admin/users", methods=["GET"])
@admin_required
def list_users():
    users = User.query.order_by(User.id).all()
    return jsonify({"users": [_user_payload(user) for user in users]}), 200


@user_bp.route("/admin/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"user": _user_payload(user)}), 200


@user_bp.route("/admin/users/<int:user_id>/role", methods=["POST"])
@admin_required
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or request.form
    role = data.get("role", "").strip()

    if role not in ROLES:
        return jsonify({"error": "Vai trò không hợp lệ. Chỉ hỗ trợ Admin hoặc User."}), 400

    user.role = role
    db.session.commit()
    return jsonify({"message": "Cập nhật vai trò thành công.", "user": _user_payload(user)}), 200
