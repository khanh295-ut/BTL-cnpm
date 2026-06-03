from flask import jsonify, redirect, url_for, request
from flask_login import logout_user, login_required

from . import auth_bp


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "GET":
        return redirect(url_for("auth.login"))

    logout_user()
    return jsonify({"message": "Đã đăng xuất. Vui lòng truy cập lại trang đăng nhập."}), 200
