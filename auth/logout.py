from flask import jsonify
from flask_login import logout_user, login_required

from . import auth_bp


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Đã đăng xuất. Vui lòng truy cập lại trang đăng nhập."}), 200
